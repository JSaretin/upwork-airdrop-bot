import asyncio
import random
from typing import Dict, List, Tuple
from bot import bot
from telebot.async_telebot import types

from bot.background_task import *
from bot.hooks import *
from bot.structure import *
from bot.utils import *



# @Decorators.register_handler(lambda message: message.text == '🔍')

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

# @Decorators.register_handler(lambda message: message.text == '🔍')



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


async def send_welcome_message(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Understood', callback_data='accept_terms'))
    await send_message(message, airdrop_config.welcome_message, reply_markup=markup)



async def request_to_join_group(message: FormatedData, **kwargs):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Group', url=f'https://t.me/{airdrop_config.group_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_group'))
    await send_message(message, 'Please, join the group', reply_markup=markup)
    

async def request_to_join_channel(message: FormatedData):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Channel', url=f'https://t.me/{airdrop_config.channel_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_channel'))
    await send_message(message, 'Please, join the channel', reply_markup=markup)
    


@get_current_user
@get_validation_ids
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
    
    


@get_current_user
@get_validation_ids
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



@get_current_user
@get_validation_ids
async def request_twitter_user_link(message: FormatedData, **kwargs):
    '''
    Request user twitter link
    '''
    # user: User = kwargs['user']
    message_ids: MessageIds = kwargs['message_ids']
    # airdrop_config: AirdropConfig = kwargs['airdrop_config']

    if message_ids.twitter_username_request_msg_id: asyncio.create_task(delete_message(message.chat_id, 
                                                                message_ids.twitter_username_request_msg_id))
    sent_msg = await send_message(message, 'Please send your twitter profile link', reply_markup=types.ForceReply())
    message_ids.twitter_username_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_db']))


@get_current_user
@get_validation_ids
async def request_post_retweet(message: FormatedData, **kwargs):
    '''
    Request user to retweet the post
    '''
    # user: User = kwargs['user']
    message_ids: MessageIds = kwargs['message_ids']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']

    if message_ids.post_retweet_msg_id: asyncio.create_task(delete_message(message.chat_id, 
                                                                message_ids.post_retweet_msg_id))

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Retweet Post', url=airdrop_config.twitter_post_retweet_link))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='retweeted_post'))
    
    sent_msg = await send_message(message, airdrop_config.request_twitter_post_retweet_message, reply_markup=types.ForceReply())
    message_ids.twitter_post_retweet_link_i = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_db']))


@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms', 'address', 'email'))
# @permission(allowed_perm=('captcha', 'accept_terms', 'address', 'email', 'twitter', 'complete'))
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






@get_current_user
async def start(message, **kwargs):
    user: User = kwargs['user']
        
    if not user.key or user.is_bot:
        return await send_captcha_message(message, **kwargs)
    
    if not user.accepted_terms:
        return await send_welcome_message(message, **kwargs)

    if not user.group_status:
        return await request_to_join_group(message, **kwargs)
    
    if not user.channel_status:
        return await request_to_join_channel(message, **kwargs)
    
    if not user.address:
        return await request_wallet_address(message, **kwargs)
    
    if not user.email:
        return await request_email(message, **kwargs)
    
    if not user.retweeted:
        pass
    
    await dashboard(message, **kwargs)




# USER INPUT DATA HANDLERS BEGINS HERE

@get_current_user
@get_validation_ids
async def confirm_verification_handler(message: FormatedData, **kwargs: Dict):
    user: User = kwargs['user']
    message_ids : MessageIds = kwargs['message_ids']
    if not user.is_bot:
        tasks = [
            handle_invalid_message(message),
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
    
    

@get_current_user
async def accept_terms_callback_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.accepted_terms:
        tasks = [
            delete_message(message.chat_id, [message.reply_to_msg_id]),
            handle_invalid_message(message)
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



@bot.callback_query_handler(func=lambda call: call.data == 'joined_group')
@get_current_user
async def check_user_in_group_handler(message: FormatedData, **kwargs):
    user : User = kwargs['user']
    if user.group_status == 0:
        await bot.answer_callback_query(message.id, 'You are not in the group', show_alert=True)
        return
    asyncio.create_task(delete_message(message.chat_id, [message.reply_to_msg_id]))
    await check_user_in_channel_handler(message, **kwargs)
    return
    
    

@get_current_user
async def check_user_in_channel_handler(message: FormatedData, **kwargs):
    user : User = kwargs['user']
    if  user.channel_status == 0:
        await bot.answer_callback_query(message.id, 'You are not in the channel', show_alert=True)
        return
    await delete_message(message.chat_id, [message.reply_to_msg_id])
    await start(message, **kwargs)
    


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
    
    message_ids : MessageIds = kwargs['message_ids']
    
    if not message.reply_to_msg_id or message.reply_to_msg_id != message_ids.address_request_msg_id:
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
    messages_ids : MessageIds = kwargs['message_ids']
    if not message.reply_to_msg_id or message.reply_to_msg_id != messages_ids.email_request_msg_id:
        tasks = [
            send_message(message.chat_id, 'please, reply to the email request message or click /start to get the question again'),
            delete_message(message.chat_id, message.id)
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
    asyncio.create_task(update_db_object(user, user_db))
    # kwargs['user'] = user
    await send_message(message.chat_id, 'Your email has been registered', reply_to_message_id=message.id)
    await start(message, **kwargs)
    




@get_current_user
@permission(allowed_perm=('captcha', 'accept_terms', 'address', 'email'))
@get_validation_ids
async def twitter_link_submition_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.twitter_username: 
        asyncio.create_task(handle_invalid_message(message))
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
    


@format_data
async def handle_invalid_message(message: FormatedData):
    tasks = [delete_message(message.chat_id, [message.id]),
    send_message(message, 'Invalid message')]
    await asyncio.gather(*tasks)