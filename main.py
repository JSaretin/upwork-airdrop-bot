import asyncio
from typing import Optional
from fastapi import FastAPI, Header
from airdrop import bot
from telebot import types
from secrets import token_urlsafe

from pydantic import BaseModel

token =token_urlsafe(10)
class Form(BaseModel): 
  domain: str


app = FastAPI()

@app.get('/')
async def root():
    return {'status': 200}


@app.put('/toggle')
async def delete():
  await bot.remove_webhook()


@app.post('/toggle')
async def set_webhook(form: Form):
  try:
    await bot.set_webhook(f'https://{form.domain}/{token}')
  except Exception as e:
    return str(e)
  return {'status': 200}
  

@app.post('/{token}')
async def webhook(update: dict):
    if update:
        update = types.Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return
