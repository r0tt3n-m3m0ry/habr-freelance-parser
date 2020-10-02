#!/usr/bin/python3
# Habr freelance parser
# Created by r0tt3n-m3m0ry

import logging # thanks to @MadNike ;>
import sqlite3
import random
import time
import os

try:
	from bs4 import BeautifulSoup as bs
	import requests
	import vk_api

	if os.name == 'nt':
		import plyer # system notifications 
except:
	print('Установите необходимые модули командой \'$ pip3 install -r requirements.txt\' перед запуском скрипта'); exit()

def send_message(vk, receiver_id, content):
	vk.messages.send(user_id=receiver_id, random_id=random.randint(-999999999999, 999999999999), message=content)

def update_receivers_id():
	global vk_receivers_ids
	vk_receivers_ids = []

	with open('receivers.txt') as file_receivers:
		for vk_receiver_id in file_receivers:
			if vk_receiver_id[0] != '#' and vk_receiver_id.strip() != '': 
				vk_receivers_ids.append(vk_receiver_id.strip())

delay = 450

vk_token = '2782fbc696d53906eabb6522aea6512cb88ddb546f1f498fc86cb8598766e11ed1d18cad659e2924b4827'

logging.basicConfig(format='\n[%(asctime)s] %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

db = sqlite3.connect('parser.db')
sql = db.cursor()

sql.execute('''CREATE TABLE IF NOT EXISTS habr (title TEXT, price TEXT, link TEXT)''')
db.commit()

try:
	vk_session = vk_api.VkApi(token=vk_token)
	vk = vk_session.get_api()

	while True:
		update_receivers_id()

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

				# plyer.notification.notify(app_name='Habr Freelance Parser', title='Habr Freelance Parser', message=f'Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}')

				for vk_receiver_id in vk_receivers_ids:
					try:
						send_message(vk, vk_receiver_id, f"Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}")
						logging.error(f'Отправлено сообщение для vk.com/id{vk_receiver_id}')
					except:
						logging.error(f'Не удалось отправить сообщение для vk.com/id{vk_receiver_id}')

				logging.info(f"Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}")

				time.sleep(10)

		logging.info('Ждем следующие заказы...')
		time.sleep(delay)

except KeyboardInterrupt:
	print('\nДо встречи :D\n'); exit()
