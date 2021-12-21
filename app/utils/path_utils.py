from mlflow.tracking import MlflowClient
from urllib.parse import urlparse


def get_prod_path_mlflow_model_mlflow_query(model_name, version, new_bucket, new_path):
    client = MlflowClient()
    artifact_path_original = None
    for mv in client.search_model_versions(f"name='{model_name}'"):
        if mv.version ==  str(version):
            artifact_path_original = mv.source
    new_mflow_path = None
    if artifact_path_original:
        if new_bucket and new_path:
            o = urlparse(artifact_path_original, allow_fragments=False)
            new_mflow_path = f"s3://{new_bucket.strip('/')}/{new_path.strip('/')}/{o.path.strip('/')}"        
    
    return {"old_mlflow_path": artifact_path_original,
            "new_mflow_path": new_mflow_path}


def get_prod_path_mlflow_model_explicit(model_name, version, new_bucket, new_path):
    new_mflow_path = f"s3://{new_bucket.strip('/')}/{new_path.strip('/')}/{model_name}/{version}"
    return {"old_mlflow_path": None,
            "new_mflow_path": new_mflow_path}


