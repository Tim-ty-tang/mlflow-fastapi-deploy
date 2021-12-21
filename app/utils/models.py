import gzip
import pickle
import botocore.session
import os
import mlflow.pyfunc
import s3fs 

from ..log import logger
from ..params import Params
from .path_utils import get_prod_path_mlflow_model_explicit

import os
from awscli.clidriver import create_clidriver
from contextlib import redirect_stdout
import io


def load_object(source, model_path, cache, query_type="explicit"):
    assert source in ['s3', 'local', 'mlflow', None]
    assert query_type in ['explicit', 'mlflow_query', None]
    assert type(cache) is str or cache is False
    if source is None:
        model = None
    elif source == "s3":
        if cache:
            download_s3_model(model_path, cache)
            model = load_from_local(cache)
        else:
            model = load_model_from_s3(model_path)
    elif source == "mlflow":
        if cache:
            pass
            # cache the model from s3 to local
        if Params.MODEL_LOAD_FROM_PROD_BUCKET:
            logger.info(f"Load from prod bucket")
            model_path_components = model_path.split('/')
            model_name, version = model_path_components[1], model_path_components[2]
            logger.info(f"from model: {model_path_components}")
            get_prod_path = Params.PROD_PATH_MAP.get(query_type, get_prod_path_mlflow_model_explicit)
            mlflow_path_dict = get_prod_path(model_name, version, 
                                             new_bucket=Params.MODEL_PROD_DEST_BUCKET, 
                                             new_path=Params.MODEL_PROD_DEST_PATH)
            
            artifact_path_original = mlflow_path_dict["old_mlflow_path"]
            prod_path = mlflow_path_dict["new_mflow_path"]
            logger.info(f"from artifact_path_original: {artifact_path_original}")
            logger.info(f"from s3 path: {prod_path}")

            f = io.StringIO()
            driver = create_clidriver()
            with redirect_stdout(f):
                driver.main(f's3 ls {prod_path} --recursive'.split())
            response = f.getvalue().strip().split()
            logger.info(f"from ls response: {response}")

            if response:
                model = mlflow.pyfunc.load_model(model_uri=prod_path)
            else:
                raise Exception(f"Load model failed for prod path {prod_path}, response from s3 ls {response}")
        else:
            logger.info(f"load from play")
            model = mlflow.pyfunc.load_model(
                model_uri=model_path
                )
    elif source == "local":
        model = load_from_local(model_path)
    else:
        # TODO define an exception here
        raise Exception
    return model

def load_from_local(local_path):
    logger.info(f'loading local model {local_path}')
    return unpickle(local_path)

def download_s3_model(s3_path, cache_file_path):
    s3_session = botocore.session.get_session()
    # TODO boto3 equivalent
    # fs = s3fs.S3FileSystem(session=s3_session)   
    # logger.info(f'saving remote model {s3_path} at  {cache_file_path}')
    # with fs.open(s3_path) as model_file:
    #     f = open(cache_file_path, 'wb')
    #     f.write(model_file.read())


class CustomUnpickler(pickle.Unpickler):
    # TODO: On the unpickler, I think we can install the custom 
    # classes module instead of unpickling it this way...
    def find_class(self, module, name):
        return super().find_class(module, name)


def unpickle(file_path):
    """
    Load pickled python object from file path
    """
    if file_path.endswith('.gz'):
        f = gzip.open(file_path, 'rb')
    else:
        f = open(file_path, 'rb')
    unpickled = CustomUnpickler(f).load()
    return unpickled


def load_model_from_s3(s3_path):
    fs = s3fs.S3FileSystem()   
    logger.info(f'loading s3 model {s3_path}')
    with fs.open(s3_path) as model_file:
        if s3_path.endswith('.gz'):
            model_file = gzip.GzipFile(fileobj=model_file)
        my_pickle = CustomUnpickler(model_file).load()
        return my_pickle

