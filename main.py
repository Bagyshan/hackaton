import requests
from bs4 import BeautifulSoup as BS
import telebot
import datetime
from telebot import types

def get_html(url):
    response = requests.get(url) 
    return response.text


def get_data(html, max_items):
    buttons = []
    data = {}
    counter = 1
    soup = BS(html, 'lxml')
    catalog = soup.find('div', class_='Tag--articles')
    news = catalog.find_all('div', class_='Tag--article')
    for i in news:
        if counter <= max_items:
            dict_ = {}
            dict_.update({'title' :i.find('a', class_='ArticleItem--name').text.strip('\r').strip('\n').strip(' ')})
            dict_.update({'image': i.find('a', class_="ArticleItem--image").find("img").get("src")})
            url = i.find('a', class_='ArticleItem--name').get('href')
            html1 = get_html(url)
            soup1 = BS(html1, 'lxml')
            catalog1 = soup1.find('div', class_='Article--text').find('p').text
            dict_.update({'opisanie':catalog1})
            data.update({counter: dict_})
            counter+=1
    return data

def news_today():
    date_time = datetime.datetime.now()
    date = str(date_time)[:10]
    url = f'https://kaktus.media/?lable=8&date={date}&order=time'
    return url



bot = telebot.TeleBot('6486125148:AAGVKRu6HbjayT8v2r3-HV7xHcDljyjrH8I')

user_data = {} 
 
CHOOSING, TYPING_REPLY = range(2) 
 
@bot.message_handler(commands=['start']) 
def start(message):
    user_data.clear() 
    bot.send_message(message.chat.id, "Привет! Я Телеграм-бот. Нажмите /getnews, чтобы получить новости.") 
    user_data[message.chat.id] = {'state': CHOOSING} 
 
@bot.message_handler(commands=['getnews']) 
def get_news(message): 
    html = get_html(news_today()) 
    article_data = get_data(html, max_items=20) 
 
    if article_data: 
        user_data[message.chat.id]['article_data'] = article_data 
        user_data[message.chat.id]['chosen_news'] = None 
        user_data[message.chat.id]['state'] = TYPING_REPLY 
 
        reply_keyboard = telebot.types.InlineKeyboardMarkup() 
 
        for i, article in article_data.items():
            button = telebot.types.InlineKeyboardButton(f"{i}. {article['title']}", callback_data=f"more_info_{i}") 
            reply_keyboard.add(button) 
 
        bot.send_message(message.chat.id, "Выберите новость:", reply_markup=reply_keyboard) 
    else: 
        bot.send_message(message.chat.id, "Извините, новости не найдены.") 
 
@bot.callback_query_handler(func=lambda call: call.data.startswith("more_info_")) 
def choose_news(call): 
    chosen_index = int(call.data.split("_")[2])
    article_data = user_data[call.message.chat.id]['article_data']
    chosen_news = article_data[chosen_index]
    bot.send_photo(call.message.chat.id, chosen_news['image'], caption=chosen_news['opisanie'])



bot.polling()

