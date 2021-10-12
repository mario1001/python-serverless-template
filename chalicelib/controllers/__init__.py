# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template controller layer module.

Main purpose of this layer is provide external utilities as within core
by making a some inspired framework for serverless applications (could be
for several goals, microservices or just step functions with AWS lambda per example).

This module defines the concept of Object oriented-paradigm controllers that
maintain the flow execution during the first stages, required of Abstract
patterns defined (known as interfaces) causing the operative for this project service.

There are different type of controllers right here, ones declared for validation and
logging features (better understanding of the program), utilities ones (just for authentication
or security issues) and bean translator ones for object composite process.

This module would export the controller beans for the program execution
in the specific layers of your application, every controller have already the controller
role just like the MVC software design (Model-View-Controller pattern).
"""

# Here goes the controller custom classes

from abc import ABC, abstractmethod
import chalicelib.core as core


class Controller(ABC, metaclass=core.context_class):
    """
    Abstract controller interface reference.

    Any class extending this type would be considered
    a controller. Main purpose of a controller is handle
    data, manage redirections with other controllers or
    call some other core component for its functionality.

    These ones are designed for a serverless architecture,
    mainly for AWS Chalice applications with other backend features.
    """


class ProcessingController(Controller):
    """
    Abstract Processing controller class reference.

    :param Controller: [description]
    :type Controller: [type]
    """

    @abstractmethod
    def process(self):
        """
        Main method for processing information.

        Parameters could be customized along with the implementation.
        """


import chalicelib.controllers.security as security
import chalicelib.controllers.validation as validation
import chalicelib.controllers.translator as translator
