
import json
import os
from celery import Celery
from algorithms.anomalyDetection import AnomalyDetection
from algorithms.forecasting import Forecasting
import pandas as pd




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CELERY_BROKER_URL = f'sqla+sqlite:///{os.path.join(BASE_DIR, "broker.sqlite")}'
CELERY_RESULT_BACKEND = f'db+sqlite:///{os.path.join(BASE_DIR, "broker.sqlite")}'

celery = Celery('app', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# celery = Celery('anomaly_tasks',
#                 broker='db+sqlite:///broker.sqlite',
#                 backend='db+sqlite:///broker.sqlite')

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)


@celery.task(name='detect_anomalies')
def detect_anomalies_task(query: str, params: dict):
    try:
        detector = AnomalyDetection(query, params)
        
        if detector.df is None or detector.df.empty:
            return {"error": "Dataframe is invalid or empty."}
        df_feat = detector.feature_engineering(detector.df)
        anomalies = detector.train_and_detect(df_feat)
        return anomalies.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}


@celery.task(name='forecasting')
def forecasting_task(parameters: dict):
    try:
        query = int(parameters["queryid"])
        future_days = int(parameters["future_days"])
        print(query,future_days,parameters)
        #
        detector = Forecasting(query, future_days)
        # if detector.df is None or detector.df.empty:
        #     return {"error": "Dataframe is invalid or empty."}
        return detector.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

def get_api_task_status(task_id):
    task_result = celery.AsyncResult(task_id)
    if task_result.state == 'SUCCESS':
        result = task_result.result
        if isinstance(result, list):
            for item in result:
                for key, value in item.items():
                    if 'timestamp' in key.lower() or isinstance(value, pd.Timestamp):
                        item[key] = str(value)
        response = {
            'status': task_result.state,
            'result': result,
            'task_id': task_id
        }
    elif task_result.state == 'FAILURE':
        response = json.loads(task_result.backend.get(task_result.backend.get_key_for_task(task_result.id)).decode('utf-8'))
        del response['children']
        del response['traceback']
    else:
        response = {
            'status': task_result.state,
            'result': task_result.info,
            'task_id': task_id
        }
    return response