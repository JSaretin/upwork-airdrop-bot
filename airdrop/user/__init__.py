from telebot import types
from secrets import token_urlsafe
from airdrop import bot
import asyncio
import random
from airdrop.structure import AirdropConfig, FormatedData, MessageIds, User
from typing import Dict
from airdrop.hooks import get_current_user, get_validation_ids, format_data, permission
from airdrop.utils import delete_message, send_message, update_db_object, update_referral, save_validation_id, replace_text_with_config

DASHBOARD_BUTTONS = [
            'Wallet Address 💸',
            'balance 💰',
            'referral 🧑‍🤝‍🧑',
            'withdraw 💎',
            'Informations 🟣',
    ]



async def call_admin_dashboard(message: FormatedData, **kwargs):
    from airdrop.admin import dashboard as admin_dashboard
    await admin_dashboard(message, **kwargs)


# @get_current_user()
@get_validation_ids
async def request_language(message, **kwargs):
    message_ids: MessageIds = kwargs['message_ids']
    if message_ids.language_request_msg_id: await delete_message(message.chat_id, [message_ids.language_request_msg_id])

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('English 🇺🇲', callback_data='select_en'), 
               types.InlineKeyboardButton('🇫🇷 French', callback_data='select_fr'))

    sent_msg = await send_message(message, 'Select your language', reply_markup=markup) 
    message_ids.language_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_ids_db']))

    


@get_current_user()
@get_validation_ids
async def send_captcha_message(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    message_ids: MessageIds = kwargs['message_ids']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    verification_code = f'{random.randint(1, 10)} {random.choice(["+", "-", "x"])} {random.randint(1, 10)}'
    verification_result = eval(verification_code.replace('x', '*'))
    user.verificatin_code = str(verification_result)
    
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
        
        
    # sent_msg = bot.send_photo(user.user_id, open('verification.png', 'rb'))
    cap_msg = await send_message(message, verification_code)
    sent_msg = await send_message(message, airdrop_config.ans_captcha, 
                     reply_to_message_id=cap_msg.message_id, reply_markup=types.ForceReply())
    message_ids.captcha_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_ids_db']))



@get_current_user()
@get_validation_ids
async def send_airdrop_rules(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    message_ids: MessageIds = kwargs['message_ids']
    if message_ids.show_terms_msg_id: await delete_message(message.chat_id, [message_ids.show_terms_msg_id])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Understood', callback_data='accept_terms'))
    sent_msg = await send_message(message, airdrop_config.airdrop_rules, reply_markup=markup)
    message_ids.show_terms_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_ids_db']))


@bot.message_handler(commands=['rules'])
@get_current_user()
async def send_rules(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, airdrop_config.airdrop_rules)


async def request_to_join_group(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Group', url=f'https://t.me/{airdrop_config.group_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_group'))
    await send_message(message, airdrop_config.join_group_msg, reply_markup=markup)
    

async def request_to_join_channel(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Join Channel', url=f'https://t.me/{airdrop_config.channel_username.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='joined_channel'))
    await send_message(message, airdrop_config.join_channel, reply_markup=markup)
    


@get_current_user()
@get_validation_ids
async def request_wallet_address(message: FormatedData, **kwargs):
    '''
    This function requests the user wallet address
    '''   
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    message_ids: MessageIds = kwargs['message_ids']
    message_ids_db = kwargs['message_ids_db']

    if message_ids.address_request_msg_id: asyncio.create_task(delete_message(message.chat_id, [message_ids.address_request_msg_id]))

    sent_msg = await send_message(message, airdrop_config.submit_wallet, reply_markup=types.ForceReply())

    message_ids.address_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, message_ids_db))
    
    


@bot.message_handler(commands=['set_email'])
@bot.message_handler(regexp='^add email$')
@get_current_user()
@get_validation_ids
async def request_email(message: FormatedData, **kwargs):
    '''
    This function send the user a request to submit his/her email
    '''
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    message_ids: MessageIds = kwargs['message_ids']
    message_ids_db = kwargs['message_ids_db']

    if message_ids.email_request_msg_id: asyncio.create_task(delete_message(message.chat_id, [message_ids.email_request_msg_id]))


    sent_msg = await send_message(message, airdrop_config.submit_email, reply_markup=types.ForceReply())
    message_ids.email_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, message_ids_db))



