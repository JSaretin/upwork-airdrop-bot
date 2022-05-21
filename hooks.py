from os import environ
from structure import *
from telebot import types
from utils import get_db

ADMIN_ID= 3454432

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
            

async def fetch_user(message: FormatedData):
    db_connection = get_db()
    query = db_connection.fetch({'user_id': message.chat_id})
    user = User(**(query.items[0] if query.count > 0 else {'user_id': message.chat_id, 
                        'first_name': message.first_name, 
                        'last_name': message.last_name,
                        'username': message.username,
                        'language_code': message.language_code
                        }))
    if not user.key:
        user_dict =user.dict()
        user_dict.pop('key')
        
        new_user = db_connection.put(user_dict)
        user.key = new_user['key']
    return (user, db_connection)

def user_in_group_and_channel(func):
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return result
    return wrapper

def get_airdrop_config(func):
    async def wrapper(*args, **kwargs):
        db = get_db('airdrop_config')
        query = db.fetch()
        if not query.count:
            airdrop_config = AirdropConfig(**{'airdrop_enabled': False})
            airdrop_config_dict = airdrop_config.dict()
            airdrop_config_dict.pop('key')
            saved_config = db.put(airdrop_config_dict)
            airdrop_config.key = saved_config['key']
        else:
            airdrop_config = AirdropConfig(**query.items[0])
            
        kwargs['airdrop_config'] = airdrop_config
        result = await func(*args, **kwargs)
        return result
    return wrapper

def get_current_user(func):
    async def wrapper(*args, **kwargs):
        message: FormatedData = args[0]
        user = kwargs.get('user')
        if not user:
            user, db = await fetch_user(message)
            kwargs.update({'user': user, 'user_db': db})
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


def try_run(func):
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return result
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            print(e)
            # if environ.get('FOWARD_ERRORS_TO_ADMIN'):
            #     await args[0].bot.send_message(ADMIN_ID, str(e))
        else:
            return result
    return wrapper



        