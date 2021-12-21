from typing import Optional
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os
import pytz
import mlflow

# other schedulers are available, depends on gdba-config service
from .params import models_dict, configs, Params
from .utils.utils import service_setup
from .routers import models_predict, models_utils
from .utils.prometheus_utils import PrometheusMiddleware, metrics
import warnings
from starlette.responses import RedirectResponse

warnings.filterwarnings('ignore')

app = FastAPI()

@app.on_event('startup')
async def startup_event():
    # service setup 
    mlflow.set_tracking_uri(Params.MLFLOW_URI)
    service_setup(Params.CONF_NAME, fp=Params.CONF_LOCAL_PATH)

    # Schedulers
    scheduler = AsyncIOScheduler(timezone=pytz.utc)
    scheduler.start()
    
    # Sync Model Config everyday?
    # scheduler.add_job(query_and_sync_relations,
    #                   args=[gdbaApiParams],
    #                   trigger="interval",
    #                   minutes=int(os.getenv("GDBA_RELATION_SYNC", 15)))  # runs every 15 min


@app.get("/")
def read_root():
    return RedirectResponse('/docs')


@app.get("/healthcheck")
async def health_check():
    return True


@app.get("/config")
async def config_return():
    return configs


@app.get("/reset_config")
async def reset_current_config(config_name: Optional[str] = None, fp: Optional[str] = None):
    if config_name:
        os.environ["CONF_NAME"] = config_name
    service_setup(Params.CONF_NAME, fp)


@app.get("/model_names")
async def model_names():
    return list(models_dict.keys())


@app.get("/params")
async def poll_params():
    return configs

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(models_predict.router, tags=["Model Predict"])
app.include_router(models_utils.router, tags=["Model utils"])
