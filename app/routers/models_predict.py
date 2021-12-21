from fastapi import APIRouter, Query, HTTPException
import json
import numpy as np
import pandas as pd
from typing import List
import functools
from txmlcommonlibrary.utilities.jsonencoder import NumpyEncoder
from fastapi.encoders import jsonable_encoder


from ..params import models_dict, configs, Params
from ..log import logger

router = APIRouter()

def call_function(model_name, obj, data, call_name, call_params):
    
    assert call_name in ["transform", "predict", "predict_proba", 
                         "mean", "predict_alert", "predict_trip", 
                         "column_list"]

    # assert call_params
    if call_name == "predict" or call_name == "predict_proba":
        return predict_with_features(model_name, data, obj, call_name, **call_params)
    elif call_name == "mean":
        return np.mean(data)
    elif call_name == "column_list":
        return obj.column_list


def predict_with_features(model_name, features, model, predict_call, call_params=None, **other_params):
    """
    given a dict of features turn it into a df and use it to predict. 
    This assumes the column order is already correct from the scaling.
    This method is relevant in most traditional techniques, 
    using a flat featrue based input.
    """
    try:
        df = pd.DataFrame(features)
    except ValueError:
        df = pd.DataFrame(features, index=[0])
    df = df.apply(functools.partial(pd.to_numeric, errors='coerce'))

    # Checks columns match
    # emergency cleaning
    data = df
    
    if call_params:
        assert isinstance(call_params, dict)
        _call_params = call_params
    else:
        _call_params = {}

    if predict_call == "predict":
        results = model.predict(data, **_call_params)
    elif predict_call == "predict_proba":
        results = model.predict_proba(data, **_call_params).flatten()
    else:
        raise Exception("Model is to be called with predict ot predict_proba")
    
    if type(results) == dict:
        results = json.loads(json.dumps(results, cls=NumpyEncoder))
        results['model_name'] = configs.get('MODELS', {}).get(model_name, {}).get('INFO', {}).get('MODEL_NAME')
        results['version'] = configs.get('MODELS', {}).get(model_name, {}).get('INFO', {}).get('VERSION')
        return results
    else:    
        res = {}
        res['model_name'] = configs.get('MODELS', {}).get(model_name, {}).get('INFO', {}).get('MODEL_NAME')
        res['version'] = configs.get('MODELS', {}).get(model_name, {}).get('INFO', {}).get('VERSION')
        if isinstance(results, list):
            res['data'] = results
            return res
        elif isinstance(results, np.ndarray):
            res['data'] = results.tolist()
            return res
        else:
            raise ValueError("Unexpected result type. Model results must be dict, list or numpy arrays")


@router.post("/model/{model_name}/{method}")
async def predict_single(model_name: str,
                         method: str,
                         data: dict):
    """  
    For a model name, return the prediction given the data. 
    The method can be found using an endpoint or prior user knowledge.
    """
    obj = models_dict.get(model_name, None)
    calls = configs.get("MODELS", {}).get(model_name, {}).get("CALLS", {}).get("CALL_PARAMS", {})
    logger.info(f"{obj}")
    # TODO All excpetions here ar e500 internals
    if method in calls.keys():
        logger.info(f"{calls}")
        call_params = calls[method]
    else:
        raise HTTPException(status_code=501, detail=f"{method} not a registered call")
    if obj:
        try:
            results = call_function(model_name, obj, data, method, call_params)
            if results is None:
                raise HTTPException(status_code=501, detail=f"null results")
            return results
        except Exception as err:
            logger.exception(f"{err}")
            raise HTTPException(status_code=500, detail=f"{err}")
    else:
        raise HTTPException(status_code=501, detail=f"Obj is Null")


# @router.post("/model/{model_name}/{method}/object")
# async def predict_single_from_object(model_name: str,
#                                      method: str,
#                                      object: str):
#     pass


# @router.post("/model/{model_name}/{method}/{id}")
# async def predict_single_from_id(model_name: str,
#                                  method: str,
#                                  id: str):
#     pass
