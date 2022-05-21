import asyncio
import random
from os import environ
from typing import Dict, List, Tuple

from telebot.async_telebot import AsyncTeleBot as TeleBot
from telebot.async_telebot import types

from background_task import *
from hooks import *
from structure import *

bot = TeleBot(environ['BOT_TOKEN'])

# BOT DEPENDENT HOOKS STARTS HERE
# def show_progress_flash(show_progress=True):
#     def wrapper(func):
#         def wrapper(*args, **kwargs):
#             message: FormatedData = args[0]
            
#             if not show_progress:
#                 return func(*args, **kwargs)
#             try:

#                 bot.send_chat_action(message.chat_id, 'typing')
#             except Exception as e:
#                 pass
                
#             result = func(*args, **kwargs)
            
#             if flash_msg:
#                 try:
#                     bot.await delete_message(message.chat_id, flash_msg.message_id)
#                 except Exception as e:
#                     pass
                
#             return result
#         return wrapper
#     return wrapper
                    

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
    
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator



# BOT DEPENDENT HOOKS ENDS HERE

# BOT GLOBAL UTILS STARTS HERE

@try_run
async def send_message(to_object: (FormatedData or int),
                       text, reply_to_message_id=None, parse_mode=None, 
                       disable_web_page_preview=None, disable_notification=None, 
                       reply_markup=None):
    
    user_id = to_object.user_id if type(to_object) == FormatedData else to_object
    
    return await bot.send_message(user_id, text, reply_to_message_id=reply_to_message_id, 
                                      parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview, 
                                      disable_notification=disable_notification, reply_markup=reply_markup)
    

@try_run
@get_airdrop_config
async def check_group_and_channel(message: FormatedData, **kwargs) -> InGroupCannellStatus:
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    
    perms = ('member', 'administrator', 'creator')
    user_in_group = (await bot.get_chat_member(airdrop_config.group_username, message.chat_id)).status in perms
    user_in_channel = (await bot.get_chat_member(airdrop_config.channel_username, message.chat_id)).status in perms
    return InGroupCannellStatus(in_group=user_in_group, 
                                in_channel=user_in_channel)
    
@try_run
async def delete_message(user_id, msg_ids: (List[int] or int or FormatedData)):
    msg_ids = [msg_ids] if type(msg_ids) == int else [msg_ids.id] if type(msg_ids) == FormatedData else msg_ids
    await asyncio.gather(*[bot.delete_message(user_id, msg_id) for msg_id in msg_ids])
    
    
@try_run
async def run_get_users_stats(message: FormatedData, user_db, wait_message_id: int):
    query = user_db.fetch()   
    users = query.items
    while query.last:
        query = user_db.fetch(last=query.last)
        users += query.items
    
    register_counts = len(users)
    addesss_submited = len(list(filter(lambda x: User(**x).address, users)))
    email_submited = len(list(filter(lambda x: User(**x).email, users)))
    submited_twitter_link = len(list(filter(lambda x: User(**x).twitter_username, users)))
    # retweeted = len(list(filter(lambda x: User(**x).retweeted, users)))
    
    formated_message = f'*Users stats*\n\n'\
    f'*Registered users:* {register_counts}\n'\
    f'*Submited address:* {addesss_submited}\n'\
    f'*Submited email:* {email_submited}\n'\
    f'*Submited twitter link:* {submited_twitter_link}\n'\
    # f'*Retweeted:* {retweeted}\n'
    asyncio.create_task(delete_message(message.chat_id, wait_message_id))
    await send_message(message.chat_id, formated_message, parse_mode='Markdown') 
    
# BOT GLOBAL UTILS ENDS HERE


# TASK HANDLERS STARTS HERE
@try_run
@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms', 'address', 'email', 'twitter', 'complete'))
@get_airdrop_config
async def dashboard(message: FormatedData, **kwargs):
    '''
    This function shows the user dashboard
    '''
    # user: User = kwargs['user']
    # if not user.registration_complete:
    #     # run the start function again
    #     await start(message)
    #     return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    buttons = [
        'Wallet Address',
        'Email',
        'Referral Link',
        'My Referrals',
        'Balance',
        'Rules',
        'Withdraw',
    ]

    buttons = [types.KeyboardButton(button) for button in buttons]
    markup.add(*buttons)

    await send_message(message, 'Your dashboard', reply_markup=markup)


