from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message
from kofnet_bot.config import bot_config


class IsAdminFilter(SimpleCustomFilter):
    """Checks if user is bot's admin"""

    key: str = "is_admin"

    @staticmethod
    def check(message: Message):
        return (
            False
            if message.chat.type != "private" or bot_config.admin_id is None
            else message.from_user.id == bot_config.admin_id
        )
