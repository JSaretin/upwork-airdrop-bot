from bot.user_handlers import *
from bot.admin_handlers import *

# Users handlers
bot.register_message_handler(start, commands=['start'])
bot.register_callback_query_handler(accept_terms_callback_handler, func=lambda call: call.data == 'accept_terms')
bot.register_message_handler(confirm_verification_handler, regexp='^[0-9]+$')
bot.register_message_handler(register_address_handler, regexp='^0[xX][0-9a-fA-F]{40}$')
bot.register_message_handler(twitter_link_submition_handler, regexp='^https://twitter.com/[a-zA-Z0-9_]{3,30}$')
bot.register_message_handler(register_email_handler, regexp='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
bot.register_callback_query_handler(check_user_in_group_handler, func=lambda call: call.data == 'joined_group')
bot.register_callback_query_handler(check_user_in_channel_handler, func=lambda call: call.data == 'joined_channel')



# Admin handlers
bot.register_message_handler(get_users_stats, regexp='^Users$')
bot.register_message_handler(export_users_data_to_csv, regexp='^Export$')
bot.register_message_handler(get_available_config_commands, regexp='^Settings$')
bot.register_message_handler(get_available_config_commands, regexp='^settings$')
bot.register_message_handler(get_available_config_commands, commands=['settings'])


# Airdrop confirms
bot.register_message_handler(request_welcome_message, commands=["set_welcome_message"])
bot.register_message_handler(request_request_twitter_post_retweet_message, commands=["set_request_twitter_post_retweet_message"])
bot.register_message_handler(request_twitter_post_retweet_link_message, commands=["set_twitter_post_retweet_link_message"])
bot.register_message_handler(request_group_message, commands=["set_group_message"])
bot.register_message_handler(request_channel_message, commands=["set_channel_message"])
bot.register_message_handler(request_enter_address_message, commands=["set_enter_address_message"])
bot.register_message_handler(request_address_already_used_message, commands=["set_address_already_used_message"])
bot.register_message_handler(request_address_save_message, commands=["set_address_save_message"])
bot.register_message_handler(request_enter_email_message, commands=["set_enter_email_message"])
bot.register_message_handler(request_email_already_used_message, commands=["set_email_already_used_message"])
bot.register_message_handler(request_email_save_message, commands=["set_email_save_message"])
bot.register_message_handler(request_enter_twitter_username_message, commands=["set_enter_twitter_username_message"])
bot.register_message_handler(request_twitter_username_already_used_message, commands=["set_twitter_username_already_used_message"])
bot.register_message_handler(request_twitter_username_save_message, commands=["set_twitter_username_save_message"])
bot.register_message_handler(request_enter_verification_code_message, commands=["set_enter_verification_code_message"])
bot.register_message_handler(request_wrong_verification_code_message, commands=["set_wrong_verification_code_message"])
bot.register_message_handler(request_invalid_message_message, commands=["set_invalid_message_message"])
bot.register_message_handler(request_captcha_message, commands=["set_captcha_message"])
bot.register_message_handler(request_dashboard_message, commands=["set_dashboard_message"])
bot.register_message_handler(request_join_group_message, commands=["set_join_group_message"])
bot.register_message_handler(request_join_channel_message, commands=["set_join_channel_message"])
bot.register_message_handler(request_ban_from_group_message, commands=["set_ban_from_group_message"])
bot.register_message_handler(request_ban_from_channel_message, commands=["set_ban_from_channel_message"])
bot.register_message_handler(request_reply_to_address_request_message, commands=["set_reply_to_address_request_message"])
bot.register_message_handler(request_reply_to_email_request_message, commands=["set_reply_to_email_request_message"])
bot.register_message_handler(request_airdrop_rules_message, commands=["set_airdrop_rules_message"])


bot.register_message_handler(set_airdrop_confirg)

# Unhandled handlers
bot.register_message_handler(handle_invalid_message)