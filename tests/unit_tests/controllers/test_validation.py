import chalicelib.controllers.validation as validation

import tests.data as data


def test_parameter_controller_empty():

    parameter_controller = validation.ParameterController()

    assert not parameter_controller.parameters
    assert parameter_controller.parameters == {}


def test_parameter_controller_process():

    parameter_controller = validation.ParameterController()
    parameter_controller.process(
        request=data.requests.request_user_id, parameters={}
    )

    parameters = parameter_controller.parameters
    assert parameters
    assert len(parameters) == 1
    assert isinstance(list(parameters.keys())[0], data.requests.app.Request)
    assert not list(parameters.values())[0]
