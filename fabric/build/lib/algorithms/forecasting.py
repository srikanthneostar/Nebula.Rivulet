# core.py
import json
import math
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import timedelta
from database.sqlService import SqlConnector
from messaging.NebulaRequestProducer import NebulaRequestProducer

sql = SqlConnector()

class Forecasting:
    def __init__(self, queryid: int, future_days=30):
        self.queryid = queryid
        self.forecast_days = future_days
        self.producer = NebulaRequestProducer()

    def get_application_query(self):
        """Get query text safely using parameterized SQL"""
        try:
            qry = "SELECT QUERY FROM APPLICATIONQUERIES WHERE ID = ?"  # Parameter placeholder
            results = sql.execute_Sql(qry, (self.queryid,))  # Pass as tuple
            
            if results.empty:  # Replace "if not results"
                raise ValueError(f"No query found with ID {self.queryid}")
                
            # Handle different result types
            if isinstance(results, pd.DataFrame):
                return results.iloc[0]['QUERY']
            elif isinstance(results, list) and len(results) > 0:
                return results[0]['QUERY']
            else:
                raise ValueError("Unexpected result format from database")
                
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise

    def load_and_prepare_data(self, query):
        """Load data with enhanced validation"""
        try:
            df = sql.execute_Sql(query)
            
            # Check for empty results
            if df is None:
                return None
            if len(df) < 10:  # Now safe to check length
                print("Insufficient data rows")
                return None
                            
            # Validate required columns
            required_cols = {"date", "value"}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                print(f"Missing columns: {missing}")
                return None
                
            # Validate date format
            df["date"] = pd.to_datetime(df["date"], errors='coerce')
            if df["date"].isnull().any():
                print("Invalid date format (YYYY-MM-DD required)")
                return None
                
            # Process data
            df = (
                df.drop_duplicates("date")
                .sort_values("date")
                .set_index("date")
                .asfreq("D")
                .reset_index()
            )
            
            return df.dropna(subset=["value"])
            
        except Exception as e:
            print(f"Data loading error: {str(e)}")
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

    def get_forecast(self):
        """Main forecasting process with validation"""
        try:
            query = self.get_application_query()
            df = self.load_and_prepare_data(query)
            
            if df is None:
                return {"error": "Data loading failed"}
            if len(df) < 10:
                return {"error": "Need at least 10 days of historical data"}
                
            # Feature engineering and modeling
            df = self.feature_engineering(df)
            feature_cols = [col for col in df.columns if col not in ["date", "value"]]
            
            model = self.train_model(df[feature_cols], df["value"])
            last_values = df["value"].tail(7).tolist()
            base_date = df["date"].max()
            
            forecast = self.forecast_future(
                model, last_values, base_date, self.forecast_days, feature_cols
            )

            # res = {
            #     "historical": df[["date", "value"]].assign(date=lambda x: x["date"].dt.strftime('%Y-%m-%d'))
            #     .to_dict(orient="records"),
            #     "forecast": forecast.to_dict(orient="records")
            # }

            response_json = {
            "category": "week",
            "predictions": [
                {
                    "predictedDate": row["date"],
                    "predictedValue": math.ceil(row["forecast"])
                }
                for row in forecast.to_dict(orient="records")
            ]
        }
            return response_json
            # # print("RESPONSE----->",response_json)
            # reqPayLoad = self.producer.get_request_payload(
            #     'TimeseriesForecasting', json.dumps(response_json))
            # self.producer.get_producer().sendMessage(
            #     'nebula.timeseries.forecasting', reqPayLoad)
        
        except Exception as e:
            return {"error": str(e)}
        
        finally:
            if response_json != None:
                reqPayLoad = self.producer.get_request_payload(
                    'TimeseriesForecasting', json.dumps(response_json))
                self.producer.get_producer().sendMessage(
                    'nebula.timeseries.forecasting', reqPayLoad)
            else:
                print("Error in forecasting")