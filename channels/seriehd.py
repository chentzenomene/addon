# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per SerieHD
# ------------------------------------------------------------


from core import scrapertoolsV2, httptools, support
from core.item import Item


__channel__ = 'seriehd'
# host = support.config.get_channel_url(__channel__)

# impostati dinamicamente da findhost()
host = ''
headers = ''

def findhost():
    data= httptools.downloadpage('https://seriehd.nuovo.link/').data
    global host, headers
    host = scrapertoolsV2.find_single_match(data, r'<div class="elementor-button-wrapper"> <a href="([^"]+)"')
    headers = [['Referer', host]]
    return host

list_servers = ['verystream', 'openload', 'streamango', 'thevideome']
list_quality = ['1080p', '720p', '480p', '360']

checklinks = support.config.get_setting('checklinks', __channel__)
checklinks_number = support.config.get_setting('checklinks_number', __channel__)


@support.menu
def mainlist(item):
    findhost()
    tvshow = [('Genere', ['', 'genre']),
              ('Americane', ['serie-tv-streaming/serie-tv-americane', 'peliculas']),
              ('Italiane', ['serie-tv-streaming/serie-tv-italiane', 'peliculas']),]
    return locals()


def search(item, texto):
    support.log(texto)
        
    item.contentType = 'tvshow'
    item.url = findhost() + "/?s=" + texto
    try:
        return peliculas(item)

    # Continua la ricerca in caso di errore .
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("%s" % line)
        return []


def newest(categoria):
    support.log(categoria)
    itemlist = []
    item = support.Item()    
    try:
        if categoria == "series":
            item.url = findhost()
            itemlist = peliculas(item)

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("{0}".format(line))
        return []

    return itemlist


@support.scrape
def genre(item):
    patronMenu = '<a href="(?P<url>[^"]+)">(?P<title>[^<]+)</a>'
    blacklist = ['Serie TV','Serie TV Americane','Serie TV Italiane','altadefinizione']
    patronBlock = '<ul class="sub-menu">(?P<block>.*)</ul>'
    action = 'peliculas'
    return locals()


@support.scrape
def peliculas(item):
    patron = r'<h2>(?P<title>.*?)</h2>\s*<img src="(?P<thumb>[^"]+)" alt="[^"]*" />\s*<A HREF="(?P<url>[^"]+)">.*?<span class="year">(?:(?P<year>[0-9]{4}))?.*?<span class="calidad">(?:(?P<quality>[A-Z]+))?.*?</span>'
    patronNext=r'<span class="current">\d+</span><a rel="nofollow" class="page larger" href="([^"]+)">\d+</a>'
    action='episodios'
    return locals()


@support.scrape
def episodios(item):
    data =''
    url = support.match(item, patronBlock=r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">')[1]
    seasons = support.match(item, r'<a href="([^"]+)">(\d+)<', r'<h3>STAGIONE</h3><ul>(.*?)</ul>', headers, url)[0]    
    for season_url, season in seasons:
        season_url = support.urlparse.urljoin(url, season_url)
        episodes = support.match(item, r'<a href="([^"]+)">(\d+)<', '<h3>EPISODIO</h3><ul>(.*?)</ul>', headers, season_url)[0]
        for episode_url, episode in episodes:
            episode_url = support.urlparse.urljoin(url, episode_url)
            title = season + "x" + episode.zfill(2)
            data += title + '|' + episode_url + '\n'
    support.log('DaTa= ',data)
    patron = r'(?P<title>[^\|]+)\|(?P<url>[^\n]+)\n'
    action = 'findvideos'
    return locals()


def findvideos(item):
    support.log()
    return support.hdpass_get_servers(item) 



