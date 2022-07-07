# tenderplan_test

import requests
import calendar
import datetime
import json
import sys


HOST = 'https://tenders.mts.ru/'
URL = 'https://tenders.mts.ru/api/v1/tenders'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}


"""Возвращает ответ, при ошибке печатает в консоль ее статус код."""

def get_tenders(url, headers, params=''):
    response = requests.get(url, headers=headers, params=params)
    if response.ok:
        # with open("response.html", "a", encoding='utf-8') as file:
        #     file.write(response.text)
        return response
    else:
        print(f"ERROR: {response.status_code}")


"""Возвращает json с требуемыми данными"""

def get_content(month, year, total_pages):
    save_json = []
    for page in range(total_pages):
        params_with_date = get_params(month, year, page)
        current_tenders = get_tenders(URL, HEADERS, params_with_date).text
        json_dict = json.loads(current_tenders)
        # with open("tenders.json", "a", encoding='utf-8') as file:
        #     file.write(current_tenders)
        for item in json_dict['data']: 
            all_tenders = {}
            
            if item['attributeCategories'][0]['attributes'][1]['code'] == 'tenders_tender_name':
                all_tenders['tenders_name'] = item['attributeCategories'][0]['attributes'][1]['value']
            elif item['attributeCategories'][0]['attributes'][0]['code'] == 'tenders_tender_name':
                all_tenders['tenders_name'] = item['attributeCategories'][0]['attributes'][0]['value']
            else:
                all_tenders['tenders_name'] = item['name']

            if item['attributeCategories'][0]['attributes'][0]['code'] == 'tenders_tender_oebs_number':
                all_tenders['tenders_tender_oebs_number'] = item['attributeCategories'][0]['attributes'][0]['value']
            else:
                all_tenders['tenders_tender_oebs_number'] = 'Не задан'

            all_tenders['tenders_publication_date'] = item['attributeCategories'][0]['attributes'][2]['value']

            for tenders_end_date_accepting_offers in item['attributeCategories'][0]['attributes']:
                if ('code', 'tenders_end_date_accepting_offers') in tenders_end_date_accepting_offers.items():
                    all_tenders['tenders_end_date_accepting_offers'] = tenders_end_date_accepting_offers['value']

            for tender_responsible in item['attributeCategories'][0]['attributes']:
                if ('code', 'tender_responsible') in tender_responsible.items():
                    all_tenders['tender_responsible'] = tender_responsible['value']['value']

            for attachments in item['attributeCategories'][0]['attributes']:
                if ('code', 'tenders_attachments') in attachments.items():
                    all_tenders['tenders_attachments'] = attachments['value']
            
            # new_json = json.dumps(all_tenders, indent=4, ensure_ascii=False)
        
            save_json.append(all_tenders)
                
    with open('all_tenders' + '_' + str(month) + '_' + str(year) + '.json', 'w', encoding = 'utf-8') as file:
        file.write(json.dumps(save_json, indent=4, ensure_ascii=False))


"""Возвращает параметры с указанной датой, годом / страницей, - при указании 3-го аргумента для учета пагинации."""

def get_params(month, year, page=0):
    amount_days_month = calendar.monthrange(year, month)[1]
    first_date_month = datetime.date(year, month, 1)
    last_date_month = datetime.date(year, month, amount_days_month)

    params_with_input_date = {
        'dateFrom': f'{first_date_month}',
        'dateTo': f'{last_date_month}',
        'pageSize': '50',
        'page': f'{page}',
        'isSubscribe': 'false',
        'attributesForSort': 'tenders_publication_date,desc',
    }
    return params_with_input_date


"""Забирает параметры и количество страниц"""

def main(month, year):
    start_time = datetime.datetime.now()
    params = get_params(month, year)
    info_json_dict = get_tenders(URL, HEADERS, params)
    amount_pages = info_json_dict.json()["totalPages"]
    print(f"Всего страниц: {amount_pages}")
    get_content(month, year, amount_pages)
    fin_time = datetime.datetime.now()
    print(fin_time - start_time)


"""На вход принимаются 2 аргумента: месяц, год."""

main(int(sys.argv[1]), int(sys.argv[2]))
