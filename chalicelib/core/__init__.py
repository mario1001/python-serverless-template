# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template core main module.

Imports the public annotations (GetMapping, PostMapping, etc...) to be
used along the service development.

Application context could be imported with inner modules,
but this module would not provide the instance to work with (not user-side).

Also here importing the required modules (not all functionality). Serialization
module should be used directly because needs the controller layer to be raised first.
Core importation is for handler layer, controller layer, service layer and repository layer,
that's why it's designed to be as slightly as possible.
"""

import chalicelib.core.singleton as singleton

# Exposed for now only for handler layer (some special functionalities)
# That's why its using the from ... import ... syntax here
from chalicelib.core.decorators import (
    classproperty,
    inject,
    logger,
    register,
    process_request,
)
from chalicelib.core.context import ApplicationContext
