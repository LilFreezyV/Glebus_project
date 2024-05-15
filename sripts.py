import datetime
import requests
import json
import pandas as pd
from retry import retry
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


def get_feedback(url):
    const = ['ма', 'июн', 'июл', 'август', 'сентябр', 'октябр', 'ноябр', 'декабр', 'январ', 'феврал', 'март', 'апрел', 'сегодня', 'вчера']
    service = Service()  # указываем путь до драйвера
    browser = webdriver.Chrome(service=service)
    browser.get(url)
    time.sleep(2)
    review = browser.find_element(By.CLASS_NAME, 'product-feedbacks__main')
    if len(review.text.split(' ')[0]) > 0:
        text = review.text.split()[14:]
        for el in text:
            for i in const:
                if i in el.lower():
                    index = text.index(el)
                    del text[index]
                    del text[index - 1]
        for el in text:
            if len(el.split(':')) == 2:
                del text[text.index(el)]
        return ' '.join(text)
    return 'У данного товара нет отзывов'

    time.sleep(10)
    browser.quit()


'''def get_description(url):
    url = url
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    result = []
    # Находим все элементы div с классом item-description-text
    ds = soup.findAll('div', class_='wrapper')

    # Перебираем такие дивы (Скорее всего он будет один, но кто его знает...)
    for d in ds:
        # Так же перебираем все параграфы и заполняем result их значениями
        for p in d.findAll():
            result.append(p.text.lstrip().rstrip())

    # Джойним все в одну строку
    return ' '.join(result)'''


def get_data_by_sku(sku: int) -> dict:
    """получаем данные о товаре по артикулу"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.wildberries.ru",
        'Content-Type': 'application/json; charset=utf-8',
        'Transfer-Encoding': 'chunked',
        "Connection": "keep-alive",
        'Vary': 'Accept-Encoding',
        'Content-Encoding': 'gzip',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1257786&nm={sku}'
    r = requests.get(url, headers=headers)
    return r.json()


def get_data_from_json(json_file: dict) -> list:
    """извлекаем из json данные"""
    data_list = []
    try:
        data = json_file['data']['products'][0]
        sku = data.get('id')
        name = data.get('name')
        price = int(data.get("priceU") / 100)
        salePriceU = int(data.get('salePriceU') / 100)
        sale = data.get('sale')
        brand = data.get('brand')
        rating = data.get('rating')
        supplier = data.get('supplier')
        supplierRating = data.get('supplierRating')
        feedbacks = data.get('feedbacks')
        reviewRating = data.get('reviewRating')
        promoTextCard = data.get('promoTextCard')
        promoTextCat = data.get('promoTextCat')
        data_list.append({
            'id': sku,
            'name': name,
            'price': price,
            'salePriceU': salePriceU,
            'sale': sale,
            'brand': brand,
            'rating': rating,
            'supplier': supplier,
            'supplierRating': supplierRating,
            'feedbacks': feedbacks,
            'reviewRating': reviewRating,
            'promoTextCard': promoTextCard,
            'promoTextCat': promoTextCat,
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/feedbacks'
        })
        return data_list
    except Exception:
        pass


def save_excel(data: list, filename: str):
    """сохранение результата в excel файл"""
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(f'{filename}.xlsx')
    df.to_excel(writer, sheet_name='data', index=False)
    writer.close()
    print(f'Все сохранено в {filename}.xlsx\n')


def parser(sku: int):
    """основная функция"""
    data = get_data_by_sku(sku)
    data_list = get_data_from_json(data)
    save_excel(data_list, f'data_by_sku_{sku}')
    return data_list


def main(_id: str, _url: str):
    _id = _id  # артикул товара
    start = datetime.datetime.now()  # запишем время старта
    data = parser(_id)
    print(data)

    end = datetime.datetime.now()  # запишем время завершения кода
    total = end - start  # расчитаем время затраченное на выполнение кода
    print("Затраченное время:" + str(total))
    return data[0]['name'], data[0]['price'], data[0]['reviewRating'], data[0]['link'], get_feedback(_url)[:500]

print(get_feedback('https://www.wildberries.ru/catalog/176186929/feedbacks?imtId=160892001'))
