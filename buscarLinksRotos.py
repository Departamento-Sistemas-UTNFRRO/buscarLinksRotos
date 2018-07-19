# -*- coding: utf-8 -*-
#    This file is part of buscarLinksRotos.
#
#    buscarLinksRotos is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    buscarLinksRotos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with buscarLinksRotos; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import urllib.request
import urllib.parse
import bs4
import datetime
import locale
from googlesearch import search
import TFIDF
import time
from pyfbutils.DataSetCSV import DataSetCSV
from pyfbutils.PostFacebook import PostFacebook


dominiosMapeados = {
    'a.ln.com.ar': 'www.lanacion.com.ar',
    'clar.in': 'www.clarin.com',
    'mundial-brasil-2014.clarin.com': 'www.clarin.com',
    'arq.clarin.com': 'www.clarin.com',
    'deporteshd.clarin.com': 'www.clarin.com'
}


def alargar_url(req):
    try:
        urlResuelta = urllib.request.urlopen(req)
        return urlResuelta.url
    except Exception as ex:
        print("ERROR" + str(ex))
    return None


def ObtenerDominioUrl(urlLink):
    '''Devuelve el dominio del link'''
    urlTraducida = urllib.parse.urlparse(urlLink)
    return '{uri.netloc}'.format(uri=urlTraducida)


def ObtenerDominioUrlMapeado(urlLink):
    dominio = ObtenerDominioUrl(urlLink)
    for viejo, nuevo in dominiosMapeados.items():
        if(viejo in dominio):
            dominio = dominio.replace(viejo, nuevo)
    return dominio


def getFechaNacion(soup):
    fechaNacion = "FECHA NO ENCONTRADA"
    if (soup is None):
        return fechaNacion

    try:
        for tag in soup.find_all("meta"):
            if tag.get("itemprop", None) == "datePublished":
                return tag.get("content", None)
        contenedor = soup.find(class_='fecha')
        if(contenedor is not None):
            fechaCompleta = contenedor.getText()
            fechaCompleta = fechaCompleta.replace('\xa0', '')
            fechaCompleta = fechaCompleta.replace('de', '')
            fechaCompleta = fechaCompleta.replace('•', '')
            fechaCompleta = fechaCompleta.replace('  ', ' ')
            fechaCompleta = fechaCompleta.replace('  ', ' ')
            fechaCompleta = fechaCompleta.strip()
            locale.setlocale(locale.LC_TIME, 'es_AR')
            if('•' in contenedor.getText()):
                fechaCompleta = datetime.datetime.strptime(
                    fechaCompleta, '%d %B %Y %H:%M')
            else:
                fechaCompleta = datetime.datetime.strptime(
                    fechaCompleta, '%d %B %Y')
            fechaNacion = fechaCompleta.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as ex:
        print("ERROR" + str(ex))
    return fechaNacion


def getFechaClarin(soup):
    fechaNacion = "FECHA NO ENCONTRADA"
    if (soup is None):
        return fechaNacion

    for tag in soup.find_all("meta"):
        if tag.get("itemprop", None) == "datePublished":
            return tag.get("content", None)
    return "FECHA NO ENCONTRADA"


def getHtmlSoup(req):
    try:
        resp = urllib.request.urlopen(req)
        html = resp.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as ex:
        print("ERROR" + str(ex))
        return None


def buscarLinksEnGoogle(datasetCSV):
    posts = datasetCSV.dataset

    for i in range(datasetCSV.inicio, datasetCSV.fin):
        try:
            print(i)
            post_link = posts[i][1]
            postFacebook = PostFacebook(post_link)
            link_url = posts[i][2]
            print(link_url)
            # FIXME: incorporar en clase post
            post_fecha = convertirTextoAFecha(posts[i][3])

            datosPost = postFacebook.getInfoPostFacebook()
            titulo_post = datosPost[0]
            posts[i].append(titulo_post)
            posts[i].append(datosPost[1])
            print(datosPost[0])

            if('youtu.be' in link_url or 'tapas.clarin.com' in link_url):
                print('Omitiendo')
                posts[i].append("LINK NULL")
                continue

            # if(titulo_post == ""):
            #    print('Omitiendo')
            #    posts[i].append("LINK Borrado")
            #    continue

            dominio = ObtenerDominioUrlMapeado(link_url)
            print(dominio)

            # Buscar el link en base a los datos que tengo
            # texto del post
            # de los resultados elegir segun la fecha tmb

            linkMismoDominio = []

            # en caso que funcione el link lo agrego directamente
            try:
                req = urllib.request.Request(link_url)
                url_larga = alargar_url(req)
                if (url_larga is not None):
                    linkMismoDominio.append(url_larga)
            except Exception:
                pass

            texto_a_buscar = titulo_post.replace('"', '') + " " + dominio
            for url in search(texto_a_buscar, tld='com.ar', lang='es', stop=5):
                print(url)
                if(dominio in url):
                    req = urllib.request.Request(url)
                    soup = getHtmlSoup(req)
                    if('clarin' in url):
                        fecha_portal = getFechaClarin(soup)
                    else:
                        if ('nacion' in url):
                            fecha_portal = getFechaNacion(soup)
                        else:
                            continue

                    if(fecha_portal == "FECHA NO ENCONTRADA"):
                        continue

                    fecha_portal = datetime.datetime.strptime(
                        fecha_portal, '%Y-%m-%d %H:%M:%S')
                    fecha_portal = fecha_portal.date()
                    if(fecha_portal <= post_fecha):
                        linkMismoDominio.append(url)

            # Siempre doy prioridad al orden de google porque es mas problable que sea
            # mejor su medida de similitud que la que podamos calcular por
            # nuestros medios
            cantidadLinksMismoDominio = len(linkMismoDominio)

            if cantidadLinksMismoDominio == 1:
                posts[i].append(linkMismoDominio[0])
            else:
                if cantidadLinksMismoDominio == 0:
                    print("No encontre link")
                    posts[i].append("No encontre link")
                else:
                    print("Necesito Distancia de Texto")
                    tfidf = TFIDF.TfIdf()
                    linkMasProximo = tfidf.getNearestLinkToTerm(linkMismoDominio, titulo_post)
                    if linkMasProximo is None:
                        posts[i].append("No encontre link")
                    else:
                        posts[i].append(linkMasProximo)

            # esperar unos segundos para que nos banee google
            time.sleep(10)
        except Exception as ex:
            columnas = len(posts[i]) + 1
            for _ in range(columnas, datasetCSV.cantidadColumnas):
                posts[i].append("TIME OUT" + str(ex))
            print("TIME OUT")
            print(ex)


def convertirTextoAFecha(fechaTexto):
    post_fecha = datetime.datetime.strptime(fechaTexto, '%Y-%m-%d').date()
    return post_fecha


nombreArchivoEntrada = 'buscarEnGoogle_restantes.csv'
nombreArchivoSalida = 'post_output.csv'
columnas = ['post_id', 'post_link', 'link', 'post_fecha', 'post_titulo', 'post_subtitulo', 'UrlCompleta']

inicio = 0
fin = None

datasetCSV = DataSetCSV(nombreArchivoEntrada, nombreArchivoSalida, columnas, inicio, fin)
buscarLinksEnGoogle(datasetCSV)
datasetCSV.guardar()
