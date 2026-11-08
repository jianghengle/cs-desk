from .model import Model
from ..services import dynamo_service
from ..errors import MyError

class CustomerModel(Model):
    TableName = 'CsCustomers'
    GSIs = {
        'emailGSI': 'email',
    }
    Fields = [
        ('id', 'str'),
        ('email', 'email', 'readonly'),
        ('phone', 'str'),
        ('name', 'str'),
        ('info', 'text'),
        ('createdAt', 'timestamp', 'auto-create'),
        ('updatedAt', 'timestamp', 'auto-update'),
    ]
