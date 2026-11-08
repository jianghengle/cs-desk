from .model import Model
from ..services import dynamo_service
from ..errors import MyError

class TicketModel(Model):
    TableName = 'CsTickets'
    GSIs = {
        'statusGSI': 'status',
    }
    Fields = [
        ('id', 'str'),
        ('status', 'enum', ['Open', 'Waiting on Customer', 'Waiting on Internal', 'Done']),
        ('inbox', 'str'),
        ('subject', 'str'),
        ('message', 'text'),
        ('customerId', 'str'),
        ('customerWaiting', 'int'),
        ('customerMood', 'str'),
        ('category', 'str'),
        ('ownerId', 'str'),
        ('comments', 'list'),
        ('createdAt', 'timestamp', 'auto-create'),
        ('updatedAt', 'timestamp', 'auto-update'),
    ]
