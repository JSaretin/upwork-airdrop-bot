from structure import *

async def update_db_object(item_to_update: (MessageIds or User or AirdropConfig), db_connection):
    item_to_update_obj = item_to_update.dict()
    item_to_update_obj.pop('key')
    db_connection.update(item_to_update_obj, item_to_update.key)