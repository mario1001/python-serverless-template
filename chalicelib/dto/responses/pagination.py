# Created in June 18, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
DTO Response color module.
"""

from typing import Any, Dict, List, Union

import chalicelib.dto.responses as responses


class ResponsePagination(responses.ServiceResponse):
    """
    Response for pagination
    """

    # Current url
    self: str
    # First url
    first: Union[str, None]
    # Last url
    last: Union[str, None]
    # Prev url
    prev: Union[str, None]
    # Next url
    next: Union[str, None]
    # query
    query: Dict[str, Any]
    # total number of results
    total_size: int
    # current count of results
    count: int
    # results
    results: List[Any]
