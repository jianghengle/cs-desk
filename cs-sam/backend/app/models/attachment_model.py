from .model import Model
from ..services import dynamo_service
from ..errors import MyError

class AttachmentModel(Model):
    TableName = 'CsAttachments'
    GSIs = {
        'commentIdGSI': 'commentId',
    }
    Fields = [
        ('id', 'str'),
        ('commentId', 'str'),
        ('ownerId', 'str'),
        ('filename', 'str'),
        ('bucket', 'str'),
        ('key', 'str'),
        ('createdAt', 'timestamp', 'auto-create'),
        ('updatedAt', 'timestamp', 'auto-update'),
    ]
