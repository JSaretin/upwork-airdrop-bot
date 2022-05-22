import csv
import io

from bot.structure import *
from bot.utils import *


async def run_get_users_stats(message: FormatedData, user_db, wait_message_id: int):
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
   
   
async def run_export_users_data_to_csv(message: FormatedData, user_db, wait_message_id: int):
    query = user_db.fetch()   
    users = query.items
    while query.last:
        query = user_db.fetch(last=query.last)
        users += query.items
    
    
    # create a file in memory

    file = io.StringIO()
    writer = csv.writer(file)

    # write the header
    writer.writerow(['id', 'user_id', 'email', 'address', 'username', 'verificatin_code', 'first_name', 'last_name', 'accepted_terms', 'twitter_username', 'is_bot', 'balance', 'referral_link', 'referrals', 'is_admin', 'language_code', 'registration_complete', 'language_set', 'group_status', 'channel_status'])
    writer.writerows(users)

    # write the data to the file
    file.seek(0)

    # send the file to the user
    tasks = [
        delete_message(message.chat_id, wait_message_id),
        send_message(message.chat_id, 'users.csv', file=file, parse_mode='Markdown'),
    ]
    await asyncio.gather(*tasks)

    file.close()
