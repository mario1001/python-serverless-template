from typing import Union, List, Dict, Any
from chalicelib.dto.responses import ServiceResponse


class ResponseError(ServiceResponse):
    """
    Error response model class
    """
    message: Union[List[Any], Dict[str, Any], str]