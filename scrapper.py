import argparse
import bs4 as bs
import re
from pprint import pprint
import urllib.request
from dateutil.parser import parse
import psycopg2

keywords = [

]

def make_link(static_link):
	date = input("Enter the date (DD.MM.YYYY): ")
	input_date = parse(date, dayfirst=True).strftime("%d.%m.%y")

	res = static_link + "?date=" + input_date
	#print(date)
	#print(input_date)
	#print(res)

	return res

def make_link_month(static_link):
	date = input("Enter the month (MM.YYYY): ")
	input_date = parse(date).strftime("%m.%y")
	res = static_link + "?date=" + input_date
	return res

def scrap(monthly):
	calendar_link = 'https://stat.gov.kz/ru/release-calendar'
	site_link = 'https://stat.gov.kz'
	if not monthly:
		full_link = make_link(static_link=calendar_link)
	else:
		full_link = make_link_month(static_link=calendar_link)
	source = urllib.request.urlopen(full_link).read()
	soup = bs.BeautifulSoup(source, 'lxml')
	list = []
	for event in soup.find_all('div', class_ = 'calendar-event'):
		title = event.find('a', class_ = 'calendar-event-title')
		link = event.find('a', class_ = 'calendar-event-title')
		type = event.find('div', class_ = 'calendar-event-type').get_text(strip=True)
		date = event.find('div', class_ = 'calendar-event-day').get_text(strip=True)
		if title is None:
				title = event.get_text(strip=True)
		if link is not None:
			title = title.get_text(strip=True)
			link = site_link + link.get('href')

		list.append({"title": title, "link": link, "type": type, "date": date})
	#for a in list:
	#	print(a)
	#	print("-------------------")
	return list

def filter(list):
	res = []

	#for event in list:
		#if event['title']

	return res

def send_to_bd(list):
	conn = psycopg2.connect('dbname=test user=postgres password=postgres')
	cur = conn.cursor()
	#cur.execute('CREATE TABLE Test (id serial PRIMARY KEY, title varchar, link varchar, type varchar, date varchar);')
	for event in list:
		cur.execute('INSERT INTO Test (title, link, type, date) VALUES (%s, %s, %s, %s)',
				 (event['title'], event['link'], event['type'], event['date']))

	cur.execute('SELECT * FROM Test;')
	cur.fetchone()
	conn.commit()
	cur.close()
	conn.close()
	return 0

def scrap_send(monthly):
	list = scrap(monthly)
	if len(list) == 0:
		return -1
	pprint('Found {} event(s), sending to BD...'.format(len(list)))	
	send_to_bd(list=list)
	return 0

def main():
	monthly = False
	parser = argparse.ArgumentParser()
	parser.add_argument('-m', '--monthly', help='Scrap by months')
	args = parser.parse_args()
	if args.monthly is not None:
		monthly = True
	scrap_send(monthly)
	return 0

if __name__ == "__main__":
	main()