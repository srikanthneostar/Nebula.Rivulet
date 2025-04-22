from fastapi import APIRouter
from fastapi_socketio import SocketManager
from fabric.build.lib.algorithms.anomalyDetection import AnomalyDetection
from fabric.build.lib.algorithms.forecasting import Forecasting
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

router = APIRouter()
sio = SocketManager()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sio = SocketManager(app=app)


@router.get("/forecast/streaming/start")
async def get_forecast(req: dict):
    # Create an instance of Forecasting class and get the forecast
    forecast = Forecasting(req["query"], req["future_days"])
    result = forecast.get_forecast()
    # Emit data to connected frontend clients via SocketIO
    await sio.emit("forecast_update", result)
    return {"status": "success", "data": result}


@router.get("/anomaly/streaming")
async def get_anomaly(req: dict): 
    query = req["query"]
    anomaly = AnomalyDetection(query)
    await sio.emit("anomaly_update", anomaly)
    return {"status": "success", "data": anomaly}