# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice main exceptions module.

Defines the exceptions for each layer, depending on the
modules here (organization and hierarchy).
"""

import chalicelib.exceptions.core_exceptions as core_exceptions

# Handler exceptions are some special ones, prefer importing directly with specific module
# Core needs to start with a bunch of static exceptions, special ones loading in time execution

import chalicelib.exceptions.repository_exceptions as repository_exceptions
import chalicelib.exceptions.security_exceptions as security_exceptions
import chalicelib.exceptions.service_exceptions as service_exception
import chalicelib.exceptions.validation_exceptions as validation_exceptions
