import os, sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_obs():
    dsn = os.getenv("SENTRY_DSN_API")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=1.0,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            environment=os.getenv("ENV","dev"),
            release=os.getenv("RELEASE","local"),
        )
