# Created in June 17, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template Microservice repository exception module.

Repository layer manages database exceptions mainly, there's
several scenaries: Exceptions occurred when execution (commit/flush operation
supported by SQLAlchemy framework) or exceptions produced before making a
commit/flush.
"""


class InputParameterException(Exception):
    """
    Input exception class reference.

    Parameters are not allowed in the repository method
    or finding several wrong/weird types in some functionality.
    """
