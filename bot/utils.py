import asyncio
from os import environ
from typing import List

from deta import Deta

from bot import bot
from bot.structure import *

deta = Deta(environ['DETA_API_KEY'])

def get_db(table='users'):
    return deta.Base('airdrop_'+table.strip())

from bot.hooks import *


def try_run(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            print(func.__name__, e)
            # if environ.get('FOWARD_ERRORS_TO_ADMIN'):
            #     await args[0].bot.send_message(ADMIN_ID, str(e))
        else:
            return result
    return wrapper



@try_run
async def send_message(to_object: (FormatedData or int),
                       text, file=None,
                       reply_to_message_id=None, parse_mode=None, 
                       disable_web_page_preview=None, disable_notification=None, 
                       reply_markup=None):
    
    user_id = to_object.user_id if type(to_object) == FormatedData else to_object

    if file:
        return await bot.send_document(user_id, file)
    
    return await bot.send_message(user_id, text, reply_to_message_id=reply_to_message_id, 
                                      parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview, 
                                      disable_notification=disable_notification, reply_markup=reply_markup)
@try_run
async def exec_delete(chat_id, message_id):
    await bot.delete_message(chat_id, message_id)

@try_run
async def delete_message(user_id, msg_ids: (List[int] or int or FormatedData)):
    msg_ids = [msg_ids] if type(msg_ids) == int else [msg_ids.id] if type(msg_ids) == FormatedData else msg_ids
    await asyncio.gather(*[exec_delete(user_id, msg_id) for msg_id in msg_ids])
    
    


