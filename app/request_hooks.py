# app/request_hooks.py

from app.lifecycle import before_request, teardown_request

from flask import Flask


def register_request_hooks(app: Flask) -> None:

    app.before_request(before_request)
    app.teardown_request(teardown_request)
