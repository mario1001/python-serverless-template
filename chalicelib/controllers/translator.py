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

    Also mentioning here that it's specially for searching
    classes with attributes definition and declaration
    (specially with DTO layer), not using the class properties/attributes
    for standard domain checks for example.

    Any new bean controller should override this class along with
    public method implementations.
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

                if not inspect.isclass(
                    class_, simple_parameters, complex_parameters
                ):
                    # Passing here of no class "format"
                    # (bean supposed to be a class type)

                    continue

                bean = cls.__check_type(
                    class_, simple_parameters, complex_parameters, table_name
                )

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
    def __check_type(
        cls, class_, standard_parameters, special_parameters, table_name
    ):
        if issubclass(class_, BaseModel):

            # Knowing it's a DTO pydantic model class type
            bean = cls.__inspect_pydantic(
                class_, standard_parameters, special_parameters, table_name
            )

        if not bean:

            # Should consider domain generic models here
            bean = cls.inspect_domain(
                class_, standard_parameters, special_parameters, table_name
            )

        if bean:
            return bean

    @staticmethod
    def __inspect_pydantic(
        class_: BaseModel,
        standard_attributes: dict,
        special_attributes: list,
        table_name: str = None,
    ) -> Union[BaseModel, None]:
        """
        Specific inspection method for pydantic distributions.

        Components should inherit from one main pydantic class
        called: BaseModel. Also would check the special types
        (for now only checking list attributes in schema defined)

        One of the pydantic model restrictions is the default contructor
        by using a full creation with attributes (you can use optional for
        the not strict ones of course) at last option, you can always define another
        __init__ constructor or builder method if really needed
        (even though pydantic is not designed for that).

        :param class_: class to study for instance creation
        :type class_: BaseModel

        :param standard_attributes: Dictionary with attributes inside
        :type standard_attributes: dict

        :param special_attributes: Special types to check and study
        :type special_attributes: list

        :return: The DTO model instance returned (or none value if
        requirements not accurated) and saved in context
        :rtype: Union[BaseModel, None]
        """

        try:

            # Inspect attributes for checking the special ones (lists and so on)
            # If having several special values, maybe a class should reimplement this

            table_found = False
            for attribute, schema in class_.__fields__.items():

                if table_name and schema.default == table_name:
                    table_found = True

                if isinstance(special_attributes, list) and (
                    schema.outer_type_ == List or schema.outer_type_ == list
                ):
                    standard_attributes[attribute] = special_attributes
                    break

            if not table_name or (table_name and table_found):
                return class_(**standard_attributes)
        except ValidationError:
            # Some of the attributes does not match with the model
            return

    def inspect_domain(
        self, class_, standard_attributes, special_attributes, table_name=None
    ) -> Union[object, None]:
        """
        Standard way for creating custom domain instances.

        What means a custom domain instance? It's just a class
        defined in the template (in the inspection packages) which
        represents different type of model (E.g. SQLAlchemy, MongoDB, DynamoDB...)

        It's a default implementation, but you could extend this functionality
        or changed it the way the bean is created, just as you want. This method
        is public because that specifically reason.

        :param class_: Specific class found to inspect
        :type class_: object

        :param standard_attributes: Data to provided for creating the instance
        :type standard_attributes: dict

        :param special_attributes: Some special information to use as data
        :type special_attributes: list

        :return: Instance created and saving in the context
        :rtype: Union[object, None]
        """

        try:

            # Depending on the model here, should check first the constructor
            # __init__ method, if no specified we can create the object with some
            # parameters and then poblate the special ones,

            if "__init__" in vars(class_):

                # In the other case, constructor is present on the bean class, just
                # provide everything as data.

                bean = class_(
                    **{
                        **standard_attributes,
                        **{
                            attribute: special_attributes
                            for attribute in inspect.signature(
                                class_.__init__
                            ).parameters
                            if attribute not in standard_attributes
                        },
                    }
                )

                valid_instance = None
                for attribute in vars(bean):
                    if attribute == table_name:
                        valid_instance = bean
                        break

                return valid_instance

            bean = class_(**standard_attributes)

            # Just iterate over the domain for searching a field like for special values
            valid_instance = None
            for attribute in vars(bean):

                if (
                    table_name
                    and attribute == table_name
                    and valid_instance is None
                ):
                    valid_instance = bean

                if getattr(bean, attribute) is None and special_attributes:
                    setattr(bean, attribute, special_attributes)
                    special_attributes = None

            return valid_instance
        except TypeError:
            # Some of the attributes does not match with the model
            return
