from bs4 import BeautifulSoup
import requests
import csv
import json

end_of_url = input('Напишите окончание ссылки на коллекцию из Читай-города: ')
url = 'https://www.chitai-gorod.ru/collections/' + end_of_url

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'
}

response = requests.get(url=url, headers=headers)
bs = BeautifulSoup(response.text, 'lxml')

pages = bs.find('div', class_='pagination__wrapper').find_all('div', class_='pagination__button')
max_page = int(pages[-2].text)

list_books = []

for page in range(1, max_page + 1):

    print(f'Собираем книги со страниц: {page} из {max_page}')

    response = requests.get(url=f'https://www.chitai-gorod.ru/collections/o-druzhbe-lyudey-i-zhivotnyh-265?page={page}',
                            headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')
    links_books = bs.find_all('a', class_='product-card__title')

    for link in links_books:
        list_books.append('https://www.chitai-gorod.ru' + link.get('href'))

books_characteristics = ['Название', 'Автор', 'Рейтинг', 'Старая цена', 'Новая цена', 'Издательство', 'Год издания',
                         'ISBN', 'Обложка', 'Описание']

with open('books.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(books_characteristics)


def check(*args):
    try:
        key = bs.find(args[0], class_=args[1]).text
        return key
    except AttributeError:
        return 'Отсутствует'


books_dict_for_json = {}
book_number_for_json = 0
for book in list_books:

    book_number_for_json += 1

    print(f'Обрабатываем информацию о книгах: {book_number_for_json} из {len(list_books)}')

    response = requests.get(url=book, headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')

    book_name = check('h1', 'app-title app-title--mounted product-detail-title__header app-title--header-4').strip()
    author = check('a', 'product-detail-title__author').strip()
    rating = check('span', 'box-none').strip().split(' ')[0]

    if not (rating.isalpha()):
        if float(rating) > 5.0:
            rating = 'Отсутствует'

    try:
        new_price = bs.find('span',
                            class_='product-detail-offer-header__price-currency product-detail-offer-header__price-currency--sale').text.strip()
        old_price = bs.find('span', class_='product-detail-offer-header__old-price').text.strip()
    except AttributeError:
        new_price = check('span', 'product-detail-offer-header__price-currency').strip()
        old_price = 'Отсутствует'

    book_cover = bs.find('img', class_='product-gallery__image').get('src')
    description = check('div', 'product-detail-additional__description').strip()
    book_info = [book_name, author, rating, old_price, new_price, book_cover, description]

    characteristics = bs.find_all('div', class_='product-detail-characteristics__item')

    for item in characteristics:
        key_characteristics = item.find('span', class_='product-detail-characteristics__item-title').text.strip()
        try:
            value_characteristics = item.find('span', class_='product-detail-characteristics__item-value').text.strip()
        except AttributeError:
            value_characteristics = item.find('a',
                                              class_='product-detail-characteristics__item-value product-detail-characteristics__item-value--link').text.strip()
        if key_characteristics in books_characteristics:
            book_info.insert(-2, value_characteristics)

    books_dict_for_json[book_number_for_json] = {
        'Название книги': book_info[0],
        'Автор': book_info[1],
        'Рейтинг': book_info[2],
        'Старая цена': book_info[3],
        'Новая цена': book_info[4],
        'Издательство': book_info[5],
        'Год издания': book_info[6],
        'ISBN': book_info[7],
        'Обложка': book_info[8],
        'Описание': book_info[9],
    }
    with open('books.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(book_info)

with open('books.json', 'a', encoding='utf-8') as file:
    json.dump(books_dict_for_json, file, indent=4, ensure_ascii=False)

print('Готово\N{fire}')
