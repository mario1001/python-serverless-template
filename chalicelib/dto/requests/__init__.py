# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template DTO Requests main module.

Defines service requests for main service. Using model
would be the best way for layer communication in case of operation needs.

There's a default model service request that would apply
to the other requests (request encapsulation here).
"""

from pydantic import BaseModel


class ServiceRequest(BaseModel):
    """
    Service request base model class reference.
    """


from chalicelib.dto.requests.request_pagination import RequestPagination
