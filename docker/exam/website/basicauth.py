import functools
import os

import flask

def check_auth(username: str, password: str) -> bool:
    return username == "proctor" and \
            password == os.environ.get("DEFAULT_PROCTOR_PASSWORD", "")

def auth_required(f):
    @functools.wraps(f)
    def wrapped_view(**kwargs):
        auth = flask.request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs)

    return wrapped_view
