import os
from pathlib import Path
from dataclasses import dataclass
from distutils.util import strtobool

from .utils.path_utils import (
    get_prod_path_mlflow_model_explicit,
    get_prod_path_mlflow_model_mlflow_query,
)

# Dictionary object for holding all model objects
models_dict = {}

# Configurations dict, this will become the config json after startup
configs = {}


class Params:
    # Get the whether we want replication. This only applies to MLFlow
    # MODEL_REPLICATE is boolean deciding we should either be directly from mlflow
    # or copy from MLFlow s3 path to a controlled bucket and loaded from there.
    MODEL_LOAD_FROM_PROD_BUCKET = strtobool(os.getenv("MODEL_LOAD_FROM_PROD_BUCKET", "True"))
    MODEL_PROD_DEST_BUCKET = os.getenv("MODEL_REPLICATE_DEST_BUCKET", "tx-ml-data")
    MODEL_PROD_DEST_PATH = os.getenv("MODEL_REPLICATE_DEST_PATH", "models")

    # Config service location
    # Stack info. This allows the right config to be grabbed
    MODEL_STACK = os.getenv("MODEL_STACK", "")
    MODEL_TYPE = os.getenv("MODEL_TYPE", "")
    MODEL_VER = os.getenv("MODEL_VER", "")

    # Config service location and conf name/location
    CONF_NAME = os.getenv("CONF_NAME", "local")
    CONF_LOCAL_PATH = os.getenv("CONF_LOCAL_PATH", "app/configs/example_deploy.yaml")

    # AWS keys
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


    # MLFLOW repo
    MLFLOW_URI = os.getenv("MLFLOW_URI", "https://mlflow.play.itbts.net/")

    # infos
    PREDICTION_TYPE = os.getenv("PREDICTION_TYPE", "")
    MODELS_VERSION = os.getenv("MODELS_VERSION", "1")

    # Cache path
    if os.environ.get("MODEL_FOLDER_PATH"):
        MODEL_FOLDER_PATH = Path(os.environ.get("MODEL_FOLDER_PATH") + f"/{PREDICTION_TYPE}/{MODELS_VERSION}")
    else:
        MODEL_FOLDER_PATH = None

    PROD_PATH_MAP = {
        "explicit": get_prod_path_mlflow_model_explicit,
        "mlflow_query": get_prod_path_mlflow_model_mlflow_query,
    }

    CONFIG_MAP = {
    }
