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
    balance: float = 0
    referral_link: str = None
    referrals: int = 0
    is_admin: bool = False
    language_code: str = 'en'
    registration_complete: bool = False
    retweeted: bool = False
    language_set: bool = False
    group_status: int = 0
    channel_status: int = 0
    
    
class MessageIds(BaseModel):
    key: str = None
    user_id: str
    captcha_msg_id: int = None
    address_request_msg_id: int = None
    email_request_msg_id: int = None
    twitter_username_request_msg_id: int = None
    

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
    


    
class AirdropConfigMessageIDS(BaseModel):
    key: str = None
    welcome_msg_id: int = None
    request_twitter_post_retweet_msg_id: int = None
    twitter_post_retweet_link_msg_id: int = None
    group_msg_id: int = None
    channel_msg_id: int = None
    registration_amount_msg_id: int = None
    referral_amount_msg_id: int = None
    min_referrals_msg_id: int = None
    max_referrals_msg_id: int = None
    enter_address_msg_id: int = None
    address_already_used_msg_id: int = None
    address_save_msg_id: int = None
    enter_email_msg_id: int = None
    email_already_used_msg_id: int = None
    email_save_msg_id: int = None
    enter_twitter_username_msg_id: int = None
    twitter_username_already_used_msg_id: int = None
    twitter_username_save_msg_id: int = None
    twitter_post_retweet_link_id: int = None
    enter_verification_code_msg_id: int = None
    wrong_verification_code_msg_id: int = None
    invalid_message_msg_id: int = None
    captcha_msg_id: int = None
    dashboard_msg_id: int = None
    join_group_msg_id: int = None
    join_channel_msg_id: int = None
    ban_from_group_msg_id: int = None
    ban_from_channel_msg_id: int = None
    reply_to_address_request_msg_id: int = None
    reply_to_email_request_msg_id: int = None
    airdrop_rules_msg_id: int = None
    referral_link_msg_id: int = None
    airdrop_puased_msg_id: int = None
    airdrop_status_msg_id: int = None
    
    
class AirdropConfig(BaseModel):
    key: str = None
    welcome_message: str = 'Welcome to the Airdrop!'
    request_twitter_post_retweet_message: str = 'Please retweet the following tweet to get your first referral: {}'
    twitter_post_retweet_link_message: str = 'Please retweet the following tweet to get your first referral: {}'
    group_message: str = 'Please join the group to get your first referral: {}'
    channel_message: str = 'Please join the channel to get your first referral: {}'
    registration_amount: float = 0.1
    referral_amount: float = 0.1
    min_referrals: int = 1
    max_referrals: int = 10
    enter_address_message: str = 'Please enter your Polygon address'
    address_already_used_message: str = 'This address is already used'
    address_save_message: str = 'Your address has been saved'
    enter_email_message: str = 'Please enter your email address'
    email_already_used_message: str = 'This email is already used'
    email_save_message: str = 'Your email has been saved'
    enter_twitter_username_message: str = 'Please enter your Twitter username'
    twitter_username_already_used_message: str = 'This Twitter username is already used'
    twitter_username_save_message: str = 'Your Twitter username has been saved'
    twitter_post_retweet_link: str = 'https://twitter.com/intent/retweet?tweet_id={}'
    enter_verification_code_message: str = 'Please enter the verification code'
    wrong_verification_code_message: str = 'Wrong verification code'
    invalid_message_message: str = 'Invalid message'
    captcha_message: str = 'Please solve the captcha'
    dashboard_message: str = 'User dashboard'
    join_group_message: str = 'Please join group to continue'
    join_channel_message: str = 'Please join channel to continue'
    ban_from_group_message: str = 'You have been banned from this group'
    ban_from_channel_message: str = 'You have been banned from this channel'
    reply_to_address_request_message: str = 'Please reply to the address request message or click /start to get a new one'
    reply_to_email_request_message: str = 'Please reply to the email request message or click /start to get a new one'
    airdrop_rules_message: str = '''*Airdrop rules:*

The airdrop is divided into two parts:
1. Registration
2. Referral
'''    
    referral_link_message: str = 'Your referral link: {}'
    airdrop_puased_message: str = 'Airdrop is currently paused'
    airdrop_status: bool = False
    group_username: str = '@Validationgrouptg'
    channel_username: str = '@validatonchanneltg'
    
    

    


class InGroupCannellStatus(BaseModel):
    in_group: bool = False
    in_channel: bool = False