# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template users handler module.
"""

import json

import app
import chalicelib.core as core
import chalicelib.handlers as handlers
from chalice import Response

# Core needs to be imported before controllers

router = app.app

SAMPLE_USER_DICT = {
    "username": "user1",
    "name": "Mario",
    "surname": "Benito Rodriguez",
}


@router.route("/")
def index():

    return {"hello": "world"}


@core.logger
@router.route("/users", methods=["GET"])
def list_users():

    handlers.save_request(router.current_request)

    print(router.current_request.to_dict())

    return Response(
        body=json.dumps([SAMPLE_USER_DICT]),
        status_code=200,
    )


@router.route("/users", methods=["POST", "PUT"])
def create_user():
    handlers.save_request(router.current_request)
    body = router.current_request.json_body

    print(body)

    return Response(
        body=json.dumps(SAMPLE_USER_DICT),
        status_code=200,
    )


@router.route("/users/{uid}", methods=["GET"])
def get_user(uid):

    handlers.save_request(router.current_request)

    print(router.current_request.to_dict())
    print(uid)

    return Response(
        body=json.dumps(SAMPLE_USER_DICT),
        status_code=200,
    )


@router.route("/users/{uid}", methods=["DELETE"])
def delete_user(uid):

    handlers.save_request(router.current_request)

    print(router.current_request.to_dict())
    print(uid)

    return Response(
        body="OK. Usuario borrado.",
        status_code=200,
    )
