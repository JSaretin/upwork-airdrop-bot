
from telebot import types

from bot import bot
from bot.structure import *
from bot.utils import *


def format_data(func):
    async def wrapper(*args, **kwargs):
        message = args[0]
        if type(message) == types.CallbackQuery:
            reply_to = (message.message.message_id or 
                        message.message.reply_to_message.message_id if 
                                                    message.message else None)
            data = {
                'id': message.id,
                'user_id': message.from_user.id,
                'msg_type': 'callback',
                'msg_text': message.data,
                'reply_to_msg_id': reply_to,
                'language_code': message.from_user.language_code,
                'chat_type': message.message.chat.type,
                'chat_id': message.message.chat.id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'content_type': message.message.content_type,
                'replied_message_text': message.message.text
            }
        elif type(message) == types.Message:
            data = {
                'id': message.message_id,
                'user_id': message.from_user.id,
                'msg_type': 'message',
                'msg_text': message.text,
                'reply_to_msg_id': (message.reply_to_message.id if 
                                    message.reply_to_message else None),
                'language_code': message.from_user.language_code,
                'chat_type': message.chat.type,
                'chat_id': message.chat.id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'content_type': message.content_type,
                'replied_message_text': message.reply_to_message.text if 
                                                    message.reply_to_message else None
            }
        else:
            data: FormatedData = message.dict()
            
        formated_data = FormatedData(**data)
        result = await func(formated_data, **kwargs)
        return result
    return wrapper
            

async def get_user(message, **kwargs):
    user = kwargs.get('user')
    if not user:
        db_connection = get_db()
        query = db_connection.fetch({'user_id': message.chat_id})
        if query.count:
            user = User(**query.items[0])
        else:
            user = User(**(query.items[0] if query.count > 0 else {'user_id': message.chat_id, 
                        'first_name': message.first_name, 
                        'last_name': message.last_name,
                        'username': message.username,
                        'language_code': message.language_code
                        }))
            user_dict = user.dict()
            user_dict.pop('key')
            saved_user = db_connection.put(user_dict)
            user.key = saved_user['key']
        kwargs['user'] = user
    return kwargs
    


async def fetch_airdrop_config(db):
    query = db.fetch()
    if not query.count:
        airdrop_config = AirdropConfig(**{'airdrop_enabled': False})
        
        airdrop_config_dict = airdrop_config.dict()
        airdrop_config_dict.pop('key')
        saved_config = db.put(airdrop_config_dict)
        airdrop_config.key = saved_config['key']
    else:
        airdrop_config = AirdropConfig(**query.items[0])
    return airdrop_config



async def check_group_and_channel(message: FormatedData, airdrop_config: AirdropConfig):
    perms = {'member': 1, 'administrator': 2,  'creator': 2, 'banned_user': -1}  
    
    user_in_group = (await bot.get_chat_member(airdrop_config.group_username, message.chat_id)).status
    user_in_channel = (await bot.get_chat_member(airdrop_config.channel_username, message.chat_id)).status
    
    group_status = perms.get(user_in_group, 0)
    channel_status = perms.get(user_in_channel, 0)
    
    return {
        'group_status': group_status,
        'channel_status': channel_status,
        'is_admin': (group_status >= 2) or (channel_status >= 2)
    }

async def get_airdrop_config_message_ids(**kwargs):
    airdrop_config_message_ids = kwargs.get('airdrop_config_message_ids')
    if not airdrop_config_message_ids:
        db = get_db('airdrop_config_message_ids')
        query = db.fetch()
        if query.count:
            airdrop_config_message_ids = AirdropConfigMessageIDS(**query.items[0])
        else:
            airdrop_config_message_ids = AirdropConfigMessageIDS()
            airdrop_config_message_ids_dict = airdrop_config_message_ids.dict()
            airdrop_config_message_ids_dict.pop('key')
            saved_config = db.put(airdrop_config_message_ids_dict)
            airdrop_config_message_ids.key = saved_config['key']
        kwargs['airdrop_config_message_ids'] = airdrop_config_message_ids
        kwargs['airdrop_config_message_ids_db'] = db
    return kwargs

        
    return []

def get_airdrop_config(func):
    async def wrapper(*args, **kwargs):
        airdrop_config = kwargs.get('airdrop_config')
        if not airdrop_config:
            db = get_db('airdrop_config')
            airdrop_config = await fetch_airdrop_config(db)
            kwargs['airdrop_config'] = airdrop_config
            kwargs['airdrop_config_db'] = db
        result = await func(*args, **kwargs)
        return result
    return wrapper


def get_current_user(func):
    @format_data
    @get_airdrop_config
    async def wrapper(*args, **kwargs):
        message: FormatedData = args[0]
        status = await check_group_and_channel(message, kwargs['airdrop_config'])
        if status['group_status'] < 0:
            return await send_message(message.chat_id, 'You are banned from this group')
        if status['channel_status'] < 0:
            return await send_message(message.chat_id, 'You are banned from this channel')
        if not status['is_admin']:
            kwargs = await get_user(message, **kwargs)
            user: User = kwargs.get('user')
            user_obj = user.dict()
            user_obj.update(status)
            user = User(**user_obj)
            kwargs = await get_airdrop_config_message_ids(**kwargs)
        result = await func(*args, **kwargs)
        return result
    return wrapper



def get_validation_ids(func):
    async def wrapper(*args, **kwargs):
        user: User = kwargs['user']
        db = get_db('message_ids')
        query = db.fetch({'user_id': user.key})
        message_ids = MessageIds(**(query.items[0] if query.count > 0 else {'user_id': user.key}))
        kwargs.update({'message_ids': message_ids, 'message_ids_db': db})
        result = await func(*args, **kwargs)
        return result
    return wrapper





