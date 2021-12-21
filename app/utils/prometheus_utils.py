import time
import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector

REQUESTS = Counter(
    "starlette_requests_total",
    "Total count of requests by method and path.",
    ["method", "path_template"]
)

RESPONSES = Counter(
    "starlette_responses_total",
    "Total count of responses by method, path and status codes.",
    ["method", "path_template", "status_code"],
)

REQUESTS_PROCESSING_TIME = Histogram(
    "starlette_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path_template"],
)

EXCEPTIONS = Counter(
    "starlette_exceptions_total",
    "Histogram of exceptions raised by path and exception type",
    ["method", "path_template", "exception_type"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "starlette_requests_in_progress",
    "Gauge of requests by method and path currently being processed",
    ["method", "path_template"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path_template = self.get_path_template(request)

        REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).inc()
        REQUESTS.labels(method=method, path_template=path_template).inc()
        try:
            before_time = time.time()
            response = await call_next(request)
            after_time = time.time()
        except Exception as e:
            EXCEPTIONS.labels(method=method, path_template=path_template, exception_type=type(e).__name__).inc()
            raise e from None
        else:
            REQUESTS_PROCESSING_TIME.labels(method=method, path_template=path_template).observe(
                after_time - before_time
            )
            RESPONSES.labels(method=method, path_template=path_template, status_code=response.status_code).inc()
        finally:
            REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).dec()

        return response

    @staticmethod
    def get_path_template(request: Request) -> str:
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path
        return request.url.path


def metrics(request: Request) -> Response:
    if "prometheus_multiproc_dir" in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

