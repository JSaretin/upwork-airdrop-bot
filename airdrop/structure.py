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
    referral_balance: float = 0
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
    

class AirdropConfig(BaseModel):
    key: str = None
    language_code: str = 'en'
    airdrop_status: bool = False
    registration_amount: float = 500
    referral_amount: float = 50
    
    min_referrals: int = 5
    max_referrals: int = None
    
    name: str = 'Versity'
    symbol: str = '$SITY'
    website_link: str = 'https://helloversity.io'
    twitter_link: str = 'https://twitter.com/helloversity'
    retweet_post_link: str = 'https://twitter.com/helloversity/status/1234'
    group_username: str = '@Validationgrouptg'
    channel_username: str = '@validatonchanneltg'
    
    send_error_message: bool = True
    send_error_to: str = '@lovelynCertk'
    
    airdrop_closed_message: str = 'Airdrop is closed'
    
    welcome_message: str = 'Welcome to the Airdrop Bot!'
    not_bot_msg: str = 'enter the answer to the captcha'
    join_group_msg: str = 'Join group to continue'
    not_in_group_msg: str = 'You are not in the group\np.s. join the group to continue'

    join_channel_msg: str = 'Join channel to continue'
    not_in_channel_msg: str = 'You are not in the channel\np.s. join the channel to continue'
    
    
    ban_from_group_msg: str = 'You are banned from group'
    ban_from_channel_msg: str = 'You are banned from channel'
    
    enter_verification_code_msg: str = 'Please enter the verification code'
    wrong_verification_code_msg: str = 'Wrong verification code'
    verification_code_saved_msg: str = 'Your verification code has been saved'
    reply_to_verification_code_request_msg: str = 'To prove your are not a bot, reply to the verification answer request message or claick /start to get a new request'

    address_exists_msg: str = 'Your address already exists, click /request_address to set a new one'
    enter_wallet_address_msg: str = 'Please enter your Polygon address'
    wallet_taken_msg: str = 'This wallet is registered to another account'
    wallet_saved_msg: str = 'You wallet address has been saved'
    reply_to_wallet_request_msg: str = 'To register your wallet address, reply to the wallet request message or claick /start to get a new request'
    
    email_exists_msg: str = 'Your email already exists, click /request_email to set a new one'
    enter_email_msg: str = 'Please enter your email address'
    email_taken_msg: str = 'This email is registered to another user'
    email_saved_msg: str = 'Your email address have been registered'
    reply_to_email_request_msg: str = 'To register your email, reply to the email request message or claick /start to get a new request'
    
    enter_twitter_link_msg : str= 'Please enter your twitter profile like\nlink must start with https://'
    twitter_username_taken : str = 'This account is registered to another user'
    twitter_username_saved: str = 'Your twitter username has been registerd'
    reply_to_twitter_link_request_msg: str = 'To register your twitter username, reply to the twitter link request message or claick /start to get a new request'
    
    registration_complete_msg: str = 'Congratulations!🎊\naccount created successfully'
    
    dashboard_msg: str = 'Welcome to the dashboard'

    balance_msg: str = '*Balance*: {balance}\n*Referral Balance*: {referral_balance}\n*Total Balance*: {total_balance}\n*Referral Counts*: {referral_counts}'
    referral_link_msg: str = 'To earn more {symbol}, send this link to your friends to receive {referral_amount} {symbol} per each referral {link}'

    withdraw_msg: str = 'Token will be distributed on {withdraw_date}'
    withdraw_date: str = '30 June 2022'
    
    invalid_message : str= 'Invalid message'
    airdrop_rules_msg: str = 'Submit your wallet and email'
    terms_msg: str = 'airdrop terms'
    
                            
    
    


    
class AirdropConfigMessageIDS(BaseModel):
    key: str = None
    airdrop_status: int = None
    registration_amount: int = None
    referral_amount: int = None
    min_referrals: int = None
    max_referrals: int = None
    name: int = None
    symbol: int = None
    website_link: int = None
    twitter_link: int = None
    group_username: int = None
    channel_username: int = None
    send_error_message: int = None
    send_error_to: int = None
    airdrop_closed_message: int = None
    welcome_message: int = None
    not_bot_msg: int = None
    join_group_msg: int = None
    not_in_group_msg: int = None
    join_channel_msg: int = None
    not_in_channel_msg: int = None
    ban_from_group_msg: int = None
    ban_from_channel_msg: int = None
    enter_verification_code_msg: int = None
    wrong_verification_code_msg: int = None
    verification_code_saved_msg: int = None
    reply_to_verification_code_request_msg: int = None
    address_exists_msg: int = None
    enter_wallet_address_msg: int = None
    wallet_taken_msg: int = None
    wallet_saved_msg: int = None
    reply_to_wallet_request_msg: int = None
    email_exists_msg: int = None
    enter_email_msg: int = None
    email_taken_msg: int = None
    email_saved_msg: int = None
    reply_to_email_request_msg: int = None
    enter_twitter_link_msg : int = None
    twitter_username_taken : int = None
    twitter_username_saved: int = None
    reply_to_twitter_link_request_msg: int = None
    registration_complete_msg: int = None
    dashboard_msg: int = None
    balance_msg: int = None
    referral_link_msg: int = None
    invalid_message: int = None
    airdrop_rules_msg: int = None
    terms_msg: int = None
    
    fr_send_error_message: int = None
    fr_send_error_to: int = None
    fr_airdrop_closed_message: int = None
    fr_welcome_message: int = None
    fr_not_bot_msg: int = None
    fr_join_group_msg: int = None
    fr_not_in_group_msg: int = None
    fr_join_channel_msg: int = None
    fr_not_in_channel_msg: int = None
    fr_ban_from_group_msg: int = None
    fr_ban_from_channel_msg: int = None
    fr_enter_verification_code_msg: int = None
    fr_wrong_verification_code_msg: int = None
    fr_verification_code_saved_msg: int = None
    fr_reply_to_verification_code_request_msg: int = None
    fr_address_exists_msg: int = None
    fr_enter_wallet_address_msg: int = None
    fr_wallet_taken_msg: int = None
    fr_wallet_saved_msg: int = None
    fr_reply_to_wallet_request_msg: int = None
    fr_email_exists_msg: int = None
    fr_enter_email_msg: int = None
    fr_email_taken_msg: int = None
    fr_email_saved_msg: int = None
    fr_reply_to_email_request_msg: int = None
    fr_enter_twitter_link_msg : int = None
    fr_twitter_username_taken : int = None
    fr_twitter_username_saved: int = None
    fr_reply_to_twitter_link_request_msg: int = None
    fr_registration_complete_msg: int = None
    fr_dashboard_msg: int = None
    fr_balance_msg: int = None
    fr_referral_link_msg: int = None
    fr_invalid_message: int = None
    fr_airdrop_rules_msg: int = None
    fr_terms_msg: int = None
    
    brodecast_msg: int = None
    
    

    


class InGroupCannellStatus(BaseModel):
    in_group: bool = False
    in_channel: bool = False