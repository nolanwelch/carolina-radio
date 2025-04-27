from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.gzip import GZipMiddleware

from .env import getenv

from .api import authentication, queue

QUEUE_SIZE = getenv("QUEUE_SIZE")

# comment to trigger rebuild
# another one


last_start_time = datetime.now()


description = """
Welcome to the Carolina Radio RESTful Application Programming Interface.
"""

feature_apis = [authentication, queue]

# Metadata to improve the usefulness of OpenAPI Docs /docs API Explorer
app = FastAPI(
    title="Carolina Radio API",
    version="0.1.0",
    description=description,
    openapi_tags=[
        authentication.openapi_tags,
        queue.openapi_tags,
    ],
)

# Use GZip middleware for compressing HTML responses over the network
app.add_middleware(GZipMiddleware)


origins = [
    "https://carolinaradio.tech",
    "https://radio.fossinating.com",
    "http://localhost:3000",
]

for feature_api in feature_apis:
    app.include_router(feature_api.api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
