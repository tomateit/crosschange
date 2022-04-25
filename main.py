import telebot

import regex as re
import logging

from settings import settings

from schemas import User, Currency, Stage

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(settings.BOT_TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN
memory = {}



@bot.message_handler(commands=['start'])
def send_welcome(message):
    memory[message.from_user.id] = User()
    bot.reply_to(message, "I will help :). Enter a ticker for your local currency:")


@bot.message_handler(commands=['enter'])
def enter(message):
    user = memory.get(message.from_user.id)
    if not user:
        logger.warning(f"No user with id {message.from_user} in memory")
        bot.reply_to(message, "Sowwy, a vewy bad ewwor occuwed, pwease restawt the bot completely <3")
        return

    if user.stage != Stage.GET_NEW_TICKER:
        user.stage = Stage.GET_NEW_TICKER
        bot.reply_to(message, "Ok, whatever, enter a ticker")


@bot.message_handler(commands=['me'])
def me(message):
    logger.debug("Me invoked")
    user = memory.get(message.from_user.id)
    bot.reply_to(message, f"You said, that {user}")


@bot.message_handler(commands=['exchange'])
def exchange(message):
    logger.debug("Exchange invoked")
    user = memory.get(message.from_user.id)
    if not user:
        logger.warning(f"No user with id {message.from_user} in memory")
        bot.reply_to(message, "Ouch, seems I don't remember you. Press /start")
        return

    q = 1 # quantity

    if len(user.currencies) > 1:
        cur0 = user.current_currency.ticker
        cur1, cur2, *_ = list(user.currencies.values())
        response = f"""
        {cur1.ticker} <-> {cur0}
        For 1 {cur0} you can get {1/cur1.buy} {cur1.ticker}
        For 1 {cur0} you can buy {1/cur1.sell} {cur1.ticker}
        For 1 {cur1.ticker} you can get {cur1.sell} {cur0}

        {cur2.ticker} <-> {cur0}
        For 1 {cur0} you can get {1/cur2.buy} {cur2.ticker}
        For 1 {cur0} you can buy {1/cur2.sell} {cur2.ticker}
        For 1 {cur2.ticker} you can get {cur2.sell} {cur0}


        {cur1.ticker} <-> {cur2.ticker}
        For 1 {cur1.ticker} you can buy {cur1.sell/cur2.sell} {cur2.ticker}
        For 1 {cur1.ticker} you can get {cur1.buy/cur2.buy} {cur2.ticker}  
        For 1 {cur2.ticker} you can buy {cur2.sell/cur1.sell} {cur1.ticker}
        For 1 {cur2.ticker} you can get {cur2.buy/cur1.buy} {cur1.ticker}
        """
        bot.reply_to(message, response)


@bot.message_handler()
def main(message):
    if not message.content_type == "text":
        bot.reply_to(message, "Please please please, only text messages <3")
        return

    user = memory.get(message.from_user.id)
    if not user:
        logger.warning(f"No user with id {message.from_user} in memory")
        bot.reply_to(message, "Sowwy, a vewy bad ewwor occuwed, pwease restawt the bot completely <3")
        return
    
    if user.stage == Stage.GET_CURRENT_CURRENCY:
        if re.match("^\w\w\w$", message.text.strip()):
            user.current_currency = Currency(ticker=message.text.strip().upper())
            user.stage = Stage.GET_NEW_TICKER
            bot.reply_to(message, "Thanks! Now I need a foreign currency. Enter a ticker:")
        else:
            bot.reply_to(message, "Sorry, your response is not what I expect. Please, type a ticker, like USD or GBP")

    elif user.stage == Stage.GET_NEW_TICKER:
        ticker = message.text.strip().upper()
        if re.match("^\w\w\w$", ticker):
            user.currencies[ticker] = Currency(ticker=ticker)
            user.selected = user.currencies[ticker]
            user.stage = Stage.GET_VALUE
            bot.reply_to(message, f"Got ya. Now I need prices for 1 {ticker} in your currency. Enter two numbers with dots separated by space")
        else:
            bot.reply_to(message, "Sorry, your response is not what I expect. Please, type a ticker, like USD or GBP")
    elif user.stage == Stage.GET_VALUE:
        try:
            value = message.text
            buy, sell = [float(x) for x in value.split(" ")]
            user.currencies[user.selected.ticker].buy = buy
            user.currencies[user.selected.ticker].sell = sell
            user.stage = Stage.WAIT_FOR_COMMAND
            bot.reply_to(message, f"Thank you. you got {user}")
        except:
            bot.reply_to(message, "Sorry, your response is not what I expect. Please, type buy and sell values like 12.36 12.56")
    elif user.stage == Stage.WAIT_FOR_COMMAND:
        command = message.text.strip()
        logger.debug("Command: " + command)
    

bot.infinity_polling() 