#!/usr/bin/python3
# Habr freelance parser
# Created by r0tt3n-m3m0ry

try:
	from bs4 import BeautifulSoup as bs
	import requests
	import vk_api
	import plyer # system notifications 
except:
	print('Установите необходимые модули командой \'$ pip3 install -r requirements.txt\' перед запуском скрипта'); exit()

import logging # thanks to @MadNike ;>
import sqlite3
import random
import time

def send_message(vk, receiver_id, content):
	vk.messages.send(user_id=receiver_id, random_id=random.randint(-999999999999, 999999999999), message=content)

delay = 450

vk_receivers_ids = [565312948, 611876555]

logging.basicConfig(format='\n[%(asctime)s] %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

db = sqlite3.connect('parser.db')
sql = db.cursor()

sql.execute('''CREATE TABLE IF NOT EXISTS habr (title TEXT, price TEXT, link TEXT)''')
db.commit()

try:
	while True:
		try:
			vk_session = vk_api.VkApi(login=input('VK login: '), password=input('VK password: '), app_id='2685278', auth_handler = lambda: [input('VK 2FA code: '), False])
			vk_session.auth()
		except vk_api.exceptions.LoginRequired:
			print('Логин не может быть пустым!')
		except vk_api.exceptions.PasswordRequired:
			print('Пароль не может быть пустым!')
		except vk_api.exceptions.BadPassword:
			print('Неверный пароль!')
		except vk_api.exceptions.Captcha: # captcha
			print('Слишком много запросов за последнее время. Подождите 5 секунд...'); time.sleep(5)
		else:
			logging.info('VK login successful!'); break
	vk = vk_session.get_api()

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

				#for vk_receiver_id in vk_receivers_ids:
					#send_message(vk, vk_receiver_id, f"Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}")

				logging.info(f"Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}")

				plyer.notification.notify(app_name='Habr Freelance Parser', title='Habr Freelance Parser', message=f'Найден новый заказ: {title}. Стоимость работы: {price}. Ссылка: {link}')

				time.sleep(10)

		logging.info('Ждем следующие заказы...')
		time.sleep(delay)

except KeyboardInterrupt:
	print('Goodbye! :D'); exit()