#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, bs4
import re
import os

# 用于跟网站子目录拼接
root_url = "http://qhzk.lib.tsinghua.edu.cn:8080"
index_url = root_url + "/Tsinghua_Journal/year.html"
# 创建文件夹
download_dir = 'tsinghua_journal_downloads'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 用于获取每一期的刊名和链接
def get_journal_page_urls():
    # 用于保存每一期刊物的元数据
    journals = []

    response = requests.get(index_url)
    # 默认编码为ISO-8859-1，此处将编码修正为UTF-8
    # https://github.com/kennethreitz/requests/issues/1604
    response.encoding = 'utf-8'
    soup = bs4.BeautifulSoup(response.text)

    for link in soup.select('table a'):
        title = link.getText()
        url = link.get('href')
        if(url):
            one_journal = {
                    'title': title,
                    'link': root_url + url, 
                    }
            journals.append(one_journal)
            print one_journal['title'],one_journal['link']
    return journals

def get_page_count(journal):
    response = requests.get(journal['link'])
    soup = bs4.BeautifulSoup(response.text)
    page_count = soup.select('div.command-bar a')[-1].get('href') 
    # page_count的格式如 'javascript:gotoPage(17)'，需要提取数字
    page_count = re.findall('\d+', page_count)[0]
    return int(page_count)

def get_pages_in_range(page_limit=None, journal_limit=None):
    journals = get_journal_page_urls()
    # 遍历限定范围内的期刊
    for journal in journals[:journal_limit]: 
        count = page_limit or get_page_count(journal) 

        for page_no in range(1, 1+count):
            # 发送POST请求，翻页
            data = {
                    'action': 'image',
                    'jumpPage': page_no,
                   }
            turnpage_response = requests.post(journal['link'], data=data)
            # print turnpage_response.url

            # 发送GET请求，获取图片
            showimage_payload = {
                    'rand': 'aaa'
                    }
            showimage_url = journal['link'].replace('turnPage', 'showImage')
            image_response = requests.get(showimage_url, params=showimage_payload)
            # print image_response.url

            # 保存图片到本地
            filename = u'%s-第%d页.png' % (journal['title'], page_no)
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(image_response.content)
                print '%s saved at %s' % (filename, filepath)

if __name__ == '__main__':
    get_pages_in_range(page_limit=3, journal_limit=5)
