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


from chalicelib.controllers.controller import Controller
from chalicelib.controllers.security_controller import SecurityController
from chalicelib.controllers.http_controller import HTTPController
from chalicelib.controllers.color_controller import ColorController
