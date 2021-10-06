# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template core main module.

Imports the public annotations (GetMapping, PostMapping, etc...) to be
used along the service development.

Application context could be imported with inner modules,
but this module would not provide the instance to work with (not user-side)
"""

from chalicelib.core.decorators import classproperty, inject, logger, register
from chalicelib.core.connections import ClientPool
from chalicelib.core.context import ApplicationContext

# Context class would be setup with lambda rising

context_class = None
