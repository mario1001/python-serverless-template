import pytest
from aws_resources.exceptions.http_exceptions import InternalServerErrorException
from pydantic.error_wrappers import ValidationError, ErrorWrapper
from pydantic import NoneIsNotAllowedError, BoolError, BaseModel
from chalicelib.dto.requests import RequestSequence, ServiceRequest
from chalicelib.exceptions import BadRequestException
from chalice.app import Response


@pytest.fixture
def mock_raise_exception_process_request(monkeypatch):
    from chalicelib.controllers.sequence_controller import SequenceController
    def process_request():
        raise InternalServerErrorException("SAMPLE EXCEPTION IN CONTROLLER")

    monkeypatch.setattr(SequenceController, "process_request", process_request)

@pytest.fixture
def mock_request_with_body(monkeypatch):
    from chalicelib.controllers.sequence_controller import SequenceController
    def request_with_body(*args, **kwargs):
        return Response(body={})

    monkeypatch.setattr(SequenceController, "process_request", request_with_body)

@pytest.fixture
def mock_raise_bad_request_exception(monkeypatch):
    from chalicelib.controllers.sequence_controller import SequenceController
    def mock_raise_bad_request_exception(*args, **kwargs):
        raise BadRequestException(error_message='example exception')
    monkeypatch.setattr(SequenceController, "process_request", mock_raise_bad_request_exception)

@pytest.fixture
def mock_raise_validation_error(monkeypatch):
    def mock_raise_validation_error(*args, **kwargs):
        raise ValidationError(
            [
                ErrorWrapper(NoneIsNotAllowedError(), "id")
            ],
            RequestSequence,
        )
    monkeypatch.setattr(ServiceRequest, "__init__", mock_raise_validation_error)