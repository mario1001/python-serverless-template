# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template controller layer module.

This module defines the concept of Object oriented-paradigm controllers that
maintain the flow execution during the first stages, required of Abstract
patterns defined (known as interfaces) causing the operative of this project service.

Makes every "external" validation for parameters obtained from AWS events
and creates service requests (specific object on DTO layer
created in time execution) for the service layer.

Some of the validations also reside in the service layer, these ones are called
"internal" validations and are treated separately after controller execution.

Each controller would represent different type of process (one for endpoint
definition, another one for parameter validation or many other features
that require some initial management in the end). This technique is fully inspired
by Spring framework in Java.
"""

# Here goes the controller custom classes

from abc import ABC
import chalicelib.core as core


class Controller(ABC, metaclass=core.context_class):
    """
    Controller interface reference.

    Any class extending this type would be considered
    a controller, having three roles associated:

    -Parameter validation obtained from AWS Responses/structures.
    -Standard custom implementation for processing those HTTP requests.
    -Calling this project service layer somehow/someway.

    Controllers are made for processing HTTP requests for this service.
    So it does not have an operation for that with specifications, with
    serverless architecture controllers will rise up directly for processing
    requests (that's they way these components are designed for).
    """


import chalicelib.controllers.security_controller as security_controller
import chalicelib.controllers.validation as validation
import chalicelib.controllers.translator as translator
