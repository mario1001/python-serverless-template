# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template decorators to work with.

User-friendly decorators for this template
dependency injections, automatic logs or class
properties as main functionality for now.
"""

import re
from typing import Iterable

import chalicelib.core as core
import chalicelib.exceptions as exceptions
import chalicelib.logs as logs

# For passing from Camel case to snake case
pattern = re.compile(r"(?<!^)(?=[A-Z])")


class ClassPropertyDescriptor(object):
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def register(*args, **kwargs):
    """
    Decorator for registering components.

    Context beans collected with a registry key, this one needs
    to be loaded here with the help of the register decorator.

    There's always a default component generation key (formed with
    class associated) but you could define beans for different situations.
    That's the way it's implemented, set the key with register decorator,
    you could check these annotations on the controller layer with several classes
    designed for that.
    """

    def decorator(f):
        main_args = list()
        for arg in args:
            if not isinstance(arg, str):
                main_args.append(str(arg))
        main_kwargs = dict()
        for kwarg, value in kwargs.items():
            if not isinstance(value, str):
                main_kwargs[kwarg] = str(value)
        f.register = (tuple(args), kwargs)
        return f

    return decorator


def logger(func):
    """
    Decorator for logging with project logs module.

    Making a log everytime with a custom method can be some headache,
    that's why this decorator will log method name along with parameters for you.

    After making some system logs it executes the function
    passed as argument, that's the way it's intended to be.
    """

    def wrapper(*args, **kwargs):
        logs.system_logger.log(
            "info",
            "[{MODULE}][{FUNCTION}]: ".format(MODULE=__name__, FUNCTION=logger.__name__)
            + "Function {type} and arguments: {data}".format(
                type=func.__name__, data=str(list(args) + list(kwargs))
            ),
        )

        return func(*args, **kwargs)

    return wrapper


def inject(ref: object, values: Iterable = tuple()):
    """
    Decorator for dependency injection (DI functionality) for
    any component of this framework with the help of context.

    Components need to be registered with context register type
    providing for this functionality to work well, when using any
    other object would raise an specific injection exception.

    :param func: Class type to inject

    :return: An instance to work with
    :rtype: :class: `func`
    """

    if not ref:

        # Really cannot "inspect" property with instance
        # or cannot assign to the specific module var

        raise exceptions.core_exceptions.DependencyInjectionException(
            "[{MODULE}][{FUNCTION}]: ".format(MODULE=__name__, FUNCTION=inject.__name__)
            + "You need to specify the reference (first attribute)"
        )

    # Allowing perfectly not providing a key combination (if so)

    # reference should be a module or a class instance
    # (also working with class attributes but to be tested), would check
    # the injection type attribute (or property defined whatever)
    # and save the reference from there

    injection_to_search = pattern.sub("_", ref.__name__).lower()

    logs.system_logger.log(
        "info",
        "[{MODULE}][{FUNCTION}]: ".format(MODULE=__name__, FUNCTION=inject.__name__)
        + "Trying to inject an instance on type {type} with values {keys}".format(
            type=ref.__name__, keys=str(values)
        ),
    )

    application_context: core.ApplicationContext = (
        core.ApplicationContext.application_context
    )
    bean = application_context.request_instance(
        ref, [ref.__name__] + [arg for arg in values]
    )

    # Check in case of instance method (with self reference)
    injection_to_search = pattern.sub("_", ref.__name__).lower()

    def inner(f):
        def wrapped(*args, **kwargs):
            if (
                args
                and args[0].__class__ not in [int, float, tuple, list, dict]
                and isinstance(args[0], object)
            ):
                setattr(args[0], injection_to_search, bean)
            return f(*args, **kwargs)

        return wrapped

    if hasattr(ref, injection_to_search):
        # Really can "inspect" property or attribute with instance
        # just making the injection there instead of the main reference
        # (useful for classes)

        setattr(ref, injection_to_search, bean)
    else:
        # Create the instance in a class property of the reference

        def instance(ref):
            return bean

        ref.instance = classproperty(instance)

    return inner
