import asyncio
from typing import List
from deta import Deta
from telebot import types
from os import environ
from airdrop import bot
from airdrop.structure import (AirdropConfig, AirdropLangConf, AirdropLangUpdateID, FormatedData, MessageIds, User, AirdropCoreConfig)



try:
    deta = Deta()
except:
    deta = Deta(environ['DETA_API_KEY'])
    



def get_db(table='users'):
    return deta.Base('airdrop_'+table.strip())

async def create_airdrop_config(lang='en'):
    db = get_db('airdrop_lang_config')
    airdrop_lang = AirdropLangConf(language_code=lang).dict()
    airdrop_lang.pop('key')
    conf = db.put(airdrop_lang)
    return AirdropLangConf(**conf)
 
 
async def get_airdrop_core_config():
    db = get_db('airdrop_core_config')
    query = db.fetch()
    if not query.count:
        air_core_config = AirdropCoreConfig()
        air_core_config_obj = air_core_config.dict()
        air_core_config_obj.pop('key')
        new_core = db.put(air_core_config_obj)
        air_core_config = AirdropCoreConfig(**new_core)
    else:
        air_core_config = AirdropCoreConfig(**query.items[0])
    return air_core_config

        
 
 
async def fetch_user_conf(lang='en', return_raw=False):
    db = get_db('airdrop_lang_config')
    airdrop_core = await get_airdrop_core_config()
    query = db.fetch({'language_code': lang})
    
    if query.count:
        lang_conf= AirdropLangConf(**query.items[0])
    else:
        lang_conf= await create_airdrop_config(lang)
    
    if not return_raw:
        lang_conf = lang_conf.dict()
        lang_conf.pop('key')
        airdrop_core = airdrop_core.dict()
        airdrop_core.pop('key')
        return AirdropConfig(**lang_conf, **airdrop_core)
    return(airdrop_core,lang_conf)
    
    
    
async def get_config_message_ids(lang='en'):
    db = get_db('airdrop_lang_config_message_ids')
    query = db.fetch({'language_code': lang})
    if not query.count:
        new_msg_ids = AirdropLangUpdateID(language_code=lang)
        new_msg_ids_obj = new_msg_ids.dict()
        new_msg_ids_obj.pop('key')
        saved_msg_ids = db.put(new_msg_ids_obj)
        lang_conf = AirdropLangUpdateID(**saved_msg_ids)
    else:
        lang_conf= AirdropLangUpdateID(**query.items[0])
    return lang_conf, db
    

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


async def exec_delete(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass



async def delete_message(user_id, msg_ids: (List[int] or int or FormatedData)):
    msg_ids = [msg_ids] if type(msg_ids) == int else [msg_ids.id] if type(msg_ids) == FormatedData else msg_ids
    await asyncio.gather(*[exec_delete(user_id, msg_id) for msg_id in msg_ids])
    
    

async def update_referral(user: User, airdrop_config: AirdropConfig,  user_db):
    query_referral = user_db.fetch({'referral_link': user.referral_code})
    if not query_referral.count:
        return
    refered_by = User(**query_referral.items[0])
    refered_by.referrals += 1
    refered_by.referral_balance += airdrop_config.referral_amount
    asyncio.create_task(update_db_object(refered_by, user_db))
    asyncio.create_task(send_message(refered_by.user_id, f'Congratulations!🎊 someone registered using your referral code\nYou have earned 50 tokens',disable_notification=True))


def replace_text_with_config(text: str, config: AirdropConfig, user: User): 
    to_replace = [
                
                ('{per_ref}', config.referral_amount),
                ('{reg_amount}}', config.registration_amount),
                ('{date}', config.withdraw_date),
                ('{tg_group}', config.group_username),
                ('{tg_channel}', config.channel_username),
                ('{min_ref}', config.min_referrals),
                ('{max_ref}', config.max_referrals),
                ('{extral}', config.extral_reward),
                ('{symbol}', config.symbol),
                ('{twitter}', config.twitter_link),
                ('{name}', config.name),
                ('{site}', config.website_link),
                ('{lang}', user.language_code),
                ('{bal}', user.balance),
                ('{ref_bal}', user.referral_balance),
                ('{ref_count}', user.referrals),
                ('{total_bal}', user.balance + user.referral_balance),
                ('{verified}', user.is_bot),
                ('{uid}', user.user_id),
            ]
    for to_replace_item in to_replace:
        text = text.replace(to_replace_item[0], str(to_replace_item[1]))
    return text



async def send_message(to_object: (FormatedData or int),
                       text, file=None,
                       reply_to_message_id=None, parse_mode=None, 
                       disable_web_page_preview=None, disable_notification=None, 
                       reply_markup=None):
    
    user_id = to_object.user_id if type(to_object) == FormatedData else to_object

    if file:
        return await bot.send_document(user_id, file, visible_file_name=text)
    
    return await bot.send_message(user_id, text, reply_to_message_id=reply_to_message_id, 
                                      parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview, 
                                      disable_notification=disable_notification, reply_markup=reply_markup)

