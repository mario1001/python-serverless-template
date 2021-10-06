# Created in June 24, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template Microservice security exception module.
"""


class AuthenticationException(Exception):
    """
    Authentication exception class reference.

    Mainly for situations when payload cannot be decoded
    and the information is untrusted or some type of error
    during the authentication process data.
    """
