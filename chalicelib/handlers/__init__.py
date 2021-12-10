# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template handler layer.

Represents and contains the router functions mapped
with specific urls/endpoints.

Also supports some common functionalities
for the specific handlers (core related issues).
"""

import chalicelib.core as core


@core.ApplicationContext
def initialize_context():
    """
    Main function for initializing application context.

    Called when application raises, so it does not need
    to be requested anymore (already prepared in this module).
    """


initialize_context()

# Add the router components (little pieces of domain handler routers)

from chalicelib.handlers import users
