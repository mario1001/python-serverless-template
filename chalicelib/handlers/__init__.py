# Created in June 15, 2021 by Mario Benito.
#
# Despite this software is developed by Neoris, it belongs to Santillana,
# either first version of the License, or (at your option) any later version.

"""
PRIDIG template handler layer.

Represents and contains the router functions mapped
with specific urls/endpoints. These ones would call
dispatcher logic along with controllers.
"""


from abc import ABCMeta

import chalicelib.core as core
from chalice.app import Request


@core.ApplicationContext
def initialize_context():
    """
    Main function for initializing application context
    """

    class ContextABC(
        ABCMeta, core.ApplicationContext.application_context.registering_type
    ):
        """
        Base Abstract class with context beans implementation.

        Every new layer feature to inject should
        have this metaclass (as declaration).
        """

    core.context_class = ContextABC


def save_request(request: Request):
    core.ApplicationContext.application_context.request = request


initialize_context()

# Add the router components (little pieces of domain handler routers)

from chalicelib.handlers import users
