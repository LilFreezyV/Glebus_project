import telebot
from sripts import main

bot = telebot.TeleBot("7169387893:AAEJtsF1C1oXTSX5rbvlBiipr7mjn4jMhGY")


@bot.message_handler(commands=["start"])
def start(message):
    mess = f"Здравствуйте, {message.from_user.first_name}!"
    bot.send_message(message.chat.id, mess)

    bot.send_photo(message.chat.id, 'https://frankmedia.ru/wp-content/uploads/2022/05/94e9090917c1.png')
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(mess + '\n')
        f.close()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    sentence = message.text
    _str = sentence[8:]
    data = _str.split('/')
    article = data[2]
    url = sentence
    try:
        name, price, rating, link, feedbacks = main(article, url)
        bot_reply = f'Название товара: {name}\nЦена: {price}\nРейтинг: {rating}\nТекст отзывов: {feedbacks}'
    except Exception as err:
        bot_reply = f'Товар не найден, проверьте правильность введенных данных ({str(err)})'
    bot.send_message(message.chat.id, bot_reply)


bot.polling(none_stop=True)
