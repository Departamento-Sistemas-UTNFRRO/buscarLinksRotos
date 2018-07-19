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

import datetime
import TFIDF
import time
from googlesearch import search
from pyfbutils.DataSetCSV import DataSetCSV
from pyfbutils.PostFacebook import PostFacebook
from pyfbutils.Link import Link
from pyfbutils.ClarinPost import ClarinPost
from pyfbutils.NacionPost import NacionPost


def buscarLinksEnGoogle(datasetCSV):
    posts = datasetCSV.dataset

    for i in range(datasetCSV.inicio, datasetCSV.fin):
        try:
            print(i)
            post_link = posts[i][1]
            link_url = posts[i][2]
            print(link_url)

            link = Link(link_url)
            print(link.linkDomain)
            if link.esLinkAOmitir():
                print('Omitiendo')
                posts[i].append("LINK NULL")
                posts[i].append("LINK NULL")
                posts[i].append("LINK NULL")
                continue

            postFacebook = PostFacebook(post_link)
            datosPost = postFacebook.getInfoPostFacebook()
            titulo_post = datosPost[0]
            posts[i].append(titulo_post)
            posts[i].append(datosPost[1])
            print(titulo_post)

            post_fecha = convertirTextoAFecha(posts[i][3])

            # Buscar el link en base a los datos que tengo
            # texto del post
            # de los resultados elegir segun la fecha tmb

            linkMismoDominio = []

            # en caso que funcione el link lo agrego directamente
            if (link.linkReal is not None):
                linkMismoDominio.append(link.linkReal)

            texto_a_buscar = titulo_post.replace('"', '') + " " + link.linkDomain
            for url in search(texto_a_buscar, tld='com.ar', lang='es', stop=5):
                print(url)
                if(link.linkDomain in url):
                    # FIXME: aca puedo usar la clase link de nuevo??
                    if('clarin' in url):
                        postPortal = ClarinPost(link)
                        fecha_portal = postPortal.getFecha()
                    else:
                        if ('nacion' in url):
                            postPortal = NacionPost(link)
                            fecha_portal = postPortal.getFecha()
                        else:
                            continue

                    if(fecha_portal == "FECHA NO ENCONTRADA"):
                        continue

                    fecha_portal = datetime.datetime.strptime(
                        fecha_portal, '%Y-%m-%d %H:%M:%S').date()
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
