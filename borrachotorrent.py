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
    itemlist.append( Item(channel=item.channel, action="menu_series", title="Series HD", url="https://www.borrachodetorrent.com/wp-json/wp/v2/episodes?per_page=28&page=1", folder=True))
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

    itemlist = list()
    
    data_Series = scrapertools.cache_page(item.url)
    JSONData_Series = jsontools.load_json(data_Series)

    contador = 0
    for Series in JSONData_Series:
      id_serie1 = Series['rest_api_enabler']['id_serie']
      title1 = Series['serie'][0]  
      title2 = Series['title']['rendered'] 
      plot1 = Series['content']['rendered']
      temporada1 = Series['rest_api_enabler']['temporada']
      episodio1 = Series['rest_api_enabler']['episodio']
      thumbnail1 = Series['rest_api_enabler']['poster_serie']
      fanart1 = Series['rest_api_enabler']['fondo_player']
      torrent_Calidad1 = Series['rest_api_enabler']['torrent_Calidad']
      torrent_url1 = Series['rest_api_enabler']['torrent_Url']
      

      if id_serie1!="":
        url_serie = "https://www.borrachodetorrent.com/wp-json/acf/v2/tvshows/"+id_serie1+"/temporadas/"
        itemlist.append( Item(channel=item.channel, action="menu_series_2", title=title2+" ["+torrent_Calidad1+"]", fulltitle=title2, url=url_serie, thumbnail=thumbnail1, plot=plot1, fanart=fanart1, magnet_url=torrent_url1, tipo="Series", folder=True))
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
        itemlist.append( Item(channel=item.channel, action="menu_series" , title=">> Página siguiente" , url=url2, tipo="Series", folder=True))

    return itemlist



def menu_series_2(item):
    logger.info("pelisalacarta.channels.borrachotorrent menu_series2")

    title3 = item.title
    fulltitle3 = item.fulltitle
    url3 = item.url
    magnet3 = item.magnet_url
    plot3 = item.plot
    thumbnail3 = item.thumbnail
    fanart3 = item.fanart

    itemlist3 = []

    itemlist3.append( Item(channel=item.channel, action="play", server="torrent", title="Ver este Capítulo ("+title3+")", fulltitle=fulltitle3, url=magnet3 , thumbnail=thumbnail3, plot=plot3, fanart=fanart3, tipo="Series", folder=False) )
    itemlist3.append( Item(channel=item.channel, action="menu_series_3" , title="Listar todos los Capítulos" , url=url3, tipo="Series", folder=True))
    

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
  
