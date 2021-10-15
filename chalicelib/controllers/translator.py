# Created in October 9, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless microservice template translator module.

Defines a translator controller for creating models in time execution.
"""

import inspect
from typing import Any, Dict, List, Union

from pydantic import BaseModel, ValidationError

import chalicelib.core as core
import chalicelib.controllers as controllers
import chalicelib.exceptions as exceptions

from pathlib import Path

from chalice.app import Request


class BeanController(controllers.Controller):
    """
    Bean controller class reference.

    This controller should be used for translation between
    certain data (AWS Chalice requests into beans).

    For now, bean translator does not search other components
    than DTO/domain classes. This could be adapted in future releases.
    """

    # Maybe this could be parameterized as environment vars
    ROOT_PACKAGES = ["dto", "domain"]

    DOUBLE_UNDERSCORES = "__"

    @property
    def path_parameter_controller(
        self,
    ) -> controllers.validation.PathParameterController:
        return self.__path_parameter_controller

    @path_parameter_controller.setter
    def path_parameter_controller(self, value):
        self.__path_parameter_controller = value

    @property
    def query_parameter_controller(
        self,
    ) -> controllers.validation.QueryParameterController:
        return self.__query_parameter_controller

    @query_parameter_controller.setter
    def query_parameter_controller(self, value):
        self.__query_parameter_controller = value

    @property
    def body_controller(
        self,
    ) -> controllers.validation.BodyController:
        return self.__body_controller

    @body_controller.setter
    def body_controller(self, value):
        self.__body_controller = value

    @core.inject(ref=controllers.validation.PathParameterController)
    @core.inject(ref=controllers.validation.QueryParameterController)
    @core.inject(ref=controllers.validation.BodyController)
    def __init__(self) -> None:
        """
        Create a new translator bean instance.

        Intended for only one request per execution, always resetting
        the memory for next steps (this should be taken for granted).
        """

        super().__init__()
        self.__log_parameter_controllers(
            [self.path_parameter_controller, self.query_parameter_controller]
        )

    @core.logger
    def __log_parameter_controllers(
        self, controllers: List[controllers.validation.ParameterController]
    ) -> None:
        """
        Private method for logging the parameters in controllers injected.
        """

    @core.logger
    def create_bean(self, request: Request) -> Union[object, None]:
        """
        Create a bean with AWS Chalice request.

        Firstly scans every available resource as model
        (DTO/domain classes existing in the template packages).

        :raises exceptions.BeanNotFoundException: When no model associated with the data provided

        :param request: AWS Chalice request mapped
        :type request: chalice.app.Request

        :return: The bean instantiated or null value if not models configured
        :rtype: Union[object, None]
        """

        self.path_parameter_controller.process(request=request)
        self.query_parameter_controller.process(request=request)
        self.body_controller.process(request=request)

        path_parameters = self.path_parameter_controller.parameters
        query_parameters = self.query_parameter_controller.parameters

        # Body is a rare case, this one should be studied carefully when doing inspection
        # If body is in JSON format (dict) just add it as standard parameters

        body_parameters = self.body_controller.parameters

        global_parameters = {**path_parameters, **query_parameters}

        if isinstance(body_parameters, dict):
            global_parameters = {**global_parameters, **body_parameters}
            body_parameters = list()

        for model in self.ROOT_PACKAGES:
            bean = self.inspect_model(
                domain_package=Path(__file__).parent / model,
                simple_parameters=global_parameters,
                complex_parameters=body_parameters,
            )

            return bean

    @classmethod
    def inspect_model(
        cls,
        model_package: str,
        table_name: str = None,
        simple_parameters: Dict[str, Any] = dict(),
        complex_parameters: List[Any] = list(),
    ) -> type:
        """
        Main method for getting domain model classes (or other types if so)
        that make references to the table name introduced as parameter.

        Uses inspecting features in some configured module. Also checks
        for submodules inside this one.

        Raises an exception when searches don't provide any located class.

        :param table_name: Table name in domain package
        :type table_name: str

        :param simple_parameters: Raw dictionary obtained from request, defaults to dict()
        :type simple_parameters: Dict[str, Any], optional

        :param complex_parameters: Special attributes we need to take care of, defaults to list()
        :type complex_parameters: List[Any], optional

        :raises exceptions.BeanNotFoundException: When no model associated with the data provided

        :return: Custom class instance (with inheritance or not)
        :rtype: type
        """

        model_package_module = cls.__import_package(model_package)

        for module in dir(model_package_module):
            if not module.startswith(cls.DOUBLE_UNDERSCORES):
                class_ = getattr(model_package_module, module)

                if not inspect.isclass(class_):
                    # Passing here of no class "format"
                    # (bean supposed to be a class type)

                    continue

                bean = cls.__check_type(class_)

                if bean:
                    return bean

        raise exceptions.BeanNotFoundException(
            "Could not instantiate binded bean"
        )

    @staticmethod
    def __import_package(name):
        """
        Loads dynamically some specific package/subpackage.

        :param name: specific path for package
        :type name: str

        :return: object (could be module or class in our case)
        """

        components = name.split(".")
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    @classmethod
    def __check_type(cls, class_):
        if issubclass(class_, BaseModel):

            # Knowing it's a DTO model class type
            bean = cls.__inspect_pydantic(class_)

        if bean:
            return bean

    @staticmethod
    def __inspect_pydantic(
        class_, standard_attributes, special_attributes
    ) -> bool:
        try:
            class_(**standard_attributes)
        except ValidationError:
            # Some of the attributes does not match with the model
            return False

        return True
