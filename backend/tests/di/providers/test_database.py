from dishka import Provider, Scope, provide
from file_catalog.config import Config


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.APP, override=True)
    def provide_config(self) -> Config:
        return Config(POSTGRES_DB='test_db')
