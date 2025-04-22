import asyncio
from threading import Lock
import socketio
from algorithms.anomalyDetection import AnomalyDetection
from algorithms.forecasting import Forecasting


# Global task management
active_tasks = {}
task_lock = Lock()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

async def emit_status(guid, status, result=None, error=None):
    await sio.emit('status_update', {
        'guid': guid,
        'status': status,
        'result': result,
        'error': error
    })


def run_anomaly_task(guid: str, query: str, parameters: dict = None):
    try:
        with task_lock:
            active_tasks[guid]['status'] = 'loading_data'
        
        # Async status update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(emit_status(guid, 'loading_data'))

        ad = AnomalyDetection(query, parameters)
        if ad.df.empty:
            raise ValueError("Data loading failed")

        with task_lock:
            if active_tasks[guid]['stop_flag']:
                loop.run_until_complete(emit_status(guid, 'stopped'))
                return

        ad.df = AnomalyDetection.feature_engineering(ad.df)
        
        with task_lock:
            if active_tasks[guid]['stop_flag']:
                loop.run_until_complete(emit_status(guid, 'stopped'))
                return

        anomalies = AnomalyDetection.train_and_detect(ad.df)
        
        with task_lock:
            active_tasks[guid]['result'] = anomalies.to_dict()
            active_tasks[guid]['status'] = 'completed'
            loop.run_until_complete(emit_status(guid, 'completed', anomalies.to_dict()))

    except Exception as e:
        with task_lock:
            active_tasks[guid]['status'] = 'failed'
            active_tasks[guid]['error'] = str(e)
            loop.run_until_complete(emit_status(guid, 'failed', error=str(e)))


def run_forecast_task(guid: str, query: str, parameters: dict, future_days: int):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        with task_lock:
            active_tasks[guid]['status'] = 'loading_data'
        loop.run_until_complete(emit_status(guid, 'loading_data'))

        forecast = Forecasting(query, parameters, future_days)
        
        with task_lock:
            if active_tasks[guid]['stop_flag']:
                loop.run_until_complete(emit_status(guid, 'stopped'))
                return

        with task_lock:
            active_tasks[guid]['status'] = 'processing'
        loop.run_until_complete(emit_status(guid, 'processing'))

        result = forecast.get_forecast()
        
        with task_lock:
            active_tasks[guid]['result'] = result
            active_tasks[guid]['status'] = 'completed'
        loop.run_until_complete(emit_status(guid, 'completed', result))

    except Exception as e:
        with task_lock:
            active_tasks[guid]['status'] = 'failed'
            active_tasks[guid]['error'] = str(e)
        loop.run_until_complete(emit_status(guid, 'failed', error=str(e)))