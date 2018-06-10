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
import time

dominiosMapeados = {
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


def getHtmlFacebook(urlLink):
    html = ""

    try:
        request = urllib.request.Request(urlLink)
        resp = urllib.request.urlopen(request)
        html = resp.read()
    except Exception as ex:
        print("ERROR" + str(ex))
    return html


def getTituloFacebook(urlLink):
    html = getHtmlFacebook(urlLink)
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
        contenido = bs4.BeautifulSoup(html, 'lxml')

        divTitulo = contenido.find_all(
            'div', {'class': 'mbs _6m6 _2cnj _5s6c'})
        if divTitulo:
            titulo_post = divTitulo[0].getText()

        divSubtitulo = contenido.find_all('div', {'class': '_6m7 _3bt9'})
        if divSubtitulo and len(divSubtitulo) > 0:
            subtitulo_post = divSubtitulo[0].getText()

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


def buscarLinksEnGoogle(posts, inicio, fin):
    for i in range(inicio, fin):
        try:
            print(i)
            post_link = posts[i][1]
            link_url = posts[i][2]
            post_fecha = posts[i][3]
            post_fecha = datetime.datetime.strptime(post_fecha, '%Y-%m-%d').date()
            print(link_url)

            titulo_post, subtitulo_post = getTituloFacebook(post_link)
            print(titulo_post)

            posts[i].append(titulo_post)
            posts[i].append(subtitulo_post)

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

                    if("FECHA NO ENCONTRADA" == fecha_portal):
                        continue

                    fecha_portal = datetime.datetime.strptime(
                        fecha_portal, '%Y-%m-%d %H:%M:%S')
                    fecha_portal = fecha_portal.date()
                    if(fecha_portal <= post_fecha):
                        linkMismoDominio.append(url)

            # Siempre doy prioridad al orden de google porque es mas problable que sea
            # mejor su medida de similitud que la que podamos calcular por
            # nuestros medios
            if (len(linkMismoDominio) > 1):
                print("Necesito Distancia de Texto")
                posts[i].append("Necesito Distancia de Texto")
            else:
                if (len(linkMismoDominio) == 1):
                    posts[i].append(linkMismoDominio[0])
                else:
                    print("No encontre link")
                    posts[i].append("No encontre link")

            time.sleep(10)
        except Exception as ex:
            columnas = len(posts[i]) + 1
            for _ in range(columnas, 8):
                posts[i].append("TIME OUT" + str(ex))
            print("TIME OUT")
            print(ex)

    return posts


def cargarCSVEnDataSet(nombreArchivoEntrada):
    csv = pd.read_csv(nombreArchivoEntrada, header=0,
                      sep=',', quotechar='\"', encoding="utf-8")
    return csv.values


def guardarEnCSV(posteos, nombreArchivoSalida):
    columnas = ['post_id', 'post_link', 'link',
                'post_fecha', 'post_titulo', 'post_subtitulo', 'UrlCompleta']

    df = pd.DataFrame(data=posteos, columns=columnas)
    df.to_csv(nombreArchivoSalida, index=False, columns=columnas, sep=';',
              quoting=csv.QUOTE_ALL, doublequote=True, quotechar='"', encoding="utf-16")


def armarRutaDatos(nombreArchivo):
    rutaADatos = os.path.join(os.path.dirname(__file__), 'data', nombreArchivo)
    return rutaADatos


nombreArchivoEntrada = armarRutaDatos('buscarEnGoogle_restantes.csv')
nombreArchivoSalida = armarRutaDatos('post_output.csv')
posts = cargarCSVEnDataSet(nombreArchivoEntrada).tolist()

inicio = 0
fin = len(posts)

postsConTitulo = buscarLinksEnGoogle(posts, inicio, fin)
guardarEnCSV(postsConTitulo, nombreArchivoSalida)
