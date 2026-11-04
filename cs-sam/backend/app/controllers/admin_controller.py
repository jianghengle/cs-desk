from ..my_http import MyError, admin_required
from ..models.user_model import UserModel
from ..services import dynamo_service

AdminModels = [
    ('user', UserModel),
]

def get_model_class(model_name):
    for model in AdminModels:
        if model[0] == model_name:
            return model[1]
    raise MyError('No such model: ' + model_name)

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
    return item.data

@admin_required
def get_item(req, model_name, id):
    ModelClass = get_model_class(model_name)
    item = ModelClass.get(id)
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

AdminRoutes = [
    ('GET', '/api/admin/get-tables', get_admin_tables),
    ('GET', '/api/admin/get-table/:model_name', get_admin_table),
    ('GET', '/api/admin/:model_name/get-item/:id', get_item),
    ('POST', '/api/admin/:model_name/query-items', query_items),
    ('POST', '/api/admin/:model_name/scan-items', scan_items),
    ('POST', '/api/admin/:model_name/create-item', create_item),
    ('POST', '/api/admin/:model_name/update-item/:id', update_item),
    ('POST', '/api/admin/:model_name/delete-item/:id', delete_item),
]
