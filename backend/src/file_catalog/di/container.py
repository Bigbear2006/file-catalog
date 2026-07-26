from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider

from file_catalog.di.providers.database import DatabaseProvider
from file_catalog.di.providers.service import ServiceProvider

providers = [
    FastapiProvider(),
    DatabaseProvider(),
    ServiceProvider(),
]
container = make_async_container(*providers)
