from typing import List
from http import HTTPStatus

import chalicelib.core as core
import chalicelib.dto.requests as requests
import chalicelib.dto.responses as responses
import chalicelib.exceptions as exceptions
import chalicelib.logs as logs
import chalicelib.services as services
from aws_resources.exceptions import HTTPRequestException
from chalice.app import Request, Response
from chalicelib.controllers.controller import Controller


class HTTPController(Controller):
    """
    HTTP controller class reference.

    Controller defines the operations for HTTP requests
    along all services, it's just the entrance for service content
    by itself.

    Controller layer is independent than handler lambda functions,
    having the same role along with other abstract features prepared
    depending on the implementation. It's class-oriented architecture
    versus the scripting functions.
    """

    @property
    def main_service(self) -> services.MainService:
        return self.__main_service

    @main_service.setter
    def main_service(self, value):
        self.__main_service = value

    @property
    def http_requests(self) -> List[Request]:
        return self.__http_requests

    @http_requests.setter
    def http_requests(self, value):
        self.__http_requests = value

    def __init__(self) -> None:
        self.main_service = services.main_service
        self.http_requests = list()

    def process_request(
        self, request: requests.ServiceRequest, method: str
    ) -> Response:
        """
        Processing method implementation for a HTTP controller.

        Should be invoked only from controller layer (not from
        the handler layer with routers). Each controller will at least
        manage requests with service layer invocation.

        That's why this method exists and generic HTTP Responses
        would be generated in this method. A child controller could always
        override this by providing more functionality.

        :param request: A service request to process
        :type request: requests.ServiceRequest

        :return: RESTful API HTTPResponse instance to return
        :rtype: :class: `aws_resources.restful_api.HTTPResponse`
        """

        self.http_requests.append(request)

        try:
            status_code, body = self.main_service.dispatch(request, method)
        except HTTPRequestException as e:
            return Response(status_code=e.http_status, body=e.get_response().body)
        except exceptions.DatabaseException as e:
            logs.system_logger.log(
                "error",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.process_request.__name__
                ) + "Catching error: {}".format(str(e)),
            )
            return Response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                body="An exception occurred while interacting with the database",
            )
        except Exception as e:
            logs.system_logger.log(
                "error",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.process_request.__name__
                )
                + "Catching error: {}".format(str(e)),
            )
            raise exceptions.InternalServerErrorException(error_message=str(e))

        if isinstance(body, responses.ServiceResponse):
            return Response(status_code=status_code, body=body.json())

        return Response(status_code=status_code, body=body)

    @staticmethod
    def save_request_in_context(request: Request):
        core.ApplicationContext.application_context.request = request
