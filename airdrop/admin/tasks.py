import asyncio
import csv
import io

from airdrop.structure import FormatedData, User
from airdrop.utils import delete_message, get_db, send_message


async def run_get_users_stats(message: FormatedData, wait_message_id: int):
    user_db = get_db()
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
   
   
async def run_export_users_data_to_csv(message: FormatedData, wait_message_id: int):
    demo_user = User(user_id=1, first_name='demo', last_name='demo', username='demo',)
    demo_dict = demo_user.dict()
    
    user_db = get_db()
    query = user_db.fetch()   
    users = query.items
    while query.last:
        query = user_db.fetch(last=query.last)
        users += query.items
        
    main_users = []
    for user in users:
        user = User(**user)
        user_dict = user.dict()
        user_dict['user_id'] = str(user.user_id)
        main_users.append(list(user_dict.values()))
    
    
    file_name = 'users_data.csv'
    
    file = io.StringIO()
    writer = csv.writer(file)
    writer.writerow(list(demo_dict.keys()))
    writer.writerows(main_users)
    
    file.seek(0)
    tasks = [
        send_message(message.chat_id, file_name, file=file),
        delete_message(message.chat_id, wait_message_id),
    ]
    await asyncio.gather(*tasks)

    file.close()


async def run_brodecast_message(message: FormatedData, wait_message_id: int):
    user_db = get_db()
    query = user_db.fetch()   
    
    users = query.items
    while query.last:
        query = user_db.fetch(last=query.last)
        users += query.items
    
    await asyncio.gather(*[send_message(user['user_id'], message.msg_text, parse_mode='Markdown') for user in users])
    
    asyncio.create_task(delete_message(message.chat_id, wait_message_id))
    await send_message(message.chat_id, 'Message sent!')