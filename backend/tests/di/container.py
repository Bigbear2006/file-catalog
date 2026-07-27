from dishka import make_async_container
from file_catalog.di.container import providers

from tests.di.providers.test_database import TestDatabaseProvider

test_providers = [TestDatabaseProvider()]
test_container = make_async_container(*providers, *test_providers)
