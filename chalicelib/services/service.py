"""
Abstract service interface
"""

from abc import ABC

import chalicelib.core as core


class Service(ABC, metaclass=core.context_class):
    """
    Abstract service interface reference.
    """
