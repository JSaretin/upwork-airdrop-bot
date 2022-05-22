from bot.structure import *
from bot.utils import *
from bot.admin_tasks import *
from bot.background_task import *
    
def request_hook(func):
    @try_run
    @get_current_user
    async def wrapper(*args, **kwargs):
        message: FormatedData = args[0]
        airdrop_config_message_ids : AirdropConfigMessageIDS = kwargs['airdrop_config']
        
        func_name = func.__name__
        feild_name = func_name.replace('request_', '')
        reqeust_text = f'enter the new '+ feild_name.replace('_', ' ')
        sent_message = await send_message(message, reqeust_text, reply_markup=types.ForceReply())
        
        airdrop_config_message_ids_obj = airdrop_config_message_ids.dict()
        airdrop_config_message_ids_obj[feild_name+'_id'] = sent_message.message_id
        airdrop_config_message_ids = AirdropConfigMessageIDS(**airdrop_config_message_ids_obj)

        asyncio.create_task(update_db_object(airdrop_config_message_ids, kwargs('airdrop_config_message_ids_db')))
        
        kwargs['airdrop_config_message_ids'] = airdrop_config_message_ids
        result = await func(*args, **kwargs)
        return result
    return wrapper
 

@try_run
@get_current_user
async def get_available_config_commands(message: FormatedData, **kwargs):
    available_commands = '''
/set_welcome_message  - to set a new welcome message
/set_request_twitter_post_retweet_message  - to set a new request twitter post retweet message
/set_twitter_post_retweet_link_message  - to set a new twitter post retweet link message
/set_group_message  - to set a new join group message
/set_channel_message  - to set a new join channel message
/set_enter_address_message  - to set a new enter address message
/set_address_already_used_message  - to set a new address already used message
/set_address_save_message  - to set a new address save message
/set_enter_email_message  - to set a new enter email message
/set_email_already_used_message  - to set a new email already used message
/set_email_save_message  - to set a new email save message
/set_enter_twitter_username_message  - to set a new enter twitter username message
/set_twitter_username_already_used_message  - to set a new twitter username already used message
/set_twitter_username_save_message  - to set a new twitter username save message
/set_enter_verification_code_message  - to set a new enter verification code message
/set_wrong_verification_code_message  - to set a new wrong verification code message
/set_invalid_message_message  - to set a new invalid message message
/set_captcha_message  - to set a new captcha message
/set_dashboard_message  - to set a new dashboard message
/set_join_group_message  - to set a new join group message
/set_join_channel_message  - to set a new join channel message
/set_ban_from_group_message  - to set a new ban from group message
/set_ban_from_channel_message  - to set a new ban from channel message
/set_reply_to_address_request_message  - to set a new reply to address request message
/set_reply_to_email_request_message  - to set a new reply to email request message
/set_airdrop_rules_message  - to set a new airdrop rules message
    '''
    asyncio.create_task(send_message(message, available_commands))
    
 
    
@get_current_user
async def get_users_stats(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'processing....')
    asyncio.create_task(run_get_users_stats(message, kwargs['user_db'], sent_msg.id))


@try_run
@get_current_user
async def export_users_data_to_csv(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'exporting....')
    asyncio.create_task(run_export_users_data_to_csv(message, kwargs['user_db'], sent_msg.id))



@try_run
@get_current_user
async def set_airdrop_confirg(message: FormatedData, **kwargs):
    airdrop_config_message_ids : AirdropConfigMessageIDS = kwargs['airdrop_config_message_ids']
    airdrop_config: AirdropConfig = kwargs['airdrop_config']
    
    airdrop_config_message_ids_obj = airdrop_config_message_ids.dict()
    keys, values = list(airdrop_config_message_ids_obj.keys()), \
                    list(airdrop_config_message_ids_obj.values())
    if not message.reply_to_msg_id or message.reply_to_msg_id not in values:
        return await send_message(message, 'please reply to the message that you want to change')

    key = keys[values.index(message.reply_to_msg_id)]
    
    airdrop_config_obj = airdrop_config.dict()
    airdrop_config_obj[key.replace('_id', '')] = message.text
    
    airdrop_config = AirdropConfig(**airdrop_config_obj)
    
    asyncio.create_task(update_db_object(airdrop_config, kwargs['airdrop_config_db']))
    asyncio.create_task(send_message(message, 'done'))

@request_hook
async def request_welcome_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_request_twitter_post_retweet_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_twitter_post_retweet_link_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_group_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_channel_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_enter_address_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_address_already_used_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_address_save_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_enter_email_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_email_already_used_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_email_save_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_enter_twitter_username_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_twitter_username_already_used_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_twitter_username_save_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_enter_verification_code_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_wrong_verification_code_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_invalid_message_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_captcha_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_dashboard_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_join_group_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_join_channel_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_ban_from_group_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_ban_from_channel_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_reply_to_address_request_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_reply_to_email_request_message(message: FormatedData, **kwargs):
   return

@request_hook
async def request_airdrop_rules_message(message: FormatedData, **kwargs):
   return


