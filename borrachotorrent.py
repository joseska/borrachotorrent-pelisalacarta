# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para borrachotorrent
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urllib
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("pelisalacarta.channels.borrachotorrent mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, action="menu_peliculas" , title="Películas" ,folder=True))
    itemlist.append( Item(channel=item.channel, action="menu_series" , title="Series" ,folder=True))
    itemlist.append( Item(channel=item.channel, action="search" , title="Buscar..."))
    return itemlist

def menu_peliculas(item):
    logger.info("pelisalacarta.channels.borrachotorrent menu_peliculas")
    
    itemlist = []

    itemlist.append( Item(channel=item.channel, action="peliculasHD" , title="Películas HD" , url="https://www.borrachodetorrent.com/wp-json/wp/v2/posts?categories_exclude=53571&page=1&per_page=28" ,folder=True))
    itemlist.append( Item(channel=item.channel, action="menu" , title="Estrenos de Película" , url="https://www.borrachodetorrent.com/wp-json/wp/v2/posts?categories_exclude=53571&page=1&per_page=28" ,folder=True))
 
    return itemlist




def peliculasHD(item):
    logger.info("pelisalacarta.channels.borrachotorrent peliculasHD")

    itemlist = list()


    data = scrapertools.cache_page(item.url)
    JSONData = jsontools.load_json(data)
    
    contador = 0
    for Video in JSONData:
      thumbnail1 = Video['rest_api_enabler']['poster_url780']
      url1 = Video['rest_api_enabler']['torrent_Url']
      title1 = Video['title']['rendered']
      plot1 = Video['rest_api_enabler']['tagline']
      fanart1 = Video['rest_api_enabler']['fondo_player']
      torrent_Calidad1 = Video['rest_api_enabler']['torrent_Calidad']

      if url1!="" and title1!="" and plot1!="" and fanart1!="" and torrent_Calidad1!="" and thumbnail1!="":
        itemlist.append( Item(channel=item.channel, action="play", server="torrent", title=title1+" ["+torrent_Calidad1+"]", fulltitle=title1, url=url1 , thumbnail=thumbnail1, plot=plot1, fanart=fanart1, folder=False) )
        contador = int(contador)+1
      else:
        continue
      
      if contador >= 28:
        url_json = item.url
        patron = re.compile('&page=([1-9])')
        matcher = patron.search(url_json)
        masuno = int(matcher.group(1))+1
        reemplazar = '&page='+str(masuno)
        url2 = url_json.replace(matcher.group(0), reemplazar)
        logger.info("[borrachodetorrent.py]  " + url2)
        itemlist.append( Item(channel=item.channel, action="peliculasHD" , title=">> Página siguiente" , url=url2, folder=True))

    return itemlist
    


def menu_series(item):
    logger.info("pelisalacarta.channels.borrachotorrent menu_series")
    
    itemlist3 = []
    itemlist3.append( Item(channel=item.channel, action="menu" , title="Series1" , url="http://www.divxatope.com/",extra="Peliculas",folder=True))
    itemlist3.append( Item(channel=item.channel, action="menu" , title="Series 2" , url="http://www.divxatope.com",extra="Series",folder=True))
    return itemlist3


def search(item,texto):
    logger.info("pelisalacarta.channels.borrachotorrent search")
    if item.url=="":
        item.url="http://www.divxatope.com/buscar/descargas"
    item.extra = urllib.urlencode({'search':texto})

    try:
        return lista(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []
  
