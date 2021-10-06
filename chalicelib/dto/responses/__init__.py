# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template DTO Responses main module.

Defines service responses for HTTP controllers.

There's a default model service response that need to apply
to the other requests (request encapsulation here).
"""

from pydantic import BaseModel


class ServiceResponse(BaseModel):
    """
    Service response base class reference.

    Every new DTO response should inherit from this base class.
    """


from chalicelib.dto.responses.error import ResponseError
from chalicelib.dto.responses.pagination import ResponsePagination
