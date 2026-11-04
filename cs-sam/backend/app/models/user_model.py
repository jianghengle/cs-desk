import bcrypt, uuid, secrets, string
import time
import html
from .model import Model
from ..services import dynamo_service
from ..errors import MyError


class UserModel(Model):
    TableName = 'CsUsers'
    GSIs = {
        'emailGSI': 'email',
        'tokenGSI': 'token',
    }
    # types: bool | enum | int | float | timestamp (seconds) | str | text | email | password | list (strs) | obj (all others)
    # modifiers: readonly, hidden, auto, required (only effectve on str)
    Fields = [
        ('id', 'str'),
        ('email', 'email', 'readonly'),
        ('username', 'str', 'required'),
        ('encryptedPassword', 'password'),
        ('isAdmin', 'bool'),
        ('groups', 'list'),
        ('token', 'str', 'hidden'),
        ('tokenUsedAt', 'timestamp', 'auto'),
        ('createdAt', 'timestamp', 'auto'),
        ('updatedAt', 'timestamp', 'auto'),
    ]

    def __init__(self, data={}):
        super().__init__(data)
        self.data.pop('encryptedPassword', None)
        self.data.pop('token', None)

    def token_expired(self):
        if not self.tokenUsedAt:
            return False
        return int(time.time()) - self.tokenUsedAt > 24 * 60 * 60

    def update_token(self):
        new_token = secrets.token_urlsafe(64)
        timestamp = int(time.time())
        updates = {
            'token': new_token,
            'tokenUsedAt': timestamp,
            'updatedAt': timestamp,
        }
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'id', self.id, updates)
        self.token = self.data['token'] = new_token
        self.tokenUsedAt = self.data['tokenUsedAt'] = timestamp
        self.updatedAt = self.data['updatedAt'] = timestamp
        return new_token
    
    def update_token_used_at(self):
        timestamp = int(time.time())
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'id', self.id, {'tokenUsedAt': timestamp})
        self.tokenUsedAt = self.data['tokenUsedAt'] = timestamp

    @staticmethod
    def auth_user(email, password):
        # email is a GSI attribute, not the table key, so query the index.
        user = UserModel.get_by_email(email)
        if not user:
            raise MyError('The user does not exist.', 403)
        if not user.encryptedPassword:
            raise MyError('Password not set.', 403)
        if bcrypt.checkpw(password.encode('utf-8'), user.encryptedPassword.encode('utf-8')):
            return user
        raise MyError('Failed to authenticate user.', 403)

    @classmethod
    def get_by_email(cls, email):
        if not email:
            raise MyError('No email', 400)
        return UserModel.get_by_index('emailGSI', email)

    @classmethod
    def get_by_token(cls, token):
        if not token:
            raise MyError('No token', 400)
        return UserModel.get_by_index('tokenGSI', token)

    @classmethod
    def create(cls, data):
        table = dynamo_service.get_table(UserModel.TableName)
        data['id'] = str(uuid.uuid4())
        # email is a GSI key, so it must be a non-empty string.
        if not data.get('email') or not isinstance(data['email'], str):
            raise MyError('Invalid email', 400)
        # DynamoDB can't enforce uniqueness on a GSI, so check before writing.
        if UserModel.get_by_email(data['email']):
            raise MyError('A user with this email already exists', 409)
        data['username'] = html.escape(data.get('username', ''))
        password = data.get('password')
        if not password or not isinstance(password, str) or len(password) < 8:
            raise MyError('Invalid password', 400)
        data['encryptedPassword'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        alphabet = string.ascii_letters + string.digits
        data['token'] = ''.join(secrets.choice(alphabet) for i in range(64))
        timestamp = int(time.time())
        data.pop('tokenUsedAt', None)
        data['createdAt'] = timestamp
        data['updatedAt'] = timestamp
        data.pop('password', None)
        # Only persist attributes defined in Fields; drop anything else the caller sent.
        field_names = {f[0] for f in cls.Fields}
        data = {k: v for k, v in data.items() if k in field_names}
        dynamo_service.create_item(table, data, 'id')
        item = UserModel(data)
        return item

    @classmethod
    def update(cls, key_value, updates):
        if 'username' in updates:
            updates['username'] = html.escape(updates['username'])
        # Never accept a raw hash from the caller; only set it from 'password'.
        updates.pop('encryptedPassword', None)
        password = updates.pop('password', None)
        if password is not None and (not isinstance(password, str) or len(password) < 8):
            raise MyError('Invalid password', 400)
        if password:
            updates['encryptedPassword'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        table = dynamo_service.get_table(UserModel.TableName)
        data = {}
        for field in cls.Fields[1:]:
            if field[0] in ['token', 'tokenUsedAt', 'createdAt', 'updatedAt']:
                continue
            field_name = field[0]
            if field_name in updates:
                data[field_name] = updates[field_name]
        data['updatedAt'] = int(time.time())
        dynamo_service.update_item(table, 'id', key_value, data)
        item = dynamo_service.get_item(table, 'id', key_value)
        return UserModel(item)
