import json
import os
from decimal import Decimal

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError

from ..my_http import MyError, admin_required
from ..models.user_model import UserModel
from ..services import dynamo_service

# Claude Sonnet 4.5 via the US cross-region inference profile. Override with
# the BEDROCK_MODEL_ID env var (e.g. to switch models) without a code change.
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
BEDROCK_REGION = os.environ.get('BEDROCK_REGION') or os.environ.get('AWS_REGION') or 'us-west-2'
BEDROCK_MAX_TOKENS = 4096

_bedrock_client = None

AdminModels = [
    ('user', UserModel),
]

def get_model_class(model_name):
    for model in AdminModels:
        if model[0] == model_name:
            return model[1]
    raise MyError('No such model: ' + model_name, 404)

@admin_required
def get_admin_tables(req):
    tables = []
    for model in AdminModels:
        table = dynamo_service.get_table(model[1].TableName)
        table.reload()
        tables.append({
            'modelName': model[0],
            'tableName': model[1].TableName,
            'indexes': model[1].GSIs,
            'fields': model[1].Fields,
            'metadata': {
                'arn': table.table_arn,
                'itemCount': table.item_count,
                'creationDateTime': table.creation_date_time.timestamp(),
            },
        })
    return tables

@admin_required
def get_admin_table(req, model_name):
    for model in AdminModels:
        if model[0] == model_name:
            table = dynamo_service.get_table(model[1].TableName)
            table.reload()
            return {
                'modelName': model[0],
                'tableName': model[1].TableName,
                'indexes': model[1].GSIs,
                'fields': model[1].Fields,
                'metadata': {
                    'arn': table.table_arn,
                    'itemCount': table.item_count,
                    'creationDateTime': table.creation_date_time.timestamp(),
                },
            }
    raise MyError('Cannot find table: ' + model_name, 400)

@admin_required
def get_item(req, model_name, id):
    ModelClass = get_model_class(model_name)
    item = ModelClass.get(id)
    if item is None:
        raise MyError('Item not found: ' + model_name + ' ' + id, 404)
    return item.data

@admin_required
def query_items(req, model_name):
    ModelClass = get_model_class(model_name)
    data = req.body
    index_name = data.get('indexName')
    index_value = data.get('indexValue')
    asc = data.get('asc', True)
    limit = data.get('limit')
    start_key = data.get('startKey')
    result = ModelClass.query(index_name, index_value, asc=asc, limit=limit, start_key=start_key)
    result['items'] = [i.data for i in result['items']]
    return result

@admin_required
def scan_items(req, model_name):
    ModelClass = get_model_class(model_name)
    data = req.body
    result = ModelClass.scan(limit=data.get('limit'), start_key=data.get('startKey'))
    result['items'] = [i.data for i in result['items']]
    return result

@admin_required
def create_item(req, model_name):
    ModelClass = get_model_class(model_name)
    item = ModelClass.create(req.body)
    return item.data

@admin_required
def update_item(req, model_name, id):
    ModelClass = get_model_class(model_name)
    item = ModelClass.update(id, req.body)
    return item.data

@admin_required
def delete_item(req, model_name, id):
    ModelClass = get_model_class(model_name)
    ModelClass.delete(id)
    return {'ok': True}

def _get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=BEDROCK_REGION,
            # API Gateway cuts requests off at 29s, so fail before that and
            # don't retry (a retry would always exceed it).
            config=Config(connect_timeout=3, read_timeout=26, retries={'total_max_attempts': 1}),
        )
    return _bedrock_client


def _json_default(value):
    # req.body is parsed with parse_float=Decimal, so numbers in messages
    # (e.g. tool inputs) arrive as Decimal, which json can't serialize.
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError('Not JSON serializable: ' + type(value).__name__)


# Bedrock error code -> HTTP status returned to the browser.
_BEDROCK_ERROR_STATUS = {
    'ValidationException': 400,
    'ThrottlingException': 429,
    'ServiceQuotaExceededException': 429,
    'ModelTimeoutException': 504,
}


@admin_required
def call_bedrock_llm(req):
    """Proxy one Anthropic Messages API turn to Claude on Bedrock (InvokeModel).

    Body: {"messages": [...], "system": "..." (optional), "tools": [...] (optional),
           "max_tokens": N (optional, capped at BEDROCK_MAX_TOKENS)}
    Returns Bedrock's response unchanged (id, content, stop_reason, usage, ...),
    which is the same shape as api.anthropic.com/v1/messages.
    The model is fixed server-side; clients can't choose it.
    """
    data = req.body if isinstance(req.body, dict) else None
    if data is None:
        raise MyError('Request body must be a JSON object', 400)

    messages = data.get('messages')
    if not isinstance(messages, list) or not messages:
        raise MyError('messages must be a non-empty list', 400)

    payload = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': BEDROCK_MAX_TOKENS,
        'messages': messages,
    }

    system = data.get('system')
    if system is not None:
        if not isinstance(system, (str, list)):
            raise MyError('system must be a string or a list of content blocks', 400)
        payload['system'] = system

    tools = data.get('tools')
    if tools is not None:
        if not isinstance(tools, list):
            raise MyError('tools must be a list', 400)
        if tools:
            payload['tools'] = tools

    max_tokens = data.get('max_tokens')
    if max_tokens is not None:
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, (int, Decimal)) or max_tokens < 1:
            raise MyError('max_tokens must be a positive integer', 400)
        payload['max_tokens'] = min(int(max_tokens), BEDROCK_MAX_TOKENS)

    try:
        resp = _get_bedrock_client().invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(payload, default=_json_default),
        )
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', 'Unknown')
        message = e.response.get('Error', {}).get('Message', '')
        print('Bedrock error: %s: %s' % (code, message))
        raise MyError('Bedrock %s: %s' % (code, message), _BEDROCK_ERROR_STATUS.get(code, 502))
    except (ReadTimeoutError, ConnectTimeoutError):
        raise MyError('Bedrock request timed out; try a shorter or more specific question', 504)

    return json.loads(resp['body'].read())

AdminRoutes = [
    ('GET', '/api/admin/get-tables', get_admin_tables),
    ('GET', '/api/admin/get-table/:model_name', get_admin_table),
    ('GET', '/api/admin/:model_name/get-item/:id', get_item),
    ('POST', '/api/admin/:model_name/query-items', query_items),
    ('POST', '/api/admin/:model_name/scan-items', scan_items),
    ('POST', '/api/admin/:model_name/create-item', create_item),
    ('POST', '/api/admin/:model_name/update-item/:id', update_item),
    ('POST', '/api/admin/:model_name/delete-item/:id', delete_item),
    ('POST', '/api/admin/call-bedrock-llm', call_bedrock_llm),
]