@try_run
@get_current_user
@get_validation_ids
# @get_airdrop_config
async def request_twitter_user_link(message: FormatedData, **kwargs):
    '''
    Request user twitter link
    '''
    # user: User = kwargs['user']
    message_ids: MessageIds = kwargs['message_ids']
    # airdrop_config: AirdropConfig = kwargs['airdrop_config']

    if message_ids.twitter_username_request_msg_id: asyncio.create_task(delete_message(message.chat_id, 
                                                                message_ids.twitter_username_request_msg_id))
    send_mst = await send_message(message, 'Please send your twitter profile link', reply_markup=types.ForceReply())
    message_ids.twitter_username_request_msg_id = send_mst.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_db']))



@try_run
@get_current_user
@get_validation_ids
@get_airdrop_config
async def request_email(message: FormatedData, **kwargs):
    '''
    This function send the user a request to submit his/her email
    '''
    user: User = kwargs['user']
    if user.email:
        asyncio.create_task(send_message(message.chat_id, 'Your email is: ' + user.email))
        return


    message_ids: MessageIds = kwargs['message_ids']
    message_ids_db = kwargs['message_ids_db']

    if message_ids.email_request_msg_id: asyncio.create_task(delete_message(message.chat_id, [message_ids.email_request_msg_id]))


    sent_msg = await send_message(message, 'Please, send me your email', reply_markup=types.ForceReply())
    message_ids.email_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, message_ids_db))


@try_run
@get_current_user
@get_validation_ids
@get_airdrop_config
async def request_wallet_address(message: FormatedData, **kwargs):
    '''
    This function requests the user wallet address
    '''
    user : User = kwargs['user']
    if user.address:
        asyncio.create_task(send_message(message, 'Your wallet address is: ' + user.address))
        return
    
    message_ids: MessageIds = kwargs['message_ids']
    message_ids_db = kwargs['message_ids_db']

    if message_ids.address_request_msg_id: asyncio.create_task(delete_message(message.chat_id, [message_ids.address_request_msg_id]))

    sent_msg = await send_message(message, 'Please, send me your Polygon address', reply_markup=types.ForceReply())

    message_ids.address_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, message_ids_db))
    


@try_run
async def request_to_join_channel(message: FormatedData):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Channel', url=f'https://t.me/{airdrop_config.channel_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_channel'))
    await send_message(message, 'Please, join the channel', reply_markup=markup)
    


@try_run
@get_airdrop_config
async def request_to_join_group(message: FormatedData, **kwargs):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Group', url=f'https://t.me/{airdrop_config.group_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_group'))
    await send_message(message, 'Please, join the group', reply_markup=markup)
    


