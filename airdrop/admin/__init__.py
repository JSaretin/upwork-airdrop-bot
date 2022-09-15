import asyncio
from typing import Tuple

from airdrop import bot
from airdrop.hooks import get_current_user, send_message, try_run, permission
from airdrop.structure import (AirdropConfig, AirdropLangConf, AirdropCoreConfig, AirdropLangUpdateID,
                               FormatedData, User)
from airdrop.utils import create_airdrop_config, delete_message, fetch_user_conf, get_airdrop_core_config, get_config_message_ids, get_db, update_db_object
from telebot import types

from .tasks import (run_brodecast_message, run_export_users_data_to_csv,
                    run_get_users_stats)
from airdrop.user import start, handle_invalid_message



async def show_dashboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        '📊 Users Stats',
        '⬇️ Export Users Data',
        '⚙️ Core Config',
        '⚙️ User config',
        '📢 Broadcast',
    ]
    markup.add(*buttons)
    asyncio.create_task(send_message(message, 'admin dashboard', reply_markup=markup))




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




    



airdrop_user_conf = AirdropLangConf()
airdrop_user_conf_obj = airdrop_user_conf.dict()
user_conf_keys = list(airdrop_user_conf_obj.keys())
user_conf_keys.remove('key')
user_conf_keys.remove('language_code')
frence_users_conf_keys = ['fr_'+key for key in user_conf_keys]




async def upate_lang_conf(message: FormatedData, message_ids:AirdropLangUpdateID ,db):
    command = message.msg_text.strip().replace('/', '').replace('fr_', '')
    message_ids_obj = message_ids.dict()
    
    _, airdrop_user = await fetch_user_conf(message_ids.language_code, True)
    
    airdrop_user_obj = airdrop_user.dict()

    sent_msg = await send_message(message,f'👇Curent value👇\n\n{airdrop_user_obj[command]}')
    sent_msg = await send_message(message,f'Enter the new replacement', 
                       reply_to_message_id=sent_msg.message_id, reply_markup=types.ForceReply())
    message_ids_obj[command] = sent_msg.message_id
    message_ids = AirdropLangUpdateID(**message_ids_obj)

    asyncio.create_task(update_db_object(message_ids, db))
    
    


@bot.message_handler(commands=user_conf_keys)
@get_current_user()
@permission(('admin', ), callback=start)
async def request_english_conf(message: FormatedData, **kwargs):
    message_ids, db = await get_config_message_ids()
    await upate_lang_conf(message, message_ids, db)
    

@bot.message_handler(commands=frence_users_conf_keys)
@get_current_user()
@permission(('admin', ), callback=start)
async def request_english_conf(message: FormatedData, **kwargs):
    message_ids, db = await get_config_message_ids(lang='fr')
    await upate_lang_conf(message, message_ids, db)




@bot.message_handler(regexp='⚙️ User config')
@bot.message_handler(commands=['settings', 'setting', 'config', 'configuration'])
@get_current_user()
@permission(('admin', ), callback=start)
async def get_settings(message: FormatedData, **kwargs):
    msg = '📢 User English config\n\n'

    confs = '\n'.join([f'/{key} = set {key.replace("_", " ")} message' for key in user_conf_keys])
    
    fr_msg = '📢 User French config\n\n'
    fr_confs = '\n'.join([f'/fr_{key} = set {key.replace("_", " ")} message' for key in user_conf_keys])
    
    await asyncio.gather(*[
        send_message(message, msg + confs),
        send_message(message, fr_msg + fr_confs)
    ])





    
    

core_conf = AirdropCoreConfig()
core_conf_obj = core_conf.dict()
core_conf_keys = list(core_conf_obj.keys())
core_conf_keys.remove('key')


async def airdrop_core():
    db = get_db('core_settings_ids')
    query = db.fetch()
    if query.count:
        core = query.items[0]
    else:
    
        new_core = {}
        for i in core_conf_keys:
            new_core[i] = None
        new_core['cast'] = None
        core = new_core
    core = db.put(core)
    return core, db


