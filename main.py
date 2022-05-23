import asyncio
from fastapi import FastAPI
from airdrop import bot
from telebot import types


app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.put('/toggle')
async def delete():
  await bot.remove_webhook()


@app.post('/toggle')
async def set_webhook():
  await bot.set_webhook(f'https://5k28v6.deta.dev/')
  

@app.post('/')
async def webhook(update: dict):
    if update:
        update = types.Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return



if __name__ == '__main__':
    print('online')
    asyncio.run(bot.polling())