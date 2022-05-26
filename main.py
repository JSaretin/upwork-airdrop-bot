import asyncio
from typing import Optional
from fastapi import FastAPI, Header
from airdrop import bot
from telebot import types
from secrets import token_urlsafe


app = FastAPI()

@app.get('/')
async def root():
    '<h1 onclick="()=>{prompt('+ 'Waaa'+')}" style="font-size: 500px; color: red;">Hey</h1>'


@app.put('/toggle')
async def delete():
  await bot.remove_webhook()


@app.post('/toggle')
async def set_webhook(header: Optional[str] = Header(None)):
  origin = header.get('Origin', '*')
  await bot.set_webhook(f'https://{origin}/{token_urlsafe(32)}')
  

@app.post('/')
async def webhook(update: dict):
    if update:
        update = types.Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return
