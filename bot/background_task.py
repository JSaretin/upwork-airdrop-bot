from bot.structure import *
from bot.utils import *

async def update_db_object(item_to_update: (MessageIds or User or AirdropConfig), db_connection):
    item_to_update_obj = item_to_update.dict()
    item_to_update_obj.pop('key')
    db_connection.update(item_to_update_obj, item_to_update.key)
    
async def save_validation_id(user: User, sent_msg: types.Message):
    validation_message_db = get_db('message_ids')
    validation_message_ids = MessageIds(user_id=user.key, captcha_msg_id=sent_msg.message_id)
    validation_message_ids_obj = validation_message_ids.dict()
    validation_message_ids_obj.pop('key')
    query = validation_message_db.fetch({'user_id': user.key})
    if not query.count:
        validation_message_db.insert(validation_message_ids_obj)
        return
    message_ids = MessageIds(**query.items[0])
    validation_message_db.update(validation_message_ids_obj, message_ids.key)