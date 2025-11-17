import json
import os
from celery import Celery
from vertex.src.api.services.vertexMLService import mlService
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CELERY_BROKER_URL = f'sqla+sqlite:///{os.path.join(BASE_DIR, "broker.sqlite")}'
CELERY_RESULT_BACKEND = f'db+sqlite:///{os.path.join(BASE_DIR, "broker.sqlite")}'

celery = Celery("app", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

algo = mlService()


@celery.task(name="detect_anomalies")
def detect_anomalies_task(params: dict):
    try:
        query = int(params["queryid"])
        detector = algo.detect_anomalies_task(query)
        return detector
    except Exception as e:
        return {"error": str(e)}


@celery.task(name="forecasting")
def forecasting_task(parameters: dict):
    try:
        query = int(parameters["queryid"])
        future_days = int(parameters["future_days"])
        detector = algo.forecasting_task(query, future_days)
        return detector
    except Exception as e:
        return {"error": str(e)}


def get_api_task_status(task_id):
    task_result = celery.AsyncResult(task_id)

    def pandas_serializer(obj):
        """Custom serializer for pandas/pydantic types"""
        if isinstance(obj, pd.Timestamp):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, np.generic):
            return np.asscalar(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    if task_result.state == "SUCCESS":
        safe_result = json.loads(
            json.dumps(task_result.result, default=pandas_serializer)
        )
        response = {
            "status": task_result.state,
            "result": safe_result,
            "task_id": task_id,
        }
    elif task_result.state == "FAILURE":
        response = json.loads(
            task_result.backend.get(
                task_result.backend.get_key_for_task(task_result.id)
            ).decode("utf-8")
        )
        del response["children"]
        del response["traceback"]
    else:
        response = {
            "status": task_result.state,
            "result": task_result.info,
            "task_id": task_id,
        }
    return response
