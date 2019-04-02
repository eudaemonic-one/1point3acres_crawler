# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import pymongo
import argparse
import requests
import tabulate
from bs4 import BeautifulSoup
from constants import index_url, admission_report_postfix


def get_page_by_requests(url):
    res = requests.get(url)
    res.encoding = 'GBK'
    return res.text


def get_last_page_number():
    url = index_url + admission_report_postfix.format(page=1)
    text = get_page_by_requests(url)
    soup = BeautifulSoup(text, 'html.parser')
    fd_page_top = soup.find('span', id='fd_page_top')
    last_num = fd_page_top.find('a', class_='last').string.lstrip('... ')
    return int(last_num)


def parse_admission_abstract(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = []
    for tbody in soup.findAll('tbody', id=re.compile(r'normalthread_(.*?)')):
        # Make sure each tbody has <span> for admission gist
        if tbody.select('tr th span'):
            # Card link
            href = tbody.find('a', class_='xst')['href']
            tid = re.search(r'thread-(.*?)-1-1.html', href)
            # Admission information
            topic = tbody.find('a', class_='xst')
            semester = tbody.find('font', attrs={'color': '#666'})
            degree = tbody.find('font', attrs={'color': 'blue'})
            admission_tag = tbody.select('span u font b')
            admission_result = None
            if admission_tag and admission_tag[0]:
                admission_result = admission_tag[0]
            admitted_major = tbody.find('font', attrs={'color': '#F60'})
            admitted_school = tbody.find('font', attrs={'color': '#00B2E8'})
            admission_date = tbody.find('font', attrs={'color': 'brown'})
            # Username & Userid
            user_tag = tbody.select('tr td cite a')
            if user_tag and user_tag[0]:
                username = re.search(r'<.*?>(.*?)</a>', str(user_tag[0]))
                uid = re.search(r'<a.*?href="space-uid-(.*?).html".*?>.*?</a>',
                                str(user_tag[0]))
            # Post datetime
            post_date_tag = str(tbody.select('tr td em span')[0])
            post_date = re.search(r'.*?title="(.*?)".*?', post_date_tag)
            if not post_date:
                post_date = re.search(r'<span>(.*?)</span>', post_date_tag)
            # Reply & Visit times
            reply_tag = tbody.find('td', class_='num')
            reply = re.search(r'<a.*?>(.*?)</a>', str(reply_tag.a))
            visit = re.search(r'<em>(.*?)</em>', str(reply_tag.em))

            if topic:
                abstract = {
                    'tid':
                        int(tid.group(1)) if tid else None,
                    'topic':
                        topic.string if topic else None,
                    'semester':
                        semester.string.lstrip('[') if semester else None,
                    'degree':
                        degree.string if degree else None,
                    'admission_result':
                        admission_result.string if admission_result else None,
                    'admitted_major':
                        admitted_major.string if admitted_major else None,
                    'admitted_school':
                        admitted_school.string if admitted_school else None,
                    'admission_date':
                        admission_date.string if admission_date else None,
                    'username':
                        username.group(1) if username else None,
                    'uid':
                        int(uid.group(1)) if uid else None,
                    'post_date':
                        post_date.group(1) if post_date else None,
                    'reply':
                        int(reply.group(1)) if reply else None,
                    'visit':
                        int(visit.group(1)) if visit else None,
                }
                if args.admitted_major:
                    if abstract['admitted_major'].upper()\
                            != args.admitted_major.upper():
                        continue
                if args.degree:
                    if abstract['degree'].upper() != args.degree.upper():
                        continue
                result.append(abstract)
    return result


def get_admission_abstracts(
        start, end, total=200000,
        collection_name='admission_abstracts'
        ):
    result = []
    count = 0
    for num in range(start, end+1):
        print('At page number: {0}'.format(num))
        if count >= total:
            return result
        # Obtain admission abstracts in each page
        url = index_url + admission_report_postfix.format(page=num)
        text = get_page_by_requests(url)
        abstracts = list(filter(
            lambda x: x not in result, parse_admission_abstract(text))
            )
        # Cut admission abstracts if result exceeds total number
        length = len(abstracts)
        filtered_length = len(abstracts)
        if length + count > total:
            abstracts = abstracts[:total-count]
            length = len(abstracts)
        # Add admission abstracts in to result list
        result.extend(abstracts)
        count += length
        # Store admission abstracts into MongoDB
        if args.store:
            update_data_into_collection(
                db_name='1point3acres',
                collection_name=collection_name,
                data=abstracts)

    if args.store:
        print('{} tuples of record are stored'.format(count))

    return result


def update_data_into_collection(db_name, collection_name, data):
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient[db_name]
    collection = mydb[collection_name]
    for item in data:
        topic = item['topic']
        if topic:
            collection.update_one(
                {'topic': topic}, {'$set': item}, upsert=True
            )


if __name__ == '__main__':
    # Obtain the whole page numbers of admission report cards
    last_num = get_last_page_number()
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='1Point3Acres Admission Data Crawler')
    parser.add_argument(
        '-v', '--version', action='version',
        version='1Point3Acres Data Crawler 1.0')
    parser.add_argument(
        '--start', type=int, action='store', default=1,
        help='The first page number to be achieved')
    parser.add_argument(
        '--end', type=int, action='store', default=last_num,
        help='The last page number to be achieved')
    parser.add_argument(
        '--total', type=int, action='store', default=200000,
        help='The total number of admission cards to be achived')
    parser.add_argument(
        '--admitted-major', type=str, action='store', default=None,
        help='only achieve admission data with the specified admitted major')
    parser.add_argument(
        '--degree', type=str, action='store', default=None,
        help='only achieve admission data with the specified degree')
    parser.add_argument(
        '--collection-name', type=str, action='store',
        default="admission_abstracts",
        help='The name of MongoDB collection to be stored')
    parser.add_argument(
        '-s', '--store', action='store_const', const=True,
        help='store admission data into MongoDB')
    parser.add_argument(
        '-o', '--output', action='store_const', const=True,
        help='print out admission data into stdout')
    args = parser.parse_args()
    # Start crawling data
    result = get_admission_abstracts(
        args.start, args.end, args.total, args.collection_name)

    if args.output and result:
        table = dict()
        for key in result[0].keys():
            if key not in ('tid', 'uid', 'reply', 'visit'):
                table[key] = [item[key].decode('utf-8')
                              if isinstance(item[key], str)
                              else item[key] for item in result]
        print(tabulate.tabulate(table, headers='keys', tablefmt='simple'))
