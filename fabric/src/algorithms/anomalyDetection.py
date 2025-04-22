import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from database.sqlService import SqlConnector

sql = SqlConnector()


class AnomalyDetection:
    def __init__(self, query,parameters):
        self.df = self.load_and_prepare_data(query,parameters)

    def load_and_prepare_data(query,parameters):
        try:
            df = sql.execute_Sql(query, parameters)
            if "date" not in df.columns or "value" not in df.columns:
                print("Missing Date or Value column!")
                return None
            elif not pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna().all():
                print("Date format is incorrect!, It should be in YYYY-MM-DD HH:MM:SS format")
                return None
            df = pd.DataFrame(df, columns=["date", "value"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
            return df
        except Exception as e:
            print("Error loading data from SQL:", e)
            return pd.DataFrame()

    def feature_engineering(df):
        df["rolling_mean"] = df["value"].rolling(window=5).mean()
        df["rolling_std"] = df["value"].rolling(window=5).std()
        df.dropna(inplace=True)
        return df

    def train_and_detect(df):
        train_size = int(len(df) * 0.8)
        train, test = df.iloc[:train_size], df.iloc[train_size:]

        features = [col for col in df.columns if col not in ["date", "value"]]
        X_train, y_train = train[features], train["value"]
        X_test, y_test = test[features], test["value"]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        errors = np.abs(y_test - y_pred)
        threshold = np.percentile(errors, 95)
        return test[errors > threshold]
