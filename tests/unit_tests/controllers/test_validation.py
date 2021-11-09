import chalicelib.controllers.validation as validation
import tests.data as data


def test_parameter_controller_empty():

    parameter_controller = validation.ParameterController()

    assert not parameter_controller.parameters
    assert parameter_controller.parameters == {}


def test_parameter_controller_process_empty():

    parameter_controller = validation.ParameterController()
    parameter_controller.process(
        request=data.requests.request_user_id, parameters={}
    )

    parameters = parameter_controller.parameters
    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)
    assert not list(parameters.values())[0]


def test_parameter_controller_process_simple_dictionary():

    parameter_controller = validation.ParameterController()
    parameter_controller.process(
        request=data.requests.request_user_id, parameters={"test": 12}
    )

    parameters = parameter_controller.parameters
    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)
    assert parameters[data.requests.request_user_id] == {"test": 12}


def test_path_parameter_process():

    parameter_controller = validation.PathParameterController()
    parameter_controller.process(request=data.requests.request_user_id)

    parameters = parameter_controller.parameters

    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)

    # For now, there is no conversion for string values obtained from Gateway event
    # This would be done within bean controller composition DTO process

    assert parameters[data.requests.request_user_id] == {"id": "3"}


def test_query_parameter_process():

    parameter_controller = validation.QueryParameterController()
    parameter_controller.process(request=data.requests.request_users)

    parameters = parameter_controller.parameters

    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)

    assert parameters[data.requests.request_users] == {
        "id_recurso": "2",
        "precio": "66",
        "top_height": "10.5",
    }


def test_query_parameter_process_no_pythonic():

    parameter_controller = validation.QueryParameterController()
    parameter_controller.process(
        request=data.requests.request_users, pythonic=False
    )

    parameters = parameter_controller.parameters

    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)

    assert parameters[data.requests.request_users] == {
        "idRecurso": "2",
        "precio": "66",
        "top_height": "10.5",
    }


def test_body_parameter_process():

    parameter_controller = validation.BodyController()
    parameter_controller.process(request=data.requests.request_users_body)

    parameters = parameter_controller.parameters

    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)

    assert parameters[data.requests.request_users_body] == {
        "username": "admin",
        "password": "admin",
    }


def test_body_parameter_process_no_json():

    parameter_controller = validation.BodyController()
    parameter_controller.process(request=data.requests.request_malformed)

    parameters = parameter_controller.parameters

    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)

    assert parameters[data.requests.request_malformed] == ["abc1234"]
