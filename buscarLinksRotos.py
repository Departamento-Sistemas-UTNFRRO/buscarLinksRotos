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
from googlesearch import search


linkMapeados = {
    'a.ln.com.ar': 'www.lanacion'
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


def buscarLinksEnGoogle(nombreArchivoEntrada):
    posts = loadCsvIntoDataSet(nombreArchivoEntrada).tolist()
    # for i in range(0, len(posts)):
    for i in range(0, 5):
        try:
            print(i)
            link_url = posts[i][3]
            texto_post = posts[i][5]
            print(link_url)
            print(texto_post)

            if(texto_post in textosAOmitir):
                print('Omitiendo')
                continue

            # req = urllib.request.Request(link_url)
            # urlOriginal = alargar_url(req)
            domain = ObtenerDominioUrlMapeado(link_url)
            print(domain)

            # Buscar el link en base a los datos que tengo
            # texto del post
            # de los resultados elegir segun la fecha tmb

            linkMismoDominio = []
            for url in search(posts[i][5], tld='com.ar', lang='es', stop=5):
                # print(url)
                # FIXME: si es uno solo entonces es el link que busco
                # FIXME: buscar la fecha a ver si coincide cuando hay mas de uno
                if(domain in url):
                    print('mismo dominio')
                    print(url)
                    linkMismoDominio.append(url)

            # Siempre doy prioridad al orden de google porque es mas problable que sea
            # mejor su medida de similitud que la que podamos calcular por nuestros medios

            if(len(linkMismoDominio) == 1):
                posts[i].append(linkMismoDominio[0])
            else:
                print('Mas de uno aca ver por fecha y dsp por mineria de texto')
                posts[i].append("LINK NULL")

        except Exception as ex:
            columnas = len(posts[i]) + 1
            for _ in range(columnas, 14):
                posts[i].append("TIME OUT")
            print("TIME OUT")
            print(ex)

    return posts


def loadCsvIntoDataSet(nombreArchivoEntrada):
    csv = pd.read_csv(nombreArchivoEntrada, header=0,
                      sep=',', quotechar='\"', encoding="utf-8")
    return csv.values


def saveInCsv(postsFinal, nombreArchivoSalida):
    columns = ['tipo_post', 'post_id', 'post_link', 'link',
               'link_domain', 'post_message', 'UrlCompleta']

    df = pd.DataFrame(data=postsFinal, columns=columns)
    df.to_csv(nombreArchivoSalida, index=False, columns=columns, sep=';',
              quoting=csv.QUOTE_ALL, doublequote=True, quotechar='"', encoding="utf-8")


def armarRutaDatos(nombreArchivo):
    rutaADatos = os.path.join(os.path.dirname(__file__), 'data', nombreArchivo)
    return rutaADatos


nombreArchivoEntrada = armarRutaDatos('buscarEnGoogle_485.csv')
nombreArchivoSalida = armarRutaDatos('post_output.csv')
postsConTitulo = buscarLinksEnGoogle(nombreArchivoEntrada)
saveInCsv(postsConTitulo, nombreArchivoSalida)
