import functools
import simplejson as json
from decimal import Decimal
from .errors import MyError
from .models.user_model import UserModel

class MyReq:
    def __init__(self, event):
        self.path = event['path']
        self.method = event['httpMethod']
        if self.method == 'OPTIONS':
            return

        self.body = event.get('body', None)
        self.raw_body = event.get('body', None)
        if self.body:
            try:
                self.body = json.loads(self.body, parse_float=Decimal)
            except Exception as e:
                pass
        self.headers = event.get('headers', {})
        self.queryStringParameters = event.get('queryStringParameters', {})
        self.user = None
        self.token = self.headers.get('Authorization', None)

def MyResp(data=None, code=200):
    return {
        "statusCode": code,
        "body": json.dumps(data),
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, Origin, Accept, X-Token, X-AppToken',
            'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS'
        },
    }

class MyRouter:
    def __init__(self, path_handlers):
        self.path_handlers = path_handlers

    def add_handlers(self, handlers):
        self.path_handlers.extend(handlers)

    def route(self, req):
        req_method = req.method
        if req_method == 'OPTIONS':
            return MyResp()

        req_path_parts = self.split_path(req.path)
        for (method, path, handler) in self.path_handlers:
            if req_method != method:
                continue
            (match, params) = self.path_match(req_path_parts, self.split_path(path))
            if match:
                return MyResp(handler(req, *params))
        raise MyError('Did not find the handler for path ' + req.path, 404)

    def path_match(self, req_path_parts, handler_path_parts):
        params = []
        if len(req_path_parts) != len(handler_path_parts):
            return (False, None)
        for i in range(len(req_path_parts)):
            req_path_part = req_path_parts[i]
            handler_path_part = handler_path_parts[i]
            if handler_path_part.startswith(':'):
                params.append(req_path_part)
            elif handler_path_part != req_path_part:
                return (False, None)
        return (True, tuple(params))

    def split_path(self, path):
        parts = []
        for s in path.split('/'):
            part = s.strip()
            if part:
                parts.append(part)
        return parts


def check_groups(user, groups):
    if not user:
        raise MyError('Cannot find user!', 403)
    for g in user.groups:
        if g in groups:
            return
    raise MyError('Your group is not allowed!', 403)

def group_required(groups=[]):
    def _my_decorator(controller):
        def _decorator(req, *args, **kwargs):
            check_groups(req.user, groups)
            return controller(req, *args, **kwargs)
        return _decorator
    return _my_decorator

def check_user(req):
    if req.token:
        req.user = UserModel.get_by_token(req.token)
    if not req.user:
        raise MyError('Cannot find user!', 403)
    if req.user.token_expired():
        raise MyError('Invalid token!', 403)

def user_required(controller):
    @functools.wraps(controller)
    def _decorator(req, *args, **kwargs):
        check_user(req)
        req.user.update_token_used_at()
        return controller(req, *args, **kwargs)
    return _decorator

def admin_required(controller):
    @functools.wraps(controller)
    def _decorator(req, *args, **kwargs):
        check_user(req)
        if not req.user.isAdmin:
            raise MyError('Not admin!', 403)
        req.user.update_token_used_at()
        return controller(req, *args, **kwargs)
    return _decorator
