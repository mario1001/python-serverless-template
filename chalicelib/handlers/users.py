# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template users handler module.
"""

import json

import app
import chalicelib.core as core
import chalicelib.controllers as controllers
from chalice import Response

# Core needs to be imported before controllers

router = app.app

SAMPLE_USER_DICT = {
    "username": "user1",
    "name": "Mario",
    "surname": "Benito Rodriguez",
}


@core.logger
@router.route("/")
def index():

    return {"hello": "world"}


@core.logger
@router.route(
    "/users", methods=[controllers.http.HTTPRequestTypes.GET.value.upper()]
)
@core.process_request(router)
def list_users():

    print(router.current_request.to_dict())

    return Response(
        body=json.dumps([SAMPLE_USER_DICT]),
        status_code=200,
    )


@core.logger
@router.route(
    "/users",
    methods=[
        controllers.http.HTTPRequestTypes.POST.value.upper(),
        controllers.http.HTTPRequestTypes.PUT.value.upper(),
    ],
)
@core.process_request(router)
def create_user():

    body = router.current_request.json_body

    print(body)

    return Response(
        body=json.dumps(SAMPLE_USER_DICT),
        status_code=200,
    )


@core.logger
@router.route(
    "/users/{uid}",
    methods=[controllers.http.HTTPRequestTypes.GET.value.upper()],
)
@core.process_request(router)
def get_user(uid):

    print(router.current_request.to_dict())
    print(uid)

    return Response(
        body=json.dumps(SAMPLE_USER_DICT),
        status_code=200,
    )


@core.logger
@router.route(
    "/users/{uid}",
    methods=[controllers.http.HTTPRequestTypes.DELETE.value.upper()],
)
@core.process_request(router)
def delete_user(uid):

    print(router.current_request.to_dict())
    print(uid)

    return Response(
        body="OK. Usuario borrado.",
        status_code=200,
    )
