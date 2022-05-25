from pydantic import BaseModel


class User(BaseModel):
    key: str = None
    user_id: int
    email: str = None
    address: str = None
    username: str = None
    verificatin_code: str = None
    first_name: str
    last_name: str = None
    accepted_terms: bool = False
    twitter_username: str = None
    is_bot: bool = True
    balance: int = 0
    referral_balance: int = 0
    referral_link: str = None
    referral_code: str = None
    referrals: int = 0
    is_admin: bool = False
    language_code: str = 'en'
    selected_lang: bool = False
    registration_complete: bool = False
    retweeted: bool = False
    group_status: int = 0
    channel_status: int = 0
    
    
class MessageIds(BaseModel):
    key: str = None
    user_id: str
    captcha_msg_id: int = None
    show_terms_msg_id: int = None
    address_request_msg_id: int = None
    email_request_msg_id: int = None
    language_request_msg_id: int = None
    twitter_username_request_msg_id: int = None
    retweet_request_id: int = None
    

class FormatedData(BaseModel):
    id: int
    user_id: int
    msg_type: str
    msg_text: str = None
    reply_to_msg_id: int = None
    replied_message_text: str = None
    language_code: str = 'en'
    chat_type: str = 'private'
    chat_id: int = None
    first_name: str = None
    last_name: str = None
    username: str = None
    content_type: str = 'text'
    

class AirdropCoreConfig(BaseModel):
    key: str = None
    name: str = 'Versity'
    symbol: str = '$SITY'
    website_link: str = 'https://www.versity.io'
    twitter_link: str = 'https://twitter.com/helloversity'
    retweet_post_link: str = 'https://twitter.com/helloversity/status/1234'
    group_username: str = '@Validationgrouptg'
    channel_username: str = '@validatonchanneltg'
    airdrop_status: bool = True
    registration_amount: int = 500
    referral_amount: int = 100
    extral_reward: int = 50
    min_referrals: int = 5
    max_referrals: int = None
    withdraw_date: str = '30 June 2022'
    send_error_message: bool = True
    send_error_to: str = '@lovelynCertk'
    
    
class AirdropLangConf(BaseModel):
    key: str = None
    language_code: str = 'en'
    invalid : str= 'Invalid message'
    airdrop_closed_message: str = 'Airdrop is closed'
    config: str = 'change email click /remove_email\nchange wallet address click /remove_wallet\nto get the airdrop rules click /rules\n'
    airdrop_rules: str = 'Submit your wallet and email'
    reteet_post = 'Retweet the post'
    
    join_channel: str = 'Join channel to continue'
    not_in_channel: str = 'You are not in the channel\np.s. join the channel to continue'
    
    welcome_message: str = '''Versity is the first real estate metaverse dedicated to professionals and individuals.



The ICO is starting very soon.

The first ICO backed by a French publicly traded company.



🔰 More informations

🟣 Website: {site}



🔰 Follow us

🟣 Telegram: {tg_group}

🟣 Twitter: {twitter}

First metaverse dedicated to real estate! | Versity
Discover Versity is the first metaverse dedicated toreal estate serving professionals, investors and individuals.
Telegram
Versity
The new age of real estate. 👉Versity.io 👉 {twitter}
Twitter
{twitter}
    
    '''
    not_bot_msg: str = 'enter the answer to the captcha'
    join_group_msg: str = 'Join group to continue'
    not_in_group_msg: str = 'You are not in the group\np.s. join the group to continue'

    ban_from_group_msg: str = 'You are banned from group'
    ban_from_channel_msg: str = 'You are banned from channel'
    
    ans_captcha: str = 'Please enter the verification code'
    wrong_captcha: str = 'Wrong verification code'
    captcha_verified: str = 'Your verification code has been saved'
    reply_captcha: str = 'To prove your are not a bot, reply to the verification answer request message or click /start to get a new request'

    submit_wallet: str = 'Please enter your Polygon address'
    wallet_used: str = 'Your address already exists, click /request_address to set a new one'
    wallet_saved: str = 'You wallet address has been saved'
    wallet_removed: str = 'Wallet removed 🙈'
    no_wallet_found: str = 'No wallet found'
    reply_wallet_request: str = 'To register your wallet address, reply to the wallet request message or click /start to get a new request'
    
    submit_email : str = 'Please enter your email'
    email_used : str = 'Your email already exists, click /request_email to set a new one'
    email_saved : str = 'You email has been saved'
    email_removed: str = 'Your email has been removed'
    no_email_found: str = 'No email found'
    reply_email_request : str = 'To register your email, reply to the email request message or click /set_email to get a new request'

    submit_twitter_link : str= 'Please enter your twitter profile like\nlink must start with https://'
    twitter_used : str = 'this twitter profile already exists'
    twitter_saved: str = 'twitter saved ✅'
    reply_twitter_request: str = 'To register your twitter profile, reply to the twitter link request message or click /start to get a new request'
    
    account_created: str = 'Congratulations!🎊\naccount created successfully'
    
    dashboard: str = 'dashboard'
    balance: str = '*Balance*: {bal}\n*Referral Balance*: {ref_bal}\n*Total Balance*: {total_bal}\n*Referral Counts*: {ref_count}'
    referral_link: str = 'To earn more {symbol}, send this link to your friends to receive {per_ref} {symbol} per each referral {ref_link}'
    withdraw: str = 'Token will be distributed on {date}'
    task_complete: str = 'Task completed ✅'
    task_completed_already: str = 'You have already completed this task'
    
    
                            