@try_run
@get_airdrop_config
async def send_welcome_message(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Understood', callback_data='accept_terms'))
    await send_message(message, airdrop_config.welcome_message, reply_markup=markup)


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


@try_run
@get_airdrop_config
@get_current_user
async def send_captcha_message(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    
    verification_code = f'{random.randint(1, 10)} {random.choice(["+", "-", "x"])} {random.randint(1, 10)}'
    verification_result = eval(verification_code.replace('x', '*'))
    user.verificatin_code = str(verification_result)
    
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
        
        
    # sent_msg = bot.send_photo(user.user_id, open('verification.png', 'rb'))
    cap_msg = await send_message(message.chat_id, verification_code)
    sent_msg = await send_message(message, 'Please, enter the result of the equation above:', 
                     reply_to_message_id=cap_msg.message_id, reply_markup=types.ForceReply())
    
    asyncio.create_task(save_validation_id(user, sent_msg))
    


@try_run
@format_data
@get_current_user
async def start(message, **kwargs):
    user: User = kwargs['user']
        
    if not user.key or user.is_bot:
        await send_captcha_message(message, **kwargs)
        return
    
    if not user.accepted_terms:
        await send_welcome_message(message, **kwargs)
        return
    
    group_and_channel: InGroupCannellStatus = await check_group_and_channel(message)
    
    if not group_and_channel.in_group:
        await request_to_join_group(message, **kwargs)
        return
    if not group_and_channel.in_channel:
        await request_to_join_channel(message, **kwargs)
        return
    
    if not user.address:
        await request_wallet_address(message, **kwargs)
        return
    
    if not user.email:
        await request_email(message, **kwargs)
        return
    
    await dashboard(message, **kwargs)

# TASK HANDLERS ENDS HERE 



# USER INPUT DATA HANDLERS BEGINS HERE
@try_run
@format_data
@get_current_user
@get_validation_ids
async def confirm_verification(message: FormatedData, **kwargs: Dict):
    user: User = kwargs['user']
    message_ids : MessageIds = kwargs['message_ids']
    if not user.is_bot:
        tasks = [
            send_invalid_message(message),
            delete_message(message.chat_id, [message.id])
        ]
        await asyncio.gather(*tasks)
        return
    if not message.reply_to_msg_id:
        asyncio.create_task(send_message(message, 'Invalid message: please reply to the verification picture'))
        return
    if message.reply_to_msg_id != message_ids.captcha_msg_id:
        asyncio.create_task(send_message(message, 'Invalid message: please reply to the verification picture'))
        return
    if message.msg_text != user.verificatin_code:
        tasks = [send_message(message, 'You have entered the wrong answer'),
        delete_message(message.chat_id, [message_ids.captcha_msg_id-1, message_ids.captcha_msg_id, message.id])]
        await asyncio.gather(*tasks)
        await start(message, **kwargs)
        return
    
    user.is_bot = False
    tasks = [
        send_message(message.chat_id, 'Your account has been verified'),
        update_db_object(user, kwargs['user_db'])
    ]
    
    await asyncio.gather(*tasks)
    await start(message, **kwargs)
    
    
# accept terms
@try_run
@format_data
@get_current_user
async def accept_terms_callback_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.accepted_terms:
        tasks = [
            delete_message(message.chat_id, [message.reply_to_msg_id]),
            send_invalid_message(message)
        ]
        asyncio.create_task(tasks)
        return
    user.accepted_terms = True
    tasks = [
            update_db_object(user, kwargs['user_db']),
            bot.edit_message_text(message.replied_message_text, message.chat_id, message.reply_to_msg_id),
            bot.answer_callback_query(message.id, 'Terms accepted')
            ]

    await asyncio.gather(*tasks)
    await start(message, **kwargs)

# handle user join group or channel

@bot.callback_query_handler(func=lambda call: call.data == 'joined_group')
@try_run
@format_data
async def check_user_in_group_handler(message: FormatedData):
    status = await check_group_and_channel(message)
    if not status.in_group:
        await bot.answer_callback_query(message.id, 'You are not in the group', show_alert=True)
        return
    asyncio.create_task(delete_message(message.chat_id, [message.reply_to_msg_id]))
    await check_user_in_channel_handler(message)
    return
    
    

@try_run
@format_data
async def check_user_in_channel_handler(message: FormatedData, **kwargs):
    status = await check_group_and_channel(message)
    if not status.in_channel:
        # show inline alert message

        await bot.answer_callback_query(message.id, 'You are not in the channel', show_alert=True)
        return
    await delete_message(message.chat_id, [message.reply_to_msg_id])
    await start(message, **kwargs)
    
    

@try_run
@format_data
@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms'))
@get_validation_ids
async def register_address_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    '''
    This function registers the user wallet address
    '''
    if user.address:
        await delete_message(message.chat_id, [message.id])

        await send_message(message, 'You have already registered your wallet address\nclick /remove_address to remove it')
        return
    
    if not message.reply_to_msg_id:
        asyncio.create_task(delete_message(message, [message.id]))
        await send_message(message, 'please, reply to the address request message or click /start to get the question again')
        return
    
    messages_ids : MessageIds = kwargs['message_ids']
    if message.reply_to_msg_id != messages_ids.address_request_msg_id:
        asyncio.create_task(delete_message(message, [message.id]))
        await send_message(message,'please, reply to the address request message or click /start to get the question again')
        return
    
    user_db = kwargs['user_db']
    address = message.msg_text.lower()
    query = user_db.fetch({'address': address})
    if query.count > 0:
        asyncio.create_task(send_message(message, 'This address is already registered by another user'))
        return
    
    user.address = address
    asyncio.create_task(update_db_object(user, user_db))

    # delete message and request message
    # await delete_message(message.chat_id, [messages_ids.address_request_msg_id, message.id])
    await send_message(message, 'Your wallet address has been registered', reply_to_message_id=message.id)
    await start(message, **kwargs)


@try_run
@format_data
@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms', 'address'))
@get_validation_ids
async def register_email_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.email:
        tasks = [
            send_message(message.chat_id, 'You have already registered your email\nclick /remove_email to remove it'),
            delete_message(message.chat_id, [message.id])]
        await asyncio.gather(*tasks)
        return
    if not message.reply_to_msg_id:
        tasks = [
            send_message(message.chat_id, 'please, reply to the email request message or click /start to get the question again'),
            delete_message(message.chat_id, [message.id])
        ]
        await asyncio.gather(*tasks)
        return
    messages_ids : MessageIds = kwargs['message_ids']
    
    if message.reply_to_msg_id != messages_ids.email_request_msg_id:
        tasks = [
            send_message(message.chat_id, 'please, reply to the email request message or click /start to get the question again'),
            delete_message(message.chat_id, [message.id])
        ]
        await asyncio.gather(*tasks) 
        return
    
    user_db = kwargs['user_db']
    email = message.msg_text.lower()
    query = user_db.fetch({'email': email})
    if query.count > 0 and query.items[0]['key'] != user.key:
        asyncio.create_task(send_message(message, 'This email is already registered to another account', reply_to_message_id=message.id))
        return

    user.email = email
    user_obj = user.dict()
    user_obj.pop('key')
    user_db.update(user_obj, user.key)
    # await delete_message(message.chat_id, [messages_ids.email_request_msg_id, message.id])
    await send_message(message.chat_id, 'Your email has been registered', reply_to_message_id=message.id)
    await start(message, **kwargs)
    



@try_run
@format_data
@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms', 'address', 'email'))
@get_validation_ids
async def twitter_link_submition_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.twitter_username: 
        asyncio.create_task(send_invalid_message(message))
        return
    messages_ids : MessageIds = kwargs['message_ids']
    if not message.reply_to_msg_id or message.reply_to_msg_id != messages_ids.twitter_request_msg_id:
        asyncio.create_task(send_message(message, 'please, reply to the twitter request message or click /start to get the question again'))
        return
    
    username = message.msg_text.lower().strip().replace('https://twitter.com/', '')
    user_db = kwargs['user_db']

    query = user_db.fetch({'twitter_username': username})
    if query.count > 0:
        asyncio.create_task(send_message(message, 'This twitter username is already registered by another user'))
        return
    
    user.twitter_username = username
    asyncio.create_task(update_db_object(user, user_db))
    
    await send_message(message, 'Your twitter username has been registered', reply_to_message_id=message.id)
    await start(message, **kwargs)
    


# USER INPUT DATA HANDLERS ENDS HERE

@try_run
@format_data
async def send_invalid_message(message):
    tasks = [delete_message(message.chat_id, [message.id]),
    send_message(message, 'Invalid message')]
    await asyncio.gather(*tasks)
    
    
        
@bot.message_handler(regexp='^users$')
@try_run
@format_data
@get_current_user
async def get_users_stats(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'processing....')
    asyncio.create_task(run_get_users_stats(message, kwargs['user_db'], sent_msg.id))
    
    
    

    

@bot.message_handler(regexp='^Update Twitter Post$')
@try_run
async def update_twitter_post(message):
    pass


async def run_update_welcome_message(sent_message: types.Message):
    pass

@bot.message_handler(regexp='^Update Welcome Message$')
@try_run
async def update_welcome_message(message):
    sent_msg = await send_message(message.chat_id, 'enter your new welcome message', reply_markup=types.ForceReply())
    asyncio.create_task(run_update_welcome_message(message, sent_msg.id))
    





# USER EVENT HANDLERS REGITER STATS HERE
bot.register_message_handler(start, commands=['start'])
bot.register_callback_query_handler(accept_terms_callback_handler, func=lambda call: call.data == 'accept_terms')
bot.register_message_handler(confirm_verification, regexp='^[0-9]+$')
bot.register_message_handler(register_address_handler, regexp='^0[xX][0-9a-fA-F]{40}$')
bot.register_message_handler(twitter_link_submition_handler, regexp='^https://twitter.com/[a-zA-Z0-9_]{3,30}$')
bot.register_message_handler(register_email_handler, regexp='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
bot.register_callback_query_handler(check_user_in_group_handler, func=lambda call: call.data == 'joined_group')
bot.register_callback_query_handler(check_user_in_channel_handler, func=lambda call: call.data == 'joined_channel')
bot.register_message_handler(send_invalid_message)
# USER EVENT HANDLERS ENDS HERE



# ADMIN EVENT HANDLERS STARTS HERE

# ADMIN EVNET HANDLERS ENDS HERE

if __name__ == '__main__':
    print('online')
    asyncio.run(bot.polling())
