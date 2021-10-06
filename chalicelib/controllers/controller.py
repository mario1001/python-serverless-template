from abc import ABC
import chalicelib.core as core


class Controller(ABC, metaclass=core.context_class):
    """
    Controller interface reference.

    Any class extending this type would be considered
    a controller instance, having three roles associated:

    -Parameter validation obtained from AWS Responses/structures.
    -Standard custom implementation for processing those HTTP requests.
    -Calling this project service layer somehow/someway.

    Controllers are made for processing HTTP requests for this service.
    So it does not have an operation for that with specifications, with
    serverless architecture controllers will rise up directly for processing
    requests (that's they way these components are designed for).
    """