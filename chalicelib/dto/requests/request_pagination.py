# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
DTO Request pagination module.
"""

from typing import Optional
from pydantic import root_validator
from chalicelib.dto.requests import ServiceRequest


class RequestPagination(ServiceRequest):
    """
    Request pagination class reference.

    Should be only used when query pagination parameters
    requested for service.
    """

    page: Optional[int] = None
    page_size: Optional[int] = None
    order_by: Optional[str] = None
    order_type: Optional[str] = None

    @root_validator
    def check_page_page_size(cls, values):
        page, page_size = values.get("page"), values.get("page_size")
        if page is None and page_size is not None:
            raise ValueError("page is None and page_size has value")
        elif page is not None and page_size is None:
            raise ValueError("page has value None and page_size is None")
        return values

    @root_validator
    def check_order_by_order_type(cls, values):
        order_by, order_type = values.get("order_by"), values.get("order_type")
        if order_by is None and order_type is not None:
            raise ValueError("order_by is None and order_type has value")
        elif order_by is not None and order_type is None:
            raise ValueError("order_by has value None and order_type is None")
        return values
