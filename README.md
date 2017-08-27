# spiderly

## 豆瓣影片爬虫

```
python doubanMovie.py
```

## 豆瓣图片爬虫。

按照下边URL格式定义爬虫进行爬取。

### 爬取单个相册。
```
from douban import AlbumSpider
spider = AlbumSpider('https://www.douban.com/photos/album/123456789/')
spider.run()
```
### 爬取一个用户的所有相册.
```
from douban import AlbumSpider
spider = AlbumSpider('https://www.douban.com/people/123456789/photos')
spider.run()
```
### 爬取影人图片。
```
from douban import AlbumSpider
spider = AlbumSpider('https://movie.douban.com/celebrity/123456/photos/')
spider.run()
```
### 爬取影片图片。
```
from douban import AlbumSpider
spider = AlbumSpider('https://movie.douban.com/subject/123456/photos')
spider.run()
```
