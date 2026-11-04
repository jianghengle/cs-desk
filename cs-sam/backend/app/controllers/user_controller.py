from ..my_http import MyError, admin_required
from ..models.user_model import UserModel


def auth_user(req):
    # req.body is None when absent, or the raw string if it isn't valid JSON.
    body = req.body if isinstance(req.body, dict) else {}
    email = body.get('email')
    password = body.get('password')
    if not isinstance(email, str) or not email or not isinstance(password, str) or not password:
        raise MyError('email and password are required', 400)
    user = UserModel.auth_user(email, password)
    user.update_token()
    return {
        'email': user.email,
        'username': user.username,
        'groups': user.groups,
        'token': user.token,
        'isAdmin': user.isAdmin,
    }

@admin_required
def verify_token(req):
    user = req.user
    return {
        'email': user.email,
        'username': user.username,
        'groups': user.groups,
        'token': user.token,
        'isAdmin': user.isAdmin,
    }
