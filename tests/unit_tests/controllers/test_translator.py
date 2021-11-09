import chalicelib.exceptions as exceptions

import chalicelib.dto as dto

import chalicelib.controllers.translator as translator
import pytest
import tests.data as data


def test_bean_controller_initialization():

    bean_controller = translator.BeanController()

    assert bean_controller


def test_bean_controller_no_bean_exception():

    bean_controller = translator.BeanController()

    with pytest.raises(exceptions.BeanNotFoundException) as exception:
        bean_controller.create_bean(request=data.requests.request_users_body)

    exception = exception.value

    assert exception
    assert isinstance(exception, exceptions.BeanNotFoundException)
    assert str(exception) == "Could not instantiate a bean for that bind"


def test_bean_controller_authentication_object():

    bean_controller = translator.BeanController()
    bean = bean_controller.create_bean(
        request=data.requests.request_authentication
    )

    assert bean
    assert isinstance(bean, dto.AuthenticationPayload)

    # You can also see that values are in the specific type (integer in this case)
    # but coming from string format within AWS Gateway event

    assert bean.dict() == {
        "exp": 2,
        "iat": 6,
        "iss": "test",
        "jti": "admin",
        "nbf": 3,
        "sub": 34,
    }
