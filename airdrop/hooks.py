from airdrop import (AirdropConfig, AirdropConfigMessageIDS, FormatedData,
                     MessageIds, User, delete_message, get_db,
                     send_message, types, bot, asyncio, Tuple)


def try_run(func):
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
        # try:
        #     result = await func(*args, **kwargs)
        # except Exception as e:
        #     print(func.__name__, e)
        #     # if environ.get('FOWARD_ERRORS_TO_ADMIN'):
        #     #     await args[0].bot.send_message(ADMIN_ID, str(e))
        # else:
        #     return result
    return wrapper




def permission(allowed_perm: Tuple = ('captcha', 'accept_terms', 'address', 'email', 'twitter')):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            message: FormatedData = args[0]
            user : User = kwargs['user']
            perms = {
                'captcha':  not user.is_bot,
                'accept_terms':  user.accepted_terms,
                'address':  user.address,
                'email':  user.email,
                'twitter':  user.twitter_username,
                'admin':  user.is_admin,
                'complete':  user.registration_complete,
            }
            
            failed_perms = list(filter(lambda perm: not perms.get(perm),  allowed_perm))
            if len(failed_perms) > 0:
                asyncio.create_task(delete_message(message.chat_id, message.id))
                return await start(message, **kwargs)
                pass
    
            result = await func(*args, **kwargs)
            return result
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

 

def get_airdrop_config(func):
    async def wrapper(*args, **kwargs):
        airdrop_config = kwargs.get('airdrop_config')
        if not airdrop_config:
            db = get_db('airdrop_config')
            query = db.fetch()
            if not query.count:
                airdrop_config = AirdropConfig(**{'airdrop_enabled': False})
                airdrop_config_obj = airdrop_config.dict()
                airdrop_config_obj.pop('key')
                saved_config = db.put(airdrop_config_obj)
                airdrop_config.key = saved_config['key']
            else:
                airdrop_config = AirdropConfig(**query.items[0])
            kwargs.update({'airdrop_config': airdrop_config, 'airdrop_config_db': db})
        return await func(*args, **kwargs)
    return wrapper


def get_current_user(load_config=False):
    def decorator(func):
        @format_data
        @get_airdrop_config
        async def wrapper(*args, **kwargs):
            message: FormatedData = args[0]
            status = await check_group_and_channel(message, kwargs['airdrop_config'])
            if status['group_status'] < 0:
                return await send_message(message.chat_id, 'You are banned from this group')
            if status['channel_status'] < 0:
                return await send_message(message.chat_id, 'You are banned from this channel')
            is_admin = status['is_admin']
            if not is_admin:
                kwargs = await get_user(message, **kwargs)
                user: User = kwargs.get('user')
                user_obj = user.dict()
                user_obj.update(status)
                user = User(**user_obj)
                kwargs.update({'user': user})
            else:
                kwargs['user'] = User(user_id=message.chat_id, first_name='admin', is_admin=True)
                if load_config:
                    kwargs = await get_airdrop_config_message_ids(**kwargs)
                
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator



def get_validation_ids(func):
    async def wrapper(*args, **kwargs):
        message_ids = kwargs.get('message_ids')
        if not message_ids:
            user: User = kwargs['user']
            db = get_db('message_ids')
            query = db.fetch({'user_id': user.key})
            if query.count:
                message_ids = MessageIds(**query.items[0])
            else:
                message_ids = MessageIds(**{'user_id': user.key})
                message_ids_obj = message_ids.dict()
                message_ids_obj.pop('key')
                saved_config = db.put(message_ids_obj)
                message_ids.key = saved_config['key']
            kwargs['message_ids'] = message_ids
            kwargs['message_ids_db'] = db
        result = await func(*args, **kwargs)
        return result
    return wrapper





