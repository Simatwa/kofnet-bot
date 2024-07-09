import telebot
import kofnet
import datetime
import re
import json
from telebot import types
import kofnet_bot.config
import kofnet_bot.filters
from bs4 import BeautifulSoup

bot = telebot.TeleBot(kofnet_bot.config.bot_config.token, disable_web_page_preview=True)

usage_info = (
    "Welcome.\n"
    "Get to know SNI bug host for mobile ISPs.\n"
    "Available commands:\n\n"
    "/start - Show this help messge\n"
    "/country - Get a list of countries\n"
    "/sni - Get SNI for a particular country\n"
    "\t\te.g /sni KE\n"
    "\t\te.g /sni Malaysia\n\n"
    "Made with ❤️ by @AlphaBei from Kenya 🇰🇪"
)

bot_cache = {
    "last_update_time": datetime.datetime.now(),
    "sni_manipulator_cache": kofnet.Manipulator(),
    "stats": {"users": 0},
}


def sni_handler() -> kofnet.Manipulator:
    """Just a wrapper for keeping watch on html updates based on time"""
    cached_sni_manipulator: kofnet.Manipulator = bot_cache["sni_manipulator_cache"]
    if datetime.datetime.now() - bot_cache["last_update_time"] > datetime.timedelta(
        days=1
    ):
        bot_cache["last_update_time"] = datetime.datetime.now()
        cached_sni_manipulator.update_cache()
    return cached_sni_manipulator


def extract_text_from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def argument_required(help="Argument is required!"):
    """Decorator for ensuring a command is followed by a value

    Args:
        help (str, optional): Help message to be shown incase of none. Defaults to 'Message is required!'.
    """

    def main(func):
        def decorator(message: types.Message):
            arg = telebot.util.extract_arguments(message.text)
            if not arg:
                markup = types.InlineKeyboardMarkup()
                markup.add(inline_delete_button(message))
                return bot.reply_to(message, help, reply_markup=markup)
            else:
                return func(message, arg)

        return decorator

    return main


def inline_delete_button(message: types.Message) -> types.InlineKeyboardButton:
    """Make delete button

    Args:
        message (types.Message): Message obj

    Returns:
        types.InlineKeyboardButton: Delete button.
    """
    button = types.InlineKeyboardButton(
        text="🗑️", callback_data=f"del:{message.chat.id}:{message.id}"
    )
    return button


def inline_refresh_button(country_code: str):
    """Generate inline button for getting latest sni bug host.

    Args:
        country_code (str): Country code.
    """
    button = types.InlineKeyboardButton(text="🔄", callback_data=f"sni:{country_code}")
    return button


@bot.message_handler(commands=["start"])
def echo_usage_info(message: types.Message):
    """Display help message"""
    bot_cache["stats"]["users"] += 1
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(inline_delete_button(message))
    markup.add(
        types.InlineKeyboardButton("Contact Developer", url="https://t.me/AlphaBei")
    )

    return bot.reply_to(message, usage_info, reply_markup=markup)


@bot.message_handler(commands=["country"])
def echo_list_of_countries(message: types.Message):
    """Issue button to select countries"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    country_list: list[str] = []
    manipulator = sni_handler()
    for code in manipulator.get_code_sni_map():
        country = manipulator.get_country(code)
        if not country:
            continue
        country_list.append(
            types.InlineKeyboardButton(text=country, callback_data="sni:" + code)
        )
    markup.add(*country_list)
    markup.add(inline_delete_button(message), row_width=1)
    return bot.send_message(message.chat.id, "Select country", reply_markup=markup)


@bot.message_handler(commands=["sni"])
@argument_required()
def echo_sni_bug_host(message: types.Message, key: str):
    """Sends back sni bug host value for a particular country|code"""
    manipulator = sni_handler()
    try:
        if len(key) == 2:
            code = key
        else:
            code_country = manipulator.get_countries_code_map()
            country_code = dict(
                zip(tuple(code_country.values()), tuple(code_country.keys()))
            )
            code = country_code[key]
        sni_bug_host = manipulator.get_sni(code)
        modded_sni_bug_host = re.sub("\n$", "<br>", sni_bug_host)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(inline_refresh_button(code), inline_delete_button(message))
        markup.add(
            types.InlineKeyboardButton("Forward", switch_inline_query=f"sni {code}"),
            row_width=1,
        )
        try:
            bot.send_message(
                message.chat.id,
                modded_sni_bug_host,
                reply_markup=markup,
                parse_mode="HTML",
            )
        except telebot.apihelper.ApiTelegramException:
            plain_text = extract_text_from_html(sni_bug_host)
            bot.send_message(
                message.chat.id,
                plain_text,
                reply_markup=markup,  # parse_mode="HTML"
            )

    except KeyError:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(inline_delete_button(message))
        return bot.reply_to(
            message, "The key does not match any country/code!", reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("del:"))
def delete_button_callback_handler(call: types.CallbackQuery):
    """Deletes a sent message"""
    _, chat_id, msg_id = call.data.split(":")
    try:
        bot.delete_message(chat_id, msg_id)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as e:
        try:
            bot.delete_message(call.message.chat.id, call.message.id)
        except:
            pass
        pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("sni:"))
def refresh_sni_bug_host(call: types.CallbackQuery):
    """Updates SNI bug host sent"""
    manipulator: kofnet.Manipulator = bot_cache["sni_manipulator_cache"]
    _, code = call.data.split(":")
    try:
        sni_bug_host = manipulator.get_sni(code)
        modded_sni_bug_host = re.sub("\n$", "<br>", sni_bug_host)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(inline_refresh_button(code), inline_delete_button(call.message))
        markup.add(
            types.InlineKeyboardButton("Forward", switch_inline_query=f"sni {code}"),
            row_width=1,
        )
        try:
            bot.send_message(
                call.message.chat.id,
                modded_sni_bug_host,
                reply_markup=markup,
                parse_mode="HTML",
            )
        except telebot.apihelper.ApiTelegramException:
            plain_text = extract_text_from_html(sni_bug_host)
            bot.send_message(
                call.message.chat.id,
                plain_text,
                reply_markup=markup,  # parse_mode="HTML"
            )
    except Exception as e:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(inline_delete_button(call.message))
        bot.reply_to(
            call.message,
            text="An error occured and I couldn't complete that request!",
            reply_markup=markup,
        )


@bot.inline_handler(lambda query: query.query.startwith("sni"))
def handle_inline_query(inline_query: telebot.types.InlineQuery):
    """Send back SNI bug host at inline"""
    try:
        _, code = inline_query.query.split(" ")
        manipulator = sni_handler()
        sni_bug_text = manipulator.get_sni(code)
        country = manipulator.get_country(code)
        feedback_options = [
            telebot.types.InlineQueryResultArticle(
                id="1",
                title=f"SNI bug host for {country}",  # "AI Generated",
                input_message_content=telebot.types.InputTextMessageContent(
                    extract_text_from_html(sni_bug_text)
                ),
            )
        ]
        return bot.answer_inline_query(inline_query.id, feedback_options)

    except Exception as e:
        print(
            f"Error while handling inline query : {e.args[1] if e.args and len(e.args)>1 else e}"
        )


@bot.message_handler(commands=["stats"], is_admin=True)
def check_stats(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(inline_delete_button(message))
    return bot.send_message(
        message.chat.id,
        text=f"```json\n{json.dumps(bot_cache['stats'], indent=4)}\n```",
        parse_mode="Markdown",
        reply_markup=markup,
    )


bot.add_custom_filter(kofnet_bot.filters.IsAdminFilter())