@get_current_user()
@get_validation_ids
async def request_twitter_user_link(message: FormatedData, **kwargs):
    '''
    Request user twitter link
    '''
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    # user: User = kwargs['user']
    message_ids: MessageIds = kwargs['message_ids']
    # airdrop_config: AirdropConfig = kwargs['airdrop_config']

    if message_ids.twitter_username_request_msg_id: asyncio.create_task(delete_message(message.chat_id, 
                                                                message_ids.twitter_username_request_msg_id))
    sent_msg = await send_message(message, airdrop_config.submit_twitter_link, reply_markup=types.ForceReply())
    message_ids.twitter_username_request_msg_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_ids_db']))


@get_current_user()
@get_validation_ids
async def request_post_retweet(message: FormatedData, **kwargs):
    '''
    Request user to retweet the post
    '''
    message_ids: MessageIds = kwargs['message_ids']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    # full width inline keyboard
    markup = types.InlineKeyboardMarkup()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.row(types.InlineKeyboardButton('Retweet Post', url=airdrop_config.retweet_post_link), 
               types.InlineKeyboardButton('Confirm', callback_data='retweeted_post'))
    
    sent_msg = await send_message(message, airdrop_config.reteet_post, 
                                                reply_markup=markup)
    if message_ids.retweet_request_id: asyncio.create_task(delete_message(message.chat_id, message_ids.retweet_request_id))
    message_ids.retweet_request_id = sent_msg.message_id
    asyncio.create_task(update_db_object(message_ids, kwargs['message_ids_db']))



    
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address', 'twitter', 'retweet', 'complete'))
async def dashboard(message: FormatedData, **kwargs):
    '''
    This function shows the user dashboard
    '''
    user : User = kwargs['user']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*DASHBOARD_BUTTONS)
    extral = ['config ⚙️']
    
    if not user.email:
        extral.append('email ✉️ = 🎁')
    markup.add(*extral)
    

    await send_message(message, airdrop_config.dashboard, reply_markup=markup)


    

