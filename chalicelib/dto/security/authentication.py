# Created in June 24, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template DTO authentication module.
"""

from pydantic import BaseModel


class AuthenticationPayload(BaseModel):
    """
    Authentication payload DTO class reference.
    """

    sub: int
    iss: str
    iat: int
    exp: int
    nbf: int
    jti: str
