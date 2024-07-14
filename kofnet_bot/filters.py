from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter
from telebot.types import Message
from kofnet_bot.config import bot_config
from telebot import TeleBot, types


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


class ForceSubscribeFilter(AdvancedCustomFilter):
    """Check that a user is a member of a certain channel"""

    key: str = "force_sub"

    def __init__(self, channel_id: int, channel_url: str, bot: TeleBot):
        """Constructor

        Args:
            channel_id (int): Channek id to check from.
            channel_url (str): Link to the telegram channel.
            bot (TeleBot): Bot instance.
        """
        self.channel_id = channel_id
        self.bot = bot
        self.channel_url = str(channel_url)

    def check(self, message: Message, text: bool):
        if not text:
            return True

        if message.chat.type == "private":
            try:
                check_membership = self.bot.get_chat_member(
                    self.channel_id, message.from_user.id
                )
                print(check_membership)
                if check_membership:
                    return True
            except:
                pass
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("Subcribe 🔔", url=self.channel_url))
            self.bot.reply_to(
                message,
                f"Hello {message.from_user.username}.\nIn order to use this service you have to subscribe to our channel.",
                reply_markup=markup,
            )
        return False
