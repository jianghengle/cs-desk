from .model import Model
from ..services import dynamo_service
from ..errors import MyError

class CommentModel(Model):
    TableName = 'CsComments'
    GSIs = {
        'ticketIdGSI': 'ticketId',
    }
    Fields = [
        ('id', 'str'),
        ('ticketId', 'str'),
        ('ownerId', 'str'),
        ('fromCustomer', 'bool'),
        ('sentEmail', 'bool'),
        ('text', 'text'),
        ('attachments', 'list'),
        ('createdAt', 'timestamp', 'auto-create'),
        ('updatedAt', 'timestamp', 'auto-update'),
    ]
