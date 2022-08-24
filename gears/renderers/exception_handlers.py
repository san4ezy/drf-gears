from copy import copy

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions

from rest_framework.response import Response
from rest_framework.views import set_rollback

from gears import Error, RESPONSE_ERROR_MAPPING


class ExceptionHandler(object):
    default_code: str = 'unknown_error'
    default_description: str = 'Unknown error'
    root_field_name: str = 'errors'

    def __init__(self, exc, context):
        self.exc = exc
        self.context = context
        self.status_code = exc.status_code
        self.errors: list = []
        self.data = {}

    def _super(self):
        exc = self.exc
        if isinstance(exc, Http404):
            exc = exceptions.NotFound()
        elif isinstance(exc, PermissionDenied):
            exc = exceptions.PermissionDenied()

        if isinstance(exc, exceptions.APIException):
            headers = {}
            if getattr(exc, 'auth_header', None):
                headers['WWW-Authenticate'] = exc.auth_header
            if getattr(exc, 'wait', None):
                headers['Retry-After'] = '%d' % exc.wait
            set_rollback()

            self.data = exc.detail
            self.exc = exc
            self.headers = headers

    def process_list(self, detail: list, location):
        for v in detail:
            self.process(v, location=location)

    def process_dict(self, detail: dict, location):
        for k, v in detail.items():
            self.process(v, location=k)

    def process_error(self, detail, location):
        self.errors.append(
            Error(
                code=detail.code or self.default_code,
                location=location,
                description=str(detail) or self.default_description,
                detail=None,
            )
        )

    def process(self, detail, location: str = None):
        if isinstance(detail, list):
            return self.process_list(detail, location)
        if isinstance(detail, dict):
            return self.process_dict(detail, location)
        return self.process_error(detail, location)

    def response(self) -> list[dict]:
        def _build(e: Error):
            er = copy(RESPONSE_ERROR_MAPPING.get(e.code, e))
            for k in ('code', 'location', 'description', 'detail',):
                # set values from me or e
                setattr(er, k, getattr(er, k) or getattr(e, k))
            return er.__dict__
        return [_build(err) for err in self.errors]

    def handle(self):
        self._super()
        self.process(self.data)
        data = {
            self.root_field_name: self.response(),
        }

        return Response(
            data=data,
            headers=self.headers,
            status=self.status_code,
        )


def exception_handler(exc, context):
    return ExceptionHandler(exc, context).handle()