class AirdropConfig(BaseModel):
    name: str = None
    symbol: str = None
    website_link: str = None
    twitter_link: str = None
    retweet_post_link: str = None
    group_username: str = None
    channel_username: str = None
    airdrop_status: bool = None
    registration_amount: int = None
    referral_amount: int = None
    extral_reward: int = None
    min_referrals: int = None
    max_referrals: int = None
    withdraw_date: str = None
    send_error_message: bool = None
    send_error_to: str = None
    language_code: str = None
    invalid : str= None
    airdrop_closed_message: str = None
    config: str = None
    airdrop_rules: str = None
    reteet_post: str = None
    join_channel: str = None
    not_in_channel: str = None
    welcome_message: str = None
    not_bot_msg: str = None
    join_group_msg: str = None
    not_in_group_msg: str = None
    ban_from_group_msg: str = None
    ban_from_channel_msg: str = None
    ans_captcha: str = None
    wrong_captcha: str = None
    captcha_verified: str = None
    reply_captcha: str = None
    submit_wallet: str = None
    wallet_used: str = None
    wallet_saved: str = None
    wallet_removed: str = 'Wallet removed 🙈'
    no_wallet_found: str = 'No wallet found'
    reply_wallet_request: str = None
    submit_email : str = None
    email_used : str = None
    email_saved : str = None
    email_removed: str = 'Your email has been removed'
    no_email_found: str = 'No email found'
    reply_email_request : str = None
    submit_twitter_link : str= None
    twitter_used : str = None
    twitter_saved: str = None
    reply_twitter_request: str = None
    account_created: str = None
    dashboard: str = None
    balance: str = None
    referral_link: str = None
    withdraw: str = None
    task_complete: str = 'Task completed ✅'
    task_completed_already: str = None
    

class AirdropLangUpdateID(BaseModel):
    key: str = None
    language_code: str = 'en'
    invalid : int = None
    airdrop_closed_message: int = None 
    config: int = None 
    airdrop_rules: int = None 
    reteet_post: int = None
    join_channel: int = None 
    not_in_channel: int = None 
    welcome_message: int = None 
    not_bot_msg: int = None 
    join_group_msg: int = None 
    not_in_group_msg: int = None 
    ban_from_group_msg: int = None 
    ban_from_channel_msg: int = None 
    ans_captcha: int = None 
    wrong_captcha: int = None 
    captcha_verified: int = None 
    reply_captcha: int = None 
    submit_wallet: int = None 
    wallet_used: int = None 
    wallet_saved: int = None 
    wallet_removed: int = None
    no_wallet_found: int = None
    reply_wallet_request: int = None 
    submit_email : int = None 
    email_used : int = None 
    email_saved : int = None
    email_removed: int = None 
    no_email_found: int = None
    reply_email_request : int = None 
    submit_twitter_link : int = None
    twitter_used : int = None 
    twitter_saved: int = None 
    reply_twitter_request: int = None 
    account_created: int = None 
    dashboard: int = None 
    balance: int = None 
    referral_link: int = None 
    withdraw: int = None 
    task_complete: int = None
    task_completed_already: int = None
    

class InGroupCannellStatus(BaseModel):
    in_group: bool = False
    in_channel: bool = False