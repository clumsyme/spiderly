import json
import time
import requests
from bs4 import BeautifulSoup as bs

class ZhihuSpider:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
    def __init__(self, url):
        if 'topic' in url:
            self.url = url + '/top-answers'
        else:
            self.url = url + '/answers?order_by=vote_num'
        self.answers = []
    def get_user_answers(self, url):
        print(url)
        pagenum = url.split('=')[-1]
        print('scrawling page', pagenum)
        page = requests.get(url, headers=ZhihuSpider.headers)
        soup = bs(page.content, "html.parser")
        items = soup.find_all('div', class_='zm-item')
        for item in items:
            title = item.h2.a.string.strip()
            try:
                answer = item.find('textarea').string
            except AttributeError:
                answer = '此答案被删除'
            self.answers.append({title: answer})
        nav = soup.find('div', class_='border-pager')
        if nav:
            nextspan = nav.div.findChildren()[-1]
        else:
            self.name = soup.title.string.strip().split(' ')[0]
            return
        try:
            nexturl = nextspan['href']
        except KeyError:
            self.name = soup.title.string.strip().split(' ')[0]
            nexturl = False
        if nexturl:
            self.get_user_answers(self.url + nexturl)
    def get_topic_answers(self, url):
        pagenum = url.split('=')[-1]
        print('scrawling page', pagenum)
        page = requests.get(url, headers=ZhihuSpider.headers)
        soup = bs(page.content, "html.parser")
        items = soup.find_all('div', class_='feed-main')
        for item in items:
            title = item.div.h2.a.string.strip()
            approval = item.find('a', class_='zm-item-vote-count').string
            try:
                author = item.find('a', class_='author-link').string
            except AttributeError:
                author = '匿名用户'
            try:
                answer = item.find('textarea').string
            except AttributeError:
                answer = '此答案被删除'
            self.answers.append({'title': title,
                                 'approval': approval,
                                 'author': author,
                                 'answer': answer
                                })
        nav = soup.find('div', class_='zm-invite-pager')
        nextspan = nav.findChildren()[-1]
        try:
            nexturl = nextspan['href']
        except KeyError:
            self.name = soup.title.string.strip().split(' ')[0]
            nexturl = False
        if nexturl:
            self.get_topic_answers(self.url + nexturl)
    def json_answers(self):
        with open(self.name+'.json', 'w', encoding='utf8') as file:
            json.dump(self.answers, file, indent=2, ensure_ascii=False)
    def run(self):
        if 'people' in self.url:
            self.get_user_answers(self.url)
            self.json_answers()
        else:
            self.get_topic_answers(self.url)
            self.json_answers()
