# core.py
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import timedelta
from database.sqlconnector import SqlConnector

sql = SqlConnector()

class Forecasting:
    def __init__(self, query : str, future_days : None = 30):
        self.df = self.load_and_prepare_data(query)
        self.forecast_days = future_days

    def load_and_prepare_data(self,query,parameters):
        try:
            df = sql.execute_Sql(query,parameters)
            if "date" not in df.columns or "value" not in df.columns:
                print("Missing Date or Value column!")
                return None
            elif not pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna().all():
                print("Date format is incorrect!, It should be in YYYY-MM-DD HH:MM:SS format")
                return None
            df["date"] = pd.to_datetime(df["date"])
            df = df.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
            df = df.set_index("date").asfreq("D").reset_index()
            # print(df.head(5))
            return df
        except Exception as e:
            print(f"Error loading data from SQL: {e}")
            return None

    def feature_engineering(self,df):
        for lag in [1, 2, 3, 7]:
            df[f"lag_{lag}"] = df["value"].shift(lag)
        df["rolling_mean_7"] = df["value"].rolling(window=7).mean()
        df["rolling_std_7"] = df["value"].rolling(window=7).std()
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["day_of_year"] = df["date"].dt.dayofyear
        df.dropna(inplace=True)
        return df

    def train_model(self,X, y):
        model = xgb.XGBRegressor(
            objective="reg:squarederror",
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X, y)
        return model

    def forecast_future(self,model, last_known_values, base_date, future_days, feature_cols):
        forecast_dates = [base_date + timedelta(days=i) for i in range(1, future_days + 1)]
        forecasts = []
        history = last_known_values.copy()

        for i in range(future_days):
            features = {
                "lag_1": history[-1],
                "lag_2": history[-2],
                "lag_3": history[-3],
                "lag_7": history[-7] if len(history) >= 7 else np.mean(history),
                "rolling_mean_7": np.mean(history[-7:]),
                "rolling_std_7": np.std(history[-7:]),
                "day_of_week": forecast_dates[i].weekday(),
                "month": forecast_dates[i].month,
                "day_of_year": forecast_dates[i].timetuple().tm_yday
            }
            features_df = pd.DataFrame([features])[feature_cols]
            pred = model.predict(features_df)[0]
            forecasts.append(pred)
            history.append(pred)

        return pd.DataFrame({
            "date": [d.strftime("%Y-%m-%d") for d in forecast_dates],
            "forecast": forecasts
        })

    def  get_forecast(self):
        df = self.load_and_prepare_data()
        if df is None or df.shape[0] < 10:
            return None
        
        df = self.feature_engineering(df)
        feature_cols = [col for col in df.columns if col not in ["date", "value"]]
        X, y = df[feature_cols], df["value"]
        model = self.train_model(X, y)

        last_values = df["value"].values[-7:].tolist()
        base_date = df["date"].max()
        future_df = self.forecast_future(model, last_values, base_date, self.forecast_days, feature_cols)

        return {
            "historical": df[["date", "value"]].to_dict(orient="records"),
            "forecast": future_df.to_dict(orient="records")
        }

# if __name__ == "__main__":
#     query = """ """
#     forecast = Forecasting(query)
    
#     response = forecast.get_forecast()
#     print(response)