from dishka import Provider, Scope, provide_all

from file_catalog.services import AdminService, CandidateService, FileService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        CandidateService,
        FileService,
        AdminService,
    )
