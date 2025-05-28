import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from database.sqlService import SqlConnector
import argparse
sql = SqlConnector()


class AnomalyDetection:
    def __init__(self, queryid: int):
        self.queryid = queryid
        qry = self.get_application_query()
        self.df = self.load_and_prepare_data(qry)

    def get_application_query(self):
        """Get query text safely using parameterized SQL"""
        try:
            qry = "SELECT QUERY FROM APPLICATIONQUERIES WHERE ID = ?"
            results = sql.execute_Sql(qry, (self.queryid,)) # type: ignore
            
            if results.empty:  # Replace "if not results"
                raise ValueError(f"No query found with ID {self.queryid}")
            
            if isinstance(results, pd.DataFrame):
                return results.iloc[0]['QUERY']
            elif isinstance(results, list) and len(results) > 0:
                return results[0]['QUERY']
            else:
                raise ValueError("Unexpected result format from database")
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise 

    def load_and_prepare_data(self,query):
        try:
            df = sql.execute_Sql(query)
            if "date" not in df.columns or "value" not in df.columns:
                print("Missing Date or Value column!")
                return None
            elif not pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce').notna().all():
                print(df["date"])
                print("Date format is incorrect!, It should be in YYYY-MM-DD format")
                return None
            df = pd.DataFrame(df, columns=["date", "value"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
            return df
        except Exception as e:
            print("Error loading data from SQL:", e)
            return pd.DataFrame()


    def feature_engineering(self,df):
        df["rolling_mean"] = df["value"].rolling(window=5).mean()
        df["rolling_std"] = df["value"].rolling(window=5).std()
        df.dropna(inplace=True)
        return df


    def train_and_detect(self,df) -> dict:
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
        anomalies = test[errors > threshold]
        # print(f"Detected {len(anomalies)} anomalies out of {len(test)} test points.")
        return {
            "anomalies":anomalies}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anomaly Detection using Random Forest")
    parser.add_argument("--queryid", type=int, required=True, help="Query ID to fetch data")
    args = parser.parse_args()
    anomaly_detector = AnomalyDetection(args.queryid)
    df = anomaly_detector.df
    if df is not None and not df.empty:
        df = anomaly_detector.feature_engineering(df)
        results = anomaly_detector.train_and_detect(df)
    else:
        print("No valid data available for anomaly detection.")