import os
import time
from contextlib import contextmanager
import requests
from bs4 import BeautifulSoup as bs

@contextmanager
def goto(dir):
    cwd = os.getcwd()
    try:
        os.chdir(dir)
    except FileNotFoundError:
        os.mkdir(dir)
        os.chdir(dir)
    yield None
    os.chdir(cwd)

INTERVAL = 0.5
class AlbumSpider:
    def __init__(self, url):
        self.url = url

    def downloadAlbum(self, albumUrl):
        """Download a single album:
            dowmloadAlbum('https://www.douban.com/photos/album/123456789/')
        """
        album = requests.get(albumUrl)
        soup = bs(album.text, "html.parser")
        albumName = soup.find('div', class_='info').h1.string.split('-')[-1]
        nextpage = soup.find('span', class_='next')
        thumbs = soup.find_all('a', class_='photolst_photo')
        imgUrls = [a.img['src'].replace('thumb', 'large')
                    for a in thumbs]
        with goto(albumName):
            for img in imgUrls:
                imgName = img.split('/')[-1]
                with open(imgName, 'wb') as imgdate:
                    imgdate.write(requests.get(img).content)
                    time.sleep(INTERVAL)
        if nextpage and nextpage.a:
            self.downloadAlbum(nextpage.a['href'])

    def downloadAllAlbums(self, albumsUrl):
        """Download all albums of a person, the albumsUrl is the url of a person's albumlist.
            downloadAllAlbums('https://www.douban.com/people/abcde/photos')
        """
        allAlbums = requests.get(albumsUrl)
        soup = bs(allAlbums.text, "html.parser")
        people = soup.find('div', class_='info').h1.string
        nextpage = soup.find('span', class_='next')
        albums = soup.find_all('a', class_='album_photo')
        albumUrls = [album['href'] for album in albums]
        with goto(people):
            for albumUrl in albumUrls:
                self.downloadAlbum(albumUrl)
        if nextpage and nextpage.a:
            self.downloadAllAlbums(nextpage.a['href'])

    def downloadCelebrity(self, celebrityUrl):
        """Download a celebrity's photos, the celebrityUrl is the celebrity's 'allphoto'
            downloadCelebrity('https://movie.douban.com/celebrity/:celebrityID/photos/')
        """
        celebrity = requests.get(celebrityUrl).text
        soup = bs(celebrity, "html.parser")
        celebrityName = "影人" + soup.find('div', id='content').h1.string.split(' ')[0]
        nextpage = soup.find('span', class_='next')
        photodivs = soup.find_all('div', class_='cover')
        photos = [(div.a['href'], div.a.img['src']) for div in photodivs]
        with goto(celebrityName):
            for photo in photos:
                photoName = photo[1].split('/')[-1]
                with open(photoName, 'wb') as photodata:
                    rawphoto = photo[1].replace('thumb', 'raw')
                    photodata.write(requests.get(rawphoto, headers={'referer':photo[0]}).content)
                    time.sleep(INTERVAL)
        if nextpage and nextpage.a:
            self.downloadCelebrity(nextpage.a['href'])

    def downloadMovie(self, movieUrl):
        """Download a movie's photos.
            downloadMovie('https://movie.douban.com/subject/1234567/photos') 
        """
        moviePhotos = requests.get(movieUrl)
        soup = bs(moviePhotos.text, "html.parser")
        title = soup.title.string.split(' ')[4]
        nextpage = soup.find('span', class_='next')
        photodivs = soup.find_all('div', class_='cover')
        photos = [(div.a['href'], div.a.img['src']) for div in photodivs]
        with goto(title):
            for photo in photos:
                photoName = photo[1].split('/')[-1]
                with open(photoName, 'wb') as photodata:
                    rawphoto = photo[1].replace('thumb', 'raw')
                    photodata.write(requests.get(rawphoto, headers={'referer':photo[0]}).content)
        if nextpage and nextpage.a:
            self.downloadMovie(nextpage.a['href'])

    def run(self):
        if 'people' in self.url:
            self.downloadAllAlbums(self.url)
        elif 'celebrity' in self.url:
            self.downloadCelebrity(self.url)
        elif 'subject' in self.url:
            self.downloadMovie(self.url)
        else:
            self.downloadAlbum(self.url)
