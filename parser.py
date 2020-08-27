#!/usr/bin/python3
# Habr freelance parser
# Created by r0tt3n-m3m0ry

try:
	from bs4 import BeautifulSoup as bs
	import requests
	import vk_api
except:
	print('Установите необходимые модули командой \'$ pip3 install -r requirements.txt\' перед запуском скрипта'); exit()

import sqlite3
import random
import time
import os

def send_message(vk, receiver_id, content):
	vk.messages.send(user_id=receiver_id, random_id=random.randint(-999999999999, 999999999999), message=content)

delay = 900

db = sqlite3.connect('parser.db')
sql = db.cursor()

sql.execute('''CREATE TABLE IF NOT EXISTS habr (title TEXT, price TEXT, link TEXT)''')
db.commit()

vk_session = vk_api.VkApi(login=os.getenv('vk_phone'), password=os.getenv('vk_pass'), app_id='2685278')
vk_session.auth()

vk = vk_session.get_api()

print('VK...ok')

while True:
	habr = bs(requests.get('https://freelance.habr.com/tasks').text, 'html.parser')
	tasks = habr.find_all('li', {'class': 'content-list__item'})

	for task in tasks:
		title = task.find('a').text

		try:
			price = f"{task.find('span', {'class': 'count'}).text}"
		except:
			price = 'договорная'

		link = 'https://freelance.habr.com' + task.find('a', href=True)['href']

		if (title, price, link) not in sql.execute('''SELECT * FROM habr'''):
			sql.execute('''INSERT INTO habr VALUES (?, ?, ?)''', (title, price, link))
			db.commit()

			send_message(vk, 565312948, f'Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}')

			print(f'Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}')

			time.sleep(3)

	print(f'Жду {int(delay/60)} минут...')
	time.sleep(delay)