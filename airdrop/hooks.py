import asyncio
from typing import Tuple

from telebot import types

from airdrop import bot
from airdrop.structure import (AirdropConfig, AirdropLangUpdateID,
                               FormatedData, MessageIds, User)
from airdrop.utils import create_airdrop_config, delete_message, fetch_user_conf, get_db, send_message, replace_text_with_config


async def send_invalid(message: FormatedData, **kwargs):
    from airdrop.user import handle_invalid_message
    return await handle_invalid_message(message, **kwargs)

def try_run(func):
    async def wrapper(*args, **kwargs):
        # return await func(*args, **kwargs)
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            pass
        else:
            return result
    return wrapper




def permission(allowed_perm: Tuple = ('verified', 
                                      'accept_terms', 
                                      'address', 'email', 
                                      'twitter'), callback=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            message: FormatedData = args[0]
            user : User = kwargs['user']
            perms = {
                'verified': user.is_bot == False,
                'accept_terms':  user.accepted_terms,
                'address':  user.address,
                'email':  user.email,
                'twitter':  user.twitter_username,
                'retweet': user.retweeted,
                'admin':  (user.is_admin or (user.group_status == 3) or( user.channel_status == 3)),
                'complete':  user.registration_complete, 
                'group': user.group_status >= 1,
                'channel': user.channel_status >= 1              
            }
            
            results = []
            for perm in allowed_perm:
                if perm.startswith('!'):
                    perm = perm[1:]
                    results.append(not perms.get(perm, False))
                else:
                    results.append(perms.get(perm, False))
            if all(results):
                return await func(*args, **kwargs)
            if callback:
                return await callback(*args, **kwargs)
            return await send_invalid(message, **kwargs)
        return wrapper
    return decorator



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
            data = message.dict()
            
        formated_data = FormatedData(**data)
        if formated_data.chat_type != 'private':
            return 
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
        kwargs.update({'user':user, 'user_db': db_connection}) 
    return kwargs
    


async def check_group_and_channel(message: FormatedData, airdrop_config: AirdropConfig):
    perms = {'member': 1, 'administrator': 2,  'creator': 3, 'restricted': -1, 'kicked': -1}  
    
    user_in_group = (await bot.get_chat_member(airdrop_config.group_username, message.chat_id)).status
    user_in_channel = (await bot.get_chat_member(airdrop_config.channel_username, message.chat_id)).status
    
    group_status = perms.get(user_in_group, 0)
    channel_status = perms.get(user_in_channel, 0)
    
    return {
        'group_status': group_status,
        'channel_status': channel_status,
    }


def get_airdrop_config(func):
    async def wrapper(*args, **kwargs):
        user: User = kwargs.get('user')
        if not user:
            kwargs['airdrop_config'] = await fetch_user_conf()    
        else:
            kwargs['airdrop_config'] = await fetch_user_conf(user.language_code)    
        return await func(*args, **kwargs)
    return wrapper


def get_current_user(load_config=False):
    def decorator(func):
        @format_data
        @get_airdrop_config
        async def wrapper(*args, **kwargs):
            message: FormatedData = args[0]
            status = await check_group_and_channel(message, kwargs['airdrop_config'])
            airdrop_config: AirdropConfig = kwargs['airdrop_config']
            if status['group_status'] < 0:
                return await send_message(message.chat_id, airdrop_config.ban_from_group_msg)
            if status['channel_status'] < 0:
                return await send_message(message.chat_id, airdrop_config.ban_from_channel_msg)
        
            kwargs = await get_user(message, **kwargs)
            user: User = kwargs.get('user')
            is_admin = ((status['group_status'] == 3) or (status['channel_status'] == 3) or user.is_admin)
            if not is_admin:
                user_obj = user.dict()
                user_obj.update(status)
                user = User(**user_obj)
                air_config = kwargs.get('airdrop_config')
                kwargs.update({'user': user})
                
                config_dict = air_config.dict()
                for key, value in config_dict.items():
                    if type(value) == str: config_dict[key] = replace_text_with_config(value, air_config, user)
                air_config = AirdropConfig(**config_dict)

                if not air_config.airdrop_status:
                    return await send_message(message.chat_id, air_config.airdrop_closed_message);
                kwargs['airdrop_config'] = air_config
                
            else:
                user.is_admin = True
                kwargs['user'] = user
                if load_config:
                    pass
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator



def get_validation_ids(func):
    async def wrapper(*args, **kwargs):
        # message: FormatedData = args[0]
        message_ids = kwargs.get('message_ids')
        if not message_ids:
            user: User = kwargs['user']
            db = get_db('message_ids')
            query = db.fetch({'user_id': user.key})
            if query.count:
                message_ids = MessageIds(**query.items[0])
            else:
                message_ids = MessageIds(user_id=user.key)
                message_ids_obj = message_ids.dict()
                message_ids_obj.pop('key')
                saved_config = db.put(message_ids_obj)
                message_ids.key = saved_config['key']
            kwargs['message_ids'] = message_ids
            kwargs['message_ids_db'] = db
        result = await func(*args, **kwargs)
        return result
    return wrapper