@bot.message_handler(regexp='📢 Broadcast')
@get_current_user()
@permission(('admin', ), callback=start)
async def broadcast(message: FormatedData, **kwargs):
    core_ids, db = await airdrop_core()
    sent_msg = await send_message(message.chat_id, 'Enter the message to broadcast', reply_markup=types.ForceReply())
    core_ids['cast'] = sent_msg.message_id
    key = core_ids.pop('key')
    db.update(core_ids, key)


@bot.message_handler(regexp='⚙️ Core Config')
@get_current_user()
@permission(('admin', ), callback=handle_invalid_message)
async def send_core_list(message: FormatedData, **kwargs):
    await send_message(message, 'CORE SETTINGS\n\n'+"\n".join([f'/{k}' for k in core_conf_keys]))




@bot.message_handler(commands=core_conf_keys)
@get_current_user()
@permission(('admin', ), callback=handle_invalid_message)
async def request_core_conf(message: FormatedData, **kwargs):
    command = message.msg_text.strip().replace('/', '')

    core_main = await get_airdrop_core_config()
    core_ids, db = await airdrop_core()
    
    await send_message(message, f'current value\n\n{core_main.dict()[message.msg_text.replace("/", "")]}')
    sent_msg = await send_message(message, 'enter new value', reply_markup=types.ForceReply())

    core_ids[command] = sent_msg.message_id
    key = core_ids.pop('key')
    db.update(core_ids, key)




@bot.message_handler()
@get_current_user()
@permission(('admin', ), callback=handle_invalid_message)
async def handle_set_airdrop_configs(message: FormatedData, **kwargs):  
    if not message.reply_to_msg_id: return await send_message(message.chat_id, \
        'invalid request: please reply to the set request of the config you want to change')   
    
      
    core_ids, db = await airdrop_core()
    keys, values = (list(core_ids.keys()), list(core_ids.values()))
    if message.reply_to_msg_id in values:        
        if message.reply_to_msg_id == core_ids.get('cast'):
            sent_msg = await send_message(message, 'sending messags.....')
            asyncio.create_task(run_brodecast_message(message, sent_msg.message_id))
            return
        core_main = await get_airdrop_core_config()
        core_main_dict = core_main.dict()
        _key = keys[values.index(message.reply_to_msg_id)]
        core_main_dict[_key] = message.msg_text
        core_main = AirdropCoreConfig(**core_main_dict)
        asyncio.create_task(update_db_object(core_main, get_db('airdrop_core_config')))
        await send_message(message, '✅ done')
        up_key = core_ids.pop('key')
        core_ids[_key] = None
        db.update(core_ids, up_key)
        return
        
    
     
    en_message_ids, _ = await get_config_message_ids()
    en_message_ids_obj = en_message_ids.dict()
    obj_key, obj_value = [list(en_message_ids_obj.keys()), list(en_message_ids_obj.values())]
    
    if message.reply_to_msg_id in obj_value:
        return await updated_conf(message, obj_key, obj_value)
    
    fr_message_ids, _ = await get_config_message_ids('fr')
    fr_message_ids_obj = fr_message_ids.dict()
    obj_key, obj_value = [list(fr_message_ids_obj.keys()), list(fr_message_ids_obj.values())]
    if message.reply_to_msg_id in obj_value:
        return await updated_conf(message, obj_key, obj_value, 'fr')




async def updated_conf(message, obj_key, obj_value, lang='en'):
    _, user_conf = await fetch_user_conf(lang, True)
    _key = obj_key[obj_value.index(message.reply_to_msg_id)]
        
    user_conf_obj = user_conf.dict()
    user_conf_obj[_key] = message.msg_text
        
    user_conf = AirdropLangConf(**user_conf_obj)
    await update_db_object(user_conf, get_db('airdrop_lang_config'))
    await send_message(message.chat_id, f'✅ {_key} has been updated')