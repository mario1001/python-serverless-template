from abc import ABC, abstractmethod
from typing import List

import chalicelib.core as core
import chalicelib.dto.requests as requests
import chalicelib.dto.responses as responses


class BaseService(ABC, metaclass=core.context_class):
    """
    Abstract service interface reference.
    """

    # Base generic operations for working with common repositories

    @abstractmethod
    def find_responses(
        self, request: requests.ServiceRequest
    ) -> List[responses.ServiceResponse]:
        """
        Abstract method for creating a list of service responses
        with some specific domain entities attached to.

        Domain entities are going to be collected by repository
        layer (this service only works with entities for
        creating service responses).

        :param request: Service request (could be from different types)
        :type request: requests.ServiceRequest

        :return: List of DTO Responses objects
        :rtype: List[responses.ServiceResponse]
        """
