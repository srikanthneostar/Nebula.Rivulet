from algorithms.anomalyDetection import AnomalyDetection
from algorithms.forecasting import Forecasting


class mlService():
    def __init__(self):
        pass

    def detect_anomalies_task(self, query: int):
        try:
            detector = AnomalyDetection(query)
            df_feat = detector.feature_engineering(detector.df)
            result = detector.train_and_detect(df_feat)
            return result
        except Exception as e:
            return {"error": str(e)}

    def forecasting_task(self, query: int, future_days: int):
        try:
            detector = Forecasting(query, future_days)
            return detector.get_forecast()
        except Exception as e:
            return {"error": str(e)}