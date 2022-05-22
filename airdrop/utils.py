from airdrop import (AirdropConfig, Deta, FormatedData, List, MessageIds, User,
                     bot, environ, types, asyncio)

deta = Deta(environ['DETA_API_KEY'])




def get_db(table='users'):
    return deta.Base('airdrop_'+table.strip())


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





# @try_run
async def send_message(to_object: (FormatedData or int),
                       text, file=None,
                       reply_to_message_id=None, parse_mode=None, 
                       disable_web_page_preview=None, disable_notification=None, 
                       reply_markup=None):
    
    user_id = to_object.user_id if type(to_object) == FormatedData else to_object

    if file:
        return await bot.send_document(user_id, file)
    
    return await bot.send_message(user_id, text, reply_to_message_id=reply_to_message_id, 
                                      parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview, 
                                      disable_notification=disable_notification, reply_markup=reply_markup)



# @try_run
async def exec_delete(chat_id, message_id):
    await bot.delete_message(chat_id, message_id)




# @try_run
async def delete_message(user_id, msg_ids: (List[int] or int or FormatedData)):
    msg_ids = [msg_ids] if type(msg_ids) == int else [msg_ids.id] if type(msg_ids) == FormatedData else msg_ids
    await asyncio.gather(*[exec_delete(user_id, msg_id) for msg_id in msg_ids])
    
    

async def update_referral(referral_code, user_db):
    query_referral = user_db.fetch({'referral_code': referral_code})
    refered_by = User(**query_referral.items[0])
    refered_by.referrals += 1
    refered_by.referral_balance += 50
    asyncio.create_task(update_db_object(refered_by, user_db))
    asyncio.create_task(send_message(refered_by.chat_id, f'Congratulations!🎊 someone registered using your referral code\nYou have earned 50 tokens',disable_notification=True))