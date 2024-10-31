import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import os

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

app = FastAPI()

app.add_middleware(SentryAsgiMiddleware)
