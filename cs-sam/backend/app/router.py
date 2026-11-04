from .my_http import MyError, MyReq, MyResp, MyRouter
from .controllers import admin_controller
from .controllers import user_controller

def handle(event, context):
    try:
        req = MyReq(event)
        router = MyRouter([
            ('POST', '/api/user/auth-user', user_controller.auth_user),
            ('POST', '/api/user/verify-token', user_controller.verify_token),
        ])
        router.add_handlers(admin_controller.AdminRoutes)
        return router.route(req)
    except MyError as err:
        print('MyError: ' + err.message )
        return MyResp({ 'err': err.message }, err.code)
    except Exception as e:
        print(e)
        return MyResp({ 'err': str(e) }, 500)
