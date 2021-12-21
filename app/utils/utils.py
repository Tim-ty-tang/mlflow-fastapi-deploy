import json
import numpy as np
import requests
import yaml

from ..log import logger
from ..params import models_dict, configs, Params
from .models import load_object

# This convert function is needed to serialize numpy data
def convert(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


def confname_to_config_query(url, config_name):
    response = requests.get(url=url + f'/conf/get/{config_name}')
    if response.status_code == 200:
        r = json.loads(response.content)
        return r
    else:
        return {}


# This sets up the service based on the config name needed. 
def query_for_configuration(query_url, config_name, fp = None):
    logger.info(f"Configs to be loaded -> {config_name}")
    if config_name == "local":
        if fp:
            with open(fp) as f:
                if fp.endswith(".json"):
                    r = {"config": json.load(f)}
                elif fp.endswith(".yaml"):
                    r = {"config": yaml.safe_load(f)}
        else:
            raise Exception("No config Local")
    else:
        r = confname_to_config_query(url=query_url,
                                    config_name=config_name)
    return r.get('config', {})
 

# Load config then load objects
def service_setup(config_name, fp = None):
    # Load params from config service
    configs.update(query_for_configuration(Params.CONF_URL, config_name, fp))
    
    # Given the startup params load the models and so on
    if configs.get("MODELS"):
        logger.info(f"Config for {config_name} loaded")
        fails = {}
        for m, v in configs.get("MODELS").items():
            path_conf = v['PICKLES']
            logger.info(f"Loading models {path_conf}")
            try:
                models_dict[m] = load_object(path_conf['OBJECT_SOURCE'], path_conf['OBJECT_PATH'], path_conf['CACHE'])
            except Exception as err:
                logger.info(f"logger. log {err}")
                raise err
                fails[m] = err
        logger.info(f"failed to load {fails}")
    else:
        # TODO define config Excpetion
        raise Exception
    
