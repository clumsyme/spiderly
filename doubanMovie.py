import json
import re
import copy
import time
from requests import get
from bs4 import BeautifulSoup as bs

pattern = re.compile(r'\((.*?)人评价\)')
rootUrl = 'https://movie.douban.com/tag/'
baseUrl = 'https://movie.douban.com'

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
}

class Spider:
    def __init__(self, cate):
        self.cate = cate
        self.tagMovies = {}
        self.movies = []
    def getTagsUrls(self):
        rootPage = get(rootUrl, headers=headers)
        rootSoup = bs(rootPage.text, 'html.parser')
        tagsTable = rootSoup.find('a', attrs={'name':self.cate}).next_sibling.next_sibling
        tags = [tag.a['href'] for row in list(tagsTable.tbody.children) for tag in row if tag != '\n']
        tagsUrls = [baseUrl+tag for tag in tags]
        return tagsUrls
    def getMovies(self, tagUrl):
        tagPage = get(tagUrl, headers=headers)
        tagSoup = bs(tagPage.text, 'html.parser')
        items = tagSoup.find_all('tr', class_='item')
        nextpage = tagSoup.find('span', class_='next')
        for item in items:
            title = item.td.a['title']
            url = item.td.a['href']
            movieid = url.split('/')[-2]
            try:
                rating = item.find('span', class_='rating_nums')
                if rating:
                    rating = float(rating.string)
                else:
                    rating = 0
            except:
                rating = 0
            try:
                rated = item.find('span', class_='pl')
                rated = re.findall(pattern, rated.string)
                if rated and rated[0] != '目前无':
                    rated = int(rated[0])
                else:
                    rated = 0
            except:
                rated = 0
            movie = {'title': title, 'rating': rating, 'rated': rated, 'url': url, 'id': movieid}
            self.movies.append(movie)
        return

        print('    ', len(self.movies), '个已爬取')
        print('--------------------------------')

        time.sleep(1)
        if nextpage and nextpage.a:
            self.getMovies(nextpage.a['href'])
    def getTagMovies(self, tagUrl):
        tag = tagUrl.split('/')[-1]
        print('+++++++++++++++++++++++')
        print('正在爬取类别：', tag)
        self.getMovies(tagUrl)
        copymovies = copy.deepcopy(self.movies)
        self.tagMovies.update({tag: copymovies})
        self.movies.clear()
    def run(self):
        tagsUrls = self.getTagsUrls()
        for tagUrl in tagsUrls:
            self.getTagMovies(tagUrl)
        with open(self.cate + '.json', 'w', encoding='utf8') as dbm:
            json.dump(self.tagMovies, dbm, indent=2, ensure_ascii=False)

spider = Spider('类型')
spider.run()
