import uuid
from ..services import dynamo_service
from ..errors import MyError


class Model:
    def __init__(self, data={}):
        self.data = {}
        for field in self.Fields:
            field_name = field[0]
            value = data.get(field_name, None)
            self.data[field_name] = value
            setattr(self, field_name, value)

    @classmethod
    def get(cls, key_value):
        table = dynamo_service.get_table(cls.TableName)
        key_field = cls.Fields[0][0]
        item = dynamo_service.get_item(table, key_field, key_value)
        if item:
            return cls(item)
        return None

    @classmethod
    def get_by_index(cls, index_name, index_value):
        table = dynamo_service.get_table(cls.TableName)
        index_key = cls.GSIs[index_name]
        if index_key is None:
            raise MyError('No such index ' + index_name)
        result = dynamo_service.query(table, index_name, index_key, index_value)
        if not len(result.get('items')):
            return None
        return cls(result.get('items')[0])

    @classmethod
    def query(cls, index_name, index_value, asc=True, limit=None, start_key=None):
        table = dynamo_service.get_table(cls.TableName)
        index_key = cls.GSIs.get(index_name)
        if index_key is None:
            raise MyError('No such index ' + index_name)
        result = dynamo_service.query(table, index_name, index_key, index_value, asc=asc, limit=limit, start_key=start_key)
        items = [cls(i) for i in result.get('items')]
        return {
            'items': items,
            'lastKey': result.get('lastKey'),
        }

    @classmethod
    def scan(cls, limit=None, start_key=None):
        table = dynamo_service.get_table(cls.TableName)
        result = dynamo_service.scan(table, limit=limit, start_key=start_key)
        items = [cls(i) for i in result.get('items')]
        return {
            'items': items,
            'lastKey': result.get('lastKey'),
        }

    @classmethod
    def create(cls, data):
        table = dynamo_service.get_table(cls.TableName)
        key_field = cls.Fields[0][0]
        key_value = data.get(key_field)
        if not key_value:
            data[key_field] = str(uuid.uuid4())
        item = cls(data)
        dynamo_service.create_item(table, item.data, key_field)
        return item

    @classmethod
    def update(cls, key_value, updates):
        table = dynamo_service.get_table(cls.TableName)
        key_field = cls.Fields[0][0]
        data = {}
        for field in cls.Fields[1:]:
            field_name = field[0]
            if field_name in updates:
                data[field_name] = updates[field_name]
        dynamo_service.update_item(table, key_field, key_value, data)
        item = dynamo_service.get_item(table, key_field, key_value)
        return cls(item)

    @classmethod
    def delete(cls, key_value):
        table = dynamo_service.get_table(cls.TableName)
        key_field = cls.Fields[0][0]
        dynamo_service.delete_item(table, key_field, key_value)
