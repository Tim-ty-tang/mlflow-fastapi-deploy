import json
from fastapi import APIRouter, Query, HTTPException

from ..params import models_dict, configs, Params
from ..log import logger

router = APIRouter()

@router.get("/models")
async def get_models():
    """  
    Get model names
    """
    return list(models_dict.keys())

@router.get("/pipelines")
async def get_models():
    """  
    Get model names
    """
    return list(configs.get("PIPELINES").keys())

@router.get("/models/{model_names}")
async def get_models_methods(model_names: str):
    """  
    Get calls given model name
    """
    return configs.get("MODELS").get(model_names).get("CALLS")


@router.get("/configs")
async def get_models_configs():
    """  
    Get Full config
    """
    return configs


@router.get("/example/{model_name}/{method}")
async def get_model_call_example(model_name: str,
                                       method: str):
    """  
    Get model example from wrapped data
    """
    calls = configs.get("MODELS", {}).get(model_name, {}).get("CALLS", {}).get("CALL_PARAMS", {})
    if method in calls.keys():
        logger.info(f"{calls}")
        call_params = calls[method]
    else:
        raise HTTPException(status_code=501, detail=f"{method} not a registered call")
    if "example_input" in call_params.keys():  
        try:
            return json.load(open(call_params["example_input"]))
        except Exception as err:
            raise HTTPException(status_code=501, detail=f"Loading exmaple resulted in error: {err}")
    else:
        raise HTTPException(status_code=501, detail=f"example input path not provided")


@router.get("/example_input/{model_name}")
async def get_model_call_example_model_name(model_name: str):
    """  
    Get model input example data
    """
    input = configs.get("MODELS", {}).get(model_name, {}).get("INPUT", {})
    if "example_input" in input.keys():  
        try:
            return json.load(open(input["example_input"]))
        except Exception as err:
            raise HTTPException(status_code=501, detail=f"Loading exmaple resulted in error: {err}")
    else:
        raise HTTPException(status_code=501, detail=f"example input path not provided")

@router.get("/example_output/{model_name}")
async def get_model_call_example_result_model_name(model_name: str):
    """  
    Get model output example data
    """
    output = configs.get("MODELS", {}).get(model_name, {}).get("OUTPUT", {})
    if "example_output" in output.keys():  
        try:
            return json.load(open(output["example_output"]))
        except Exception as err:
            raise HTTPException(status_code=501, detail=f"Loading exmaple resulted in error: {err}")
    else:
        raise HTTPException(status_code=501, detail=f"example output path not provided")

@router.get("/example/{pipeline_name}")
async def get_model_call_example(pipeline_name: str):
    """  
    Get model input example data from pipeline
    """
    input = configs.get("PIPELINES", {}).get(pipeline_name, {}).get("INPUT", {})
    if "example_input" in input.keys():  
        try:
            return json.load(open(input["example_input"]))
        except Exception as err:
            raise HTTPException(status_code=501, detail=f"Loading exmaple resulted in error: {err}")
    else:
        raise HTTPException(status_code=501, detail=f"example input path not provided")