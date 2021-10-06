# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice main service module.

This module attempts to communicate with
rest of services defined in the project
(or in this layer in the end).

Also defines the main service to be injected
in controller layer (custom controllers should inherit
from HTTPController to do so).
"""

from typing import Callable, Dict, Tuple

import chalicelib.core as core
import chalicelib.dto.requests as requests
import chalicelib.dto.responses as responses
import chalicelib.exceptions as exceptions


class MainService(object):
    """
    Service layer main service class reference.

    Controllers would use that instance reference without
    knowing anything about internal domain service implementation/creation.

    It's intended to be the main service in this API (should handle
    every service features and operative functions).

    Handles service request depending on the type
    and execute one specific dispatcher method for responses.
    """

    @property
    def service_dispatcher(self) -> Dict[requests.ServiceRequest, Callable]:
        return self.__service_dispatcher

    @service_dispatcher.setter
    def service_dispatcher(self, value):
        self.__service_dispatcher = value

    def __init__(self) -> None:
        """
        Creates a main service instance with dispatcher functions inside.
        """

        self.service_dispatcher = {
            # ...requests.Custom_request: custom_function...
        }

    def dispatch(
        self, request: requests.ServiceRequest, method: str
    ) -> Tuple[int, responses.ServiceResponse]:
        """
        Main service dispatching method in this layer.
        Controllers request some certain type request, this
        method would then dispatch those requests somehow.

        :param request: Service requested by controller layer
        :type request: BaseModel

        :return: A DTO response constructed
        :rtype: BaseModel
        """

        if not isinstance(request, requests.ServiceRequest):
            raise exceptions.ServiceRequestException()

        # As a precondition service would have mapped request functions
        status_code, body = self.service_dispatcher[
            (request.__class__, method)
        ](request)

        core.ClientPool.close("rds")

        return (status_code, body)
