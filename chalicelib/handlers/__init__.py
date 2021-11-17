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

from chalice import Chalice


@core.ApplicationContext
def initialize_context():
    """
    Main function for initializing application context

    Called when application raises, so it does not need
    to be requested anymore (already prepared in this module).
    """


def process_request(router: Chalice):
    """
    Main function for saving AWS Chalice request
    in the application context.

    You should use this one if you want context registration
    and configuration for next steps (custom components studying
    the request).

    Configuration components should be an optional flag
    in this functionality (it's executing always right now).

    :param router: Chalice application
    :type router: Chalice
    """

    def decorator(func):
        def wrapper(*args, **kwargs):

            import chalicelib.controllers as controllers

            core.ApplicationContext.application_context.requests = (
                router.current_request
            )
            data = func(*args, **kwargs)

            # Maybe this should be a decorator (separating concepts)
            # Check if data is serialized (if no -> apply serialization process)
            return {
                controllers.http.to_camel_case(key): value
                for key, value in vars(
                    controllers.http.HTTPResponse(*data)
                ).items()
            }

        return wrapper

    return decorator


initialize_context()

# Add the router components (little pieces of domain handler routers)

from chalicelib.handlers import users
