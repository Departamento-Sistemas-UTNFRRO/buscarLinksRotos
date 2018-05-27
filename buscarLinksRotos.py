# -*- coding: utf-8 -*-
#    This file is part of buscarEnPortalesDiarios.
#
#    buscarEnPortalesDiarios is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    buscarEnPortalesDiarios is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with buscarEnPortalesDiarios; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import urllib.request
import pandas as pd
import os
import urllib.parse
import csv
import bs4
import datetime
import locale
from googlesearch import search


linkMapeados = {
    'a.ln.com.ar': 'www.lanacion',
    'clar.in': 'www.clarin.com',
    'mundial-brasil-2014.clarin.com': 'www.clarin.com',
    'arq.clarin.com': 'www.clarin.com',
    'deporteshd.clarin.com': 'www.clarin.com'
}

textosAOmitir = [
    'LA NACION shared a link',
    'Diario Clarín shared a link.',
    '\\N'
]


def alargar_url(req):
    try:
        resolvedURL = urllib.request.urlopen(req)
        return resolvedURL.url
    except Exception as ex:
        print("ERROR" + str(ex))
    return None


def ObtenerDominioUrl(link_url):
    '''Devuelve el dominio del link'''
    parsed_uri = urllib.parse.urlparse(link_url)
    return '{uri.netloc}'.format(uri=parsed_uri)


def ObtenerDominioUrlMapeado(link_url):
    domain = ObtenerDominioUrl(link_url)
    for viejo in linkMapeados:
        if(viejo in domain):
            domain = domain.replace(viejo, linkMapeados[viejo])
    return domain


def getHtmlFacebook(url):
    req = urllib.request.Request(url)
    try:
        resp = urllib.request.urlopen(req)
        html = resp.read()
        return html
    except Exception as ex:
        print("ERROR" + str(ex))
    return None


def getTituloFacebook(url):
    html = getHtmlFacebook(url)
    titulo_post = ""
    subtitulo_post = ""

    if (html is not None):
        # El html de facebook viene en una etiqueta "code" comentada y se arma dinamico con Javascript
        # para poder interpretarlo, sacamos el comentario y lo pasamos normalmente al parseador
        # Por ejemplo:
        # <div class="hidden_elem"><code id="u_0_q"><!-- <div class="_5pcb _3z-f"> --></code>

        html = html.replace(b'<!--', b'')  # Apertura comentario
        html = html.replace(b'-->', b'')  # Cierre Comentario
        # print(html)
        content = bs4.BeautifulSoup(html, 'lxml')

        b = content.find_all('div', {'class': 'mbs _6m6 _2cnj _5s6c'})
        if b:
            titulo_post = b[0].getText()

        c = content.find_all('div', {'class': '_6m7 _3bt9'})
        if c and len(c) > 0:
            subtitulo_post = c[0].getText()

    return (titulo_post, subtitulo_post)


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
            fechaNacion = fechaCompleta.strftime('%d/%m/%Y %H:%M:%S')
    except Exception as ex:
        print("ERROR" + str(ex))
    return fechaNacion


def getFechaClarin(soup):
    for tag in soup.find_all("meta"):
        if tag.get("itemprop", None) == "datePublished":
            return tag.get("content", None)
    return "FECHA NO ENCONTRADA"


def getHtml(req):
    try:
        resp = urllib.request.urlopen(req)
        html = resp.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as ex:
        print("ERROR" + str(ex))
        return None


def buscarLinksEnGoogle(posts):
#    for i in range(0, len(posts)):
    for i in range(87, 89):
        try:
            print(i)
            post_link = posts[i][1]
            link_url = posts[i][2]
            post_fecha = posts[i][3]
            print(link_url)

            titulo_post, subtitulo_post = getTituloFacebook(post_link)
            print(titulo_post)

            posts[i].append(titulo_post)
            posts[i].append(subtitulo_post)

            if('youtu.be' in link_url):
                print('Omitiendo')
                posts[i].append("LINK NULL")
                continue

            if(titulo_post == ""):
                print('Omitiendo')
                posts[i].append("LINK Borrado")
                continue

            domain = ObtenerDominioUrlMapeado(link_url)
            print(domain)

            # Buscar el link en base a los datos que tengo
            # texto del post
            # de los resultados elegir segun la fecha tmb

            linkMismoDominio = []
            for url in search(titulo_post, tld='com.ar', lang='es', stop=5):
                print(url)
                if(domain in url):
                    print('mismo dominio')
                    print(url)
                    linkMismoDominio.append(url)

            # Siempre doy prioridad al orden de google porque es mas problable que sea
            # mejor su medida de similitud que la que podamos calcular por nuestros medios

            if (len(linkMismoDominio) == 1):
                posts[i].append(linkMismoDominio[0])
            else:
                if (len(linkMismoDominio) > 1):
                    print('Mas de uno aca ver por fecha y dsp por mineria de texto')
                    # FIXME: en base a si es la nacion o clarin buscar la fecha
                    print(linkMismoDominio)
                    #posts[i].append("LINK Mas de Uno")

                    #Si tengo varios link pueden ser del dia o no
                    #entonces descarto los que son de una fecha posterior al posteo de facebook
                    #si es mas de uno entonces distingo por mineria de texto

                    for l in linkMismoDominio:
                        req = urllib.request.Request(l)
                        soup = getHtml(req)
                        if('clarin' in l):
                            fecha_portal = getFechaClarin(soup)
                            fecha_portal = datetime.datetime.strptime(
                                fecha_portal, '%Y-%m-%d %H:%M:%S')
                            post_fecha = datetime.datetime.strptime(
                                post_fecha, '%Y-%m-%d')
                            if(fecha_portal <= post_fecha):
                                posts[i].append(l)
                                break
                        else:
                            if ('nacion' in l):
                                fecha_portal = getFechaNacion(soup)
                                if(fecha_portal == post_fecha):
                                    posts[i].append(l)
                                    break
                            else:
                                print('ERROR')
                                posts[i].append("LINK Mas de Uno")
                else:
                    # FIXME: en base a si es la nacion o clarin buscar la fecha
                    print('No encontre link')
                    print(linkMismoDominio)
                    posts[i].append("LINK ninguno")
        except Exception as ex:
            columnas = len(posts[i]) + 1
            for _ in range(columnas, 8):
                posts[i].append("TIME OUT")
            print("TIME OUT")
            print(ex)

    return posts


def loadCsvIntoDataSet(nombreArchivoEntrada):
    csv = pd.read_csv(nombreArchivoEntrada, header=0,
                      sep=';', quotechar='\"', encoding="utf-8")
    return csv.values


def saveInCsv(postsFinal, nombreArchivoSalida):
    columns = ['post_id', 'post_link', 'link',
               'post_fecha', 'post_titulo', 'post_subtitulo', 'UrlCompleta']

    df = pd.DataFrame(data=postsFinal, columns=columns)
    df.to_csv(nombreArchivoSalida, index=False, columns=columns, sep=';',
              quoting=csv.QUOTE_ALL, doublequote=True, quotechar='"', encoding="utf-16")


def armarRutaDatos(nombreArchivo):
    rutaADatos = os.path.join(os.path.dirname(__file__), 'data', nombreArchivo)
    return rutaADatos


nombreArchivoEntrada = armarRutaDatos('buscarEnGoogle_485.csv')
nombreArchivoSalida = armarRutaDatos('post_output.csv')
posts = loadCsvIntoDataSet(nombreArchivoEntrada).tolist()
postsConTitulo = buscarLinksEnGoogle(posts)
saveInCsv(postsConTitulo, nombreArchivoSalida)
