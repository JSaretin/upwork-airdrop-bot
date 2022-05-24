import asyncio
from typing import Tuple

from airdrop import bot
from airdrop.hooks import get_current_user, send_message, try_run, permission
from airdrop.structure import (AirdropConfig, AirdropConfigMessageIDS,
                               FormatedData, User)
from airdrop.utils import create_airdrop_config, delete_message, fetch_user_conf, get_db, update_db_object
from telebot import types

from .tasks import (run_brodecast_message, run_export_users_data_to_csv,
                    run_get_users_stats)
from airdrop.user import start, handle_invalid_message



async def show_dashboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        '📊 Users Stats',
        '⬇️ Export Users Data',
        '⚙️ Settings',
        '📢 Broadcast',
    ]
    markup.add(*buttons)
    asyncio.create_task(send_message(message, 'admin dashboard', reply_markup=markup))

new_config_message_ids = AirdropConfigMessageIDS()
new_config_message_ids_obj = new_config_message_ids.dict()
keys = list(new_config_message_ids_obj.keys())
keys.remove('key')
keys.remove('brodecast_msg')


@bot.message_handler(commands=['start'])
@get_current_user()
@permission(('admin',), callback=start)
async def dashboard(message: FormatedData, **kwargs):
    if message.msg_text != '/start':
        await handle_set_airdrop_configs(message, **kwargs)
    await show_dashboard(message)


@bot.message_handler(regexp='📊 Users Stats')
@get_current_user()
@permission(('admin', ), callback=start)
async def get_users_stats(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'processing....')
    asyncio.create_task(run_get_users_stats(message, sent_msg.id))


@bot.message_handler(regexp='⬇️ Export Users Data')
@get_current_user()
@permission(('admin', ), callback=start)
async def export_users_data_to_csv(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'exporting....')
    asyncio.create_task(run_export_users_data_to_csv(message, sent_msg.id))



@bot.message_handler(regexp='⚙️ Settings')
@bot.message_handler(commands=['settings', 'setting', 'config', 'configuration'])
@get_current_user()
@permission(('admin', ), callback=start)
async def get_settings(message: FormatedData, **kwargs):
    text = '\n'.join([f'/{key} : to set {key.replace("msg", "message").replace("_", " ")}' for key in keys])
    lines = text.split('\n')
    part_1 = '\n'.join(lines[:len(lines)//2])
    part_2 = '\n'.join(lines[len(lines)//2:])
    await send_message(message.chat_id, part_1)
    await send_message(message.chat_id, part_2)
    

@bot.message_handler(regexp='📢 Broadcast')
@get_current_user(load_config=True)
@permission(('admin', ), callback=start)
async def broadcast(message: FormatedData, **kwargs):
    sent_msg = await send_message(message.chat_id, 'enter the message to broadcast', reply_markup=types.ForceReply())
    airdrop_config_message_ids : AirdropConfigMessageIDS = kwargs['airdrop_config_message_ids']
    if airdrop_config_message_ids.brodecast_msg: asyncio.create_task(delete_message(message, airdrop_config_message_ids.brodecast_msg))
    airdrop_config_message_ids.brodecast_msg = sent_msg.message_id
    asyncio.create_task(update_db_object(airdrop_config_message_ids, kwargs['airdrop_config_message_ids_db']))
    




@bot.message_handler(commands=keys)
@get_current_user(load_config=True)
@permission(('admin', ), callback=start)
async def show_config_commands(message: FormatedData, **kwargs):
    command = message.msg_text.strip().replace('/', '')

    airdrop_config_message_ids: AirdropConfigMessageIDS = kwargs['airdrop_config_message_ids']
    airdrop_config_message_ids_obj = airdrop_config_message_ids.dict()
    to_update = airdrop_config_message_ids_obj.get(command)

    if to_update: asyncio.create_task(delete_message(message, to_update))
    
    if command.startswith('fr_'):
        airdrop_config: AirdropConfig = kwargs['airdrop_config_fr']
    else:
        airdrop_config: AirdropConfig = kwargs['airdrop_config']
    await send_message(message, f'*current value*\n\n{airdrop_config.dict()[command.replace("fr_", "")]}', parse_mode='Markdown')
    sent_msg = await send_message(message, f'enter your new {command.replace("fr_", "Frence").replace("_", " ")}', reply_markup=types.ForceReply())
    airdrop_config_message_ids_obj.update({command: sent_msg.message_id})
    airdrop_config_message_ids = AirdropConfigMessageIDS(**airdrop_config_message_ids_obj)
    asyncio.create_task(update_db_object(airdrop_config_message_ids, kwargs['airdrop_config_message_ids_db']))





@bot.message_handler()
@get_current_user(load_config=True)
@permission(('admin', ), callback=handle_invalid_message)
async def handle_set_airdrop_configs(message: FormatedData, **kwargs):    
    airdrop_config_message_ids: AirdropConfigMessageIDS = kwargs['airdrop_config_message_ids']
    airdrop_config_message_ids_obj = airdrop_config_message_ids.dict()
    request_keys = list(airdrop_config_message_ids_obj.keys())
    request_value = list(airdrop_config_message_ids_obj.values())
    if not message.reply_to_msg_id:
        asyncio.create_task(send_message(message, 'invalid message📛: reply to the replace request if you want to update a message or value or click /settings to get the config list'))
        return
    if message.reply_to_msg_id not in request_value:
        asyncio.create_task(send_message(message, 'You have replied to an invalid or expired request\nclick /settings a list of available configs'))
        return 
    
    message_text = message.msg_text

    key = request_keys[request_value.index(message.reply_to_msg_id)]
        
    if key == 'brodecast_msg':
        sent_msg = await send_message(message, 'sending message, you will get a notification when done ✅')
        asyncio.create_task(show_dashboard(message))
        asyncio.create_task(run_brodecast_message(message, sent_msg.message_id))
        airdrop_config_message_ids_obj[key] = None
        airdrop_config_message_ids = AirdropConfigMessageIDS(**airdrop_config_message_ids_obj)
        asyncio.create_task(update_db_object(airdrop_config_message_ids, kwargs['airdrop_config_message_ids_db']))
        return
    if key.startswith('fr_'):
        airdrop_config: AirdropConfig = kwargs.get('airdrop_config_fr', await fetch_user_conf('fr'))
    else:
        airdrop_config: AirdropConfig = kwargs['airdrop_config']
    airdrop_config_obj = airdrop_config.dict()
    airdrop_config_obj.update({key: message_text})
    airdrop_config = AirdropConfig(**airdrop_config_obj)
    asyncio.create_task(update_db_object(airdrop_config, kwargs['airdrop_config_db']))
    
    asyncio.create_task(send_message(message, f'*{key.replace("_", " ")}* set ✅', parse_mode='Markdown'))
    
    airdrop_config_message_ids_obj[key] = None
    airdrop_config_message_ids = AirdropConfigMessageIDS(**airdrop_config_message_ids_obj)
    asyncio.create_task(update_db_object(airdrop_config_message_ids, kwargs['airdrop_config_message_ids_db']))
    
    await show_dashboard(message)
    
    
