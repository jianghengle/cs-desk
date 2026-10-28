import simplejson as json
from decimal import Decimal
#from .models.user_model import UserModel

class MyError(Exception):
    def __init__(self, message='MyError', code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

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
        self.token = None

        token = self.headers.get('Authorization', None)
        if token:
            self.token = token
            #self.user = UserModel.get_by_token(token)


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