@bot.message_handler(commands=['start'])
@get_current_user()
@permission(allowed_perm=('!admin',), callback=call_admin_dashboard)
async def start(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    
    
    if not user.selected_lang:
        split_msg_text = message.msg_text.split(' ')
        if not user.referral_code and len(split_msg_text) == 2:
            user.referral_code = split_msg_text[1]
            asyncio.create_task(update_db_object(user, kwargs['user_db']))
        return await request_language(message, **kwargs)
        
    if user.is_bot:
        return await send_captcha_message(message, **kwargs)
    
    
    if not user.accepted_terms:
        return await send_airdrop_rules(message, **kwargs)

    if not user.group_status:
        return await request_to_join_group(message, **kwargs)
    
    if not user.channel_status:
        return await request_to_join_channel(message, **kwargs)
    
    if not user.address:
        return await request_wallet_address(message, **kwargs)
    
    # if not user.email:
    #     return await request_email(message, **kwargs)
    
    if not user.twitter_username:
        return await request_twitter_user_link(message, **kwargs)
    
    if not user.retweeted:
        return await request_post_retweet(message, **kwargs)
    
    return await dashboard(message, **kwargs)
    # return handle_invalid_message(message, **kwargs)



# USER INPUT DATA HANDLERS BEGINS HERE

@bot.callback_query_handler(func=lambda call: (call.data in ['select_en', 'select_fr']))
@get_current_user()
async def select_language(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    user.language_code = message.msg_text.split('_')[-1]
    user.selected_lang = True
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
    await start(message, **kwargs)



@bot.message_handler(regexp='^[0-9]+$')
@get_current_user()
@permission(('!admin',), callback=call_admin_dashboard)
@get_validation_ids
async def confirm_verification_handler(message: FormatedData, **kwargs: Dict):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user: User = kwargs['user']
    message_ids : MessageIds = kwargs['message_ids']
    if not user.is_bot:
        asyncio.create_task(handle_invalid_message(message),)
        return
    
    if not message.reply_to_msg_id:
        return await send_message(message, airdrop_config.reply_captcha)
    if message.reply_to_msg_id != message_ids.captcha_msg_id:
        return await send_message(message, airdrop_config.reply_captcha)

    if message.msg_text != user.verificatin_code:
        await delete_message(message.chat_id, [message_ids.captcha_msg_id-1, message_ids.captcha_msg_id, message.id][::-1])
        await send_message(message, airdrop_config.wrong_captcha),
        await start(message, **kwargs)
        return
    
    user.is_bot = False
    await send_message(message, airdrop_config.captcha_verified)
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
    await start(message, **kwargs)
    
    
@bot.callback_query_handler(func=lambda call: call.data == 'accept_terms')
@get_current_user()
async def accept_terms_callback_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if user.accepted_terms:
        await delete_message(message.chat_id, [message.reply_to_msg_id]),
        await bot.answer_callback_query(message.reply_to_msg_id, 'You already accepted the terms', show_alert=True)
        return
    
    user.accepted_terms = True
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
    await bot.edit_message_text(message.replied_message_text, message.chat_id, message.reply_to_msg_id)

    await start(message, **kwargs)



@bot.callback_query_handler(func=lambda call: call.data == 'joined_group')
@get_current_user()
async def check_user_in_group_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user : User = kwargs['user']
    if user.group_status == 0:
        await bot.answer_callback_query(message.id, airdrop_config.not_in_group_msg, show_alert=True)
        return
    user.group_status = 1
    await bot.edit_message_reply_markup(message.chat_id, message.reply_to_msg_id, reply_markup=None)
    await send_message(message, 'task completed ✅')
    await start(message, **kwargs)
    return
    
    
@bot.callback_query_handler(func=lambda call: call.data == 'joined_channel')
@get_current_user()
async def check_user_in_channel_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user : User = kwargs['user']
    if  user.channel_status == 0:
        await bot.answer_callback_query(message.id, airdrop_config.not_in_channel, show_alert=True)
        return
    user.channel_status = 1
    await bot.edit_message_reply_markup(message.chat_id, message.reply_to_msg_id, reply_markup=None)
    await send_message(message, 'task completed ✅')
    await start(message, **kwargs)
    

@bot.message_handler(regexp='^0[xX][0-9a-fA-F]{40}$')
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms'), callback=start)
@get_validation_ids
async def register_address_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user: User = kwargs['user']
    '''
    This function registers the user wallet address
    '''
    if user.address:
        await send_message(message, airdrop_config.task_completed_already)
        return
    
    message_ids : MessageIds = kwargs['message_ids']
    
    if not message.reply_to_msg_id or message.reply_to_msg_id != message_ids.address_request_msg_id:
        await send_message(message,airdrop_config.reply_wallet_request)
        return
    
    user_db = kwargs['user_db']
    address = message.msg_text.lower()
    query = user_db.fetch({'address': address})
    if query.count > 0:
        await send_message(message, airdrop_config.wallet_used)
        return
    
    user.address = address
    
    asyncio.create_task(update_db_object(user, user_db))

    await send_message(message, airdrop_config.wallet_saved, reply_to_message_id=message.id)
    await start(message, **kwargs)



@bot.message_handler(regexp='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address', 'complete'), callback=start)
@get_validation_ids
async def register_email_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user: User = kwargs['user']
    if user.email:
        await send_message(message, airdrop_config.task_completed_already)
        return
    
    messages_ids : MessageIds = kwargs['message_ids']
    if not message.reply_to_msg_id or \
        message.reply_to_msg_id != messages_ids.email_request_msg_id:
        await send_message(message, airdrop_config.reply_email_request),
        return
    
    user_db = kwargs['user_db']
    email = message.msg_text.lower()
    query = user_db.fetch({'email': email})
    if query.count > 0 and query.items[0]['key'] != user.key:
        asyncio.create_task(send_message(message, airdrop_config.email_used, reply_to_message_id=message.id))
        return

    user.email = email
    user.balance = user.balance + airdrop_config.extral_reward
    await send_message(message, airdrop_config.email_saved, reply_to_message_id=message.id)
    asyncio.create_task(update_db_object(user, user_db))
    kwargs['user'] = user
    await start(message, **kwargs)
    



@bot.message_handler(regexp='^(https://)?twitter.com/[a-zA-Z0-9_]{3,30}$')
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address'), callback=start)
@get_validation_ids
async def twitter_link_submition_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user: User = kwargs['user']
    if user.twitter_username: return await send_message(message, airdrop_config.task_completed_already)
        
    messages_ids : MessageIds = kwargs['message_ids']
    if not message.reply_to_msg_id or \
        message.reply_to_msg_id != \
            messages_ids.twitter_username_request_msg_id: return await \
                send_message(message, airdrop_config.reply_twitter_request)
    
    ignore_usernames = ['about', 'home', 
                        airdrop_config.twitter_link.split('/')[-1], 
                        'tweetdeck', 'mobile']
    
    username = message.msg_text.lower().strip().replace('https://twitter.com/', '')

    # if username in ignore_usernames: return await send_message(message, 'unsuported 📛')
        
    user_db = kwargs['user_db']

    query = user_db.fetch({'twitter_username': username})
    
    if query.count > 0:
        asyncio.create_task(send_message(message, airdrop_config.twitter_used))
        return
    
    user.twitter_username = username
    
    asyncio.create_task(update_db_object(user, user_db))
    
    await send_message(message, airdrop_config.twitter_saved, reply_to_message_id=message.id)
    await start(message, **kwargs)
    


@bot.message_handler(commands=['remove_wallet'])
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address'), callback=start)
async def remove_wallet_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    if not user.address: return await send_message(message, 'You don\'t have a wallet 🤷‍♂️')
    user.address = None
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
    await send_message(message, 'Wallet removed 🙈')
    await start(message, **kwargs)
    
    
@bot.message_handler(commands=['remove_email'])
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address'), callback=start)
async def remove_email_handler(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    if not user.email: return await send_message(message, 'You don\'t have an email 🤷‍♂️')
    user.email = None
    user.balance -= airdrop_config.extral_reward
    asyncio.create_task(update_db_object(user, kwargs['user_db']))
    await send_message(message, 'Email removed 🙈')
    await start(message, **kwargs)

    
    

@bot.callback_query_handler(func=lambda call: call.data == 'retweeted_post')
@get_current_user()
@permission(allowed_perm=('verified', 'accept_terms', 'address', 'twitter'), callback=start)
async def retweeted_callback_handler(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    user: User = kwargs['user']
    if user.retweeted: 
        await send_message(message, 'task already completed ☑️')
        return
    user_db = kwargs['user_db']
    
    user_obj= user.dict()
    user_obj.update({'retweeted': True, 'registration_complete': True,
                     'referral_link': token_urlsafe(random.randint(6, 16)), 
                     'balance': user.balance + airdrop_config.registration_amount})
    user = User(**user_obj)
    kwargs['user'] = user
    
    await bot.edit_message_reply_markup(message.chat_id, message.reply_to_msg_id, reply_markup=None)
    await send_message(message, 'task completed ☑️')
    asyncio.create_task(update_db_object(user, user_db))
    await send_message(message, airdrop_config.account_created)
    await start(message, **kwargs)
    if user.referral_code:
        asyncio.create_task(update_referral(user, airdrop_config, user_db))
    
    

@bot.message_handler(regexp='^balance 💰$')
@get_current_user()
@permission(allowed_perm=('complete','channel', 'group', 'retweet', 'accept_terms'), callback=start)
async def get_balance(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, airdrop_config.balance, parse_mode='Markdown')
    
   

@bot.message_handler(regexp='^referral 🧑‍🤝‍🧑$')
@get_current_user()
@permission(allowed_perm=('complete','channel', 'group', 'retweet', 'accept_terms'), callback=start)
async def get_referral_link(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    me = await bot.get_me()
    link = f' https://t.me/{me.username}/?start={user.referral_link}'
    await send_message(message, airdrop_config.referral_link.replace('{ref_link}', link))
    


@bot.message_handler(regexp='Wallet Address 💸')
@get_current_user()
@permission(allowed_perm=('complete','channel', 'group', 'retweet', 'accept_terms'), callback=start)
async def check_wallet(message: FormatedData, **kwargs):
    user: User = kwargs['user']
    await send_message(message, f'*wallet*: {user.address}', parse_mode='Markdown')



# @get_current_user()
# @permission(allowed_perm=('complete',), callback=start)
# async def check_email(message: FormatedData, **kwargs):
#     user: User = kwargs['user']
#     await send_message(message, f'*email*: {user.email}', parse_mode='Markdown')


@bot.message_handler(regexp='^Informations 🟣$')
@get_current_user()
# @permission(allowed_perm=('!admin',), callback=start)
async def information(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    # user: User = kwargs['user']
    await send_message(message, airdrop_config.welcome_message)


@bot.message_handler(regexp=r'^withdraw 💎$')
@get_current_user()
@permission(allowed_perm=('complete','channel', 'group', 'retweet', 'accept_terms'), callback=start)
async def withdraw(message: FormatedData, **kwargs):
    airdriop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, airdriop_config.withdraw)


@bot.message_handler(regexp=r'^config ⚙️$')
@bot.message_handler(commands=['config'])
@get_current_user()
async def config(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, airdrop_config.config)



@format_data
@get_current_user()
@permission(allowed_perm=('!admin',), callback=call_admin_dashboard)
async def handle_invalid_message(message: FormatedData, **kwargs):
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, airdrop_config.invalid, parse_mode='Markdown')