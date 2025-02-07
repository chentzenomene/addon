# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per Filmsenzalimiti
# ------------------------------------------------------------
"""
    Trasformate le sole def per support.menu e support.scrape
    da non inviare nel test.
    Test solo a trasformazione completa

"""
import re

from core import scrapertools, servertools, httptools, support
from core.item import Item
from platformcode import config
from platformcode import logger
from specials import autoplay

__channel__ = 'filmsenzalimiti'
host = config.get_channel_url(__channel__)

IDIOMAS = {'Italiano': 'IT'}
list_language = IDIOMAS.values()
list_servers = ['verystream', 'openload', 'streamango', 'vidoza', 'okru']
list_quality = ['1080p', '720p', '480p', '360']

checklinks = config.get_setting('checklinks', 'filmsenzalimiti')
checklinks_number = config.get_setting('checklinks_number', 'filmsenzalimiti')

headers = [['Referer', host]]


def mainlist(item):
    logger.info('[filmsenzalimiti.py] mainlist')

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = [Item(channel=item.channel,
                     action='video',
                     title='Film',
                     contentType='movie',
                     url=host,
                     thumbnail= ''),
                Item(channel=item.channel,
                     action='video',
                     title='Novità',
                     contentType='movie',
                     url=host + '/category/nuove-uscite',
                     thumbnail=''),
                Item(channel=item.channel,
                     action='video',
                     title='In Sala',
                     contentType='movie',
                     url=host + '/category/in-sala',
                     thumbnail=''),
                Item(channel=item.channel,
                     action='video',
                     title='Sottotitolati',
                     contentType='movie',
                     url=host + '/category/sub-ita',
                     thumbnail=''),
                Item(channel=item.channel,
                     action='sottomenu',
                     title='[B]Categoria[/B]',
                     contentType='movie',
                     url=host,
                     thumbnail=''),
                Item(channel=item.channel,
                     action='search',
                     extra='tvshow',
                     title='[B]Cerca...[/B]',
                     contentType='movie',
                     thumbnail='')]

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info('[filmsenzalimiti.py] search')

    item.url = host + '/?s=' + texto

    try:
        return cerca(item)

    # Continua la ricerca in caso di errore .
    except:
        import sys
        for line in sys.exc_info():
            logger.error('%s' % line)
        return []


def sottomenu(item):
    logger.info('[filmsenzalimiti.py] sottomenu')
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<li class="cat-item.*?<a href="([^"]+)">(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=item.channel,
                 action='video',
                 title=scrapedtitle,
                 url=scrapedurl))

    # Elimina Film dal Sottomenù
    itemlist.pop(0)

    return itemlist

@support.scrape
def video(item):
    logger.info('[filmsenzalimiti.py] video')
    itemlist = []

    patron = '<div class="col-mt-5 postsh">.*?<a href="(?P<url>[^"]+)" '\
             'title="(?P<title>[^"]+)">.*?<span class="rating-number">(?P<rating>.*?)<.*?<img src="(?P<thumb>[^"]+)"'
    patronNext = '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right"'

##    support.scrape(item, itemlist, patron, ['url', 'title', 'rating', 'thumb'], patronNext=patronNext)

##    return itemlist
    return locals()
def cerca(item):
    logger.info('[filmsenzalimiti.py] cerca')
    itemlist = []

    data = httptools.downloadpage(item.url).data.replace('\t','').replace('\n','')
    logger.info('[filmsenzalimiti.py] video' +data)

    patron = '<div class="list-score">(.*?)<.*?<a href="([^"]+)" title="([^"]+)"><img src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedrating, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedrating = scrapertools.decodeHtmlentities(scrapedrating)

        itemlist.append(
            Item(channel=item.channel,
                 action='findvideos',
                 title=scrapedtitle + ' (' + scrapedrating + ')',
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 contentType=item.contentType,
                 thumbnail=scrapedthumbnail), tipo='movie')

    patron = '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right"'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != '':
        itemlist.append(
            Item(channel=item.channel,
                 action='video',
                 title='[COLOR lightgreen]' + config.get_localized_string(30992) + '[/COLOR]',
                 contentType=item.contentType,
                 url=next_page))

    return itemlist


def findvideos(item):
    logger.info('[filmsenzalimiti.py] findvideos')

    itemlist = support.hdpass_get_servers(item)

   # Link Aggiungi alla Libreria
    if item.contentType == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findservers':
            itemlist.append(
                Item(channel=item.channel, title='[COLOR lightblue][B]Aggiungi alla videoteca[/B][/COLOR]', url=item.url,
                     action="add_pelicula_to_library", extra="findservers", contentTitle=item.contentTitle))

    #Necessario per filtrare i Link
    if checklinks:
        itemlist = servertools.check_list_links(itemlist, checklinks_number)

    # Necessario per  FilterTools
    # itemlist = filtertools.get_links(itemlist, item, list_language)

    # Necessario per  AutoPlay
    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    itemlist = servertools.find_video_items(data=item.url)

    return itemlist

def newest(categoria):
    logger.info('[filmsenzalimiti.py] newest' + categoria)
    itemlist = []
    item = Item()
    try:

        ## cambiare i valori 'peliculas, infantiles, series, anime, documentales por los que correspondan aqui en
        # nel py e nel json ###
        if categoria == 'peliculas':
            item.url = host
            itemlist = video(item)

            if 'Successivo>>' in itemlist[-1].title:
                itemlist.pop()

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error('{0}'.format(line))
        return []

    return itemlist
