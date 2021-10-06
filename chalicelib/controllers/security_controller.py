# Created in June 24, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Security controller module.
"""

import chalicelib.core as core
import chalicelib.logs as logs
import chalicelib.resources as resources
import jwt
from chalice.app import Request
from chalicelib.controllers import Controller
from chalicelib.dto.security import AuthenticationPayload
from chalicelib.exceptions import AuthenticationException

main_resources: resources.Resources = resources.resources


class SecurityController(Controller):
    """
    Security controller class reference.

    Contains the JWT token validation (a simple one, already have
    a service in API Distribution for that) and exposing a method for
    getting (for now) the user ID from kernel.
    """

    UTF8_FORMAT = "utf-8"

    @property
    def authentication_payload(self):
        return self.__authentication_payload

    @authentication_payload.setter
    def authentication_payload(self, value):
        self.__authentication_payload = value

    @core.register("security")
    def __init__(self, request: Request) -> None:
        super().__init__()

        self.authentication_payload = self.get_payload(
            request.headers[main_resources.X_AUTH_TOKEN]
        )

    def get_payload(self, authentication_token: str) -> AuthenticationPayload:
        """
        Validate JWT token with SHA256 algorithm (API Distribution uses
        this algorithm) and retrieve the payload from its content.

        Payload is exposed in a DTO way.

        :param authentication_token: Authentication token
        :type authentication_token: str

        :return: The Authentication payload to retrieve
        :rtype: :class: `chalicelib.dto.security.AuthenticationPayload`
        """

        try:
            return AuthenticationPayload(
                **jwt.decode(
                    authentication_token, options={"verify_signature": False}
                )
            )
        except (jwt.exceptions.PyJWTError,) as e:
            logs.system_logger.log(
                "error",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.get_payload.__name__
                )
                + "Catching error: {}".format(str(e)),
            )
            raise AuthenticationException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.get_payload.__name__
                )
                + "Payload cannot be retrieved from this token"
            )
