# -*- coding: utf-8 -*-

import urllib.request
import bs4
import pandas as pd
import os
import numpy as np
import time
from urllib.parse import urlparse 

def getHtml(url):

	req = urllib.request.Request(url)
	try:
	    resp = urllib.request.urlopen(req)
	except:
		print("ERROR")
		return None
	else:
	    html = resp.read()
	    soup = bs4.BeautifulSoup(html, 'html.parser')
	    return soup

def getHtml2(url):

	req = urllib.request.Request(url)
	try:
	    resp = urllib.request.urlopen(req)
	except:
		print("ERROR")
		return None
	else:
	    html = resp.read()
	    soup = bs4.BeautifulSoup(html, 'html.parser')
	    return html


def getFechaNacion(url):
    soup = getHtml(url)
    for tag in soup.find_all("meta"):
        if tag.get("itemprop", None) == "datePublished":
            return tag.get("content", None)
    return "FECHA NO ENCONTRADA"


def getTemaNacion(url):
    soup = getHtml(url)
    contenedor = soup.find(class_='path floatFix breadcrumb')
    if(contenedor is None):
        contenedor = soup.find(class_='path patrocinado floatFix breadcrumb')
    elementosContenedor = contenedor.find_all("span")
    tag = elementosContenedor[1]
    if tag.get("itemprop", None) == "name":
        return tag.getText()
    return "TEMA NO ENCONTRADO"


def getVolantaNacion(url):
    soup = getHtml(url)
    contenedor = soup.find(class_='path floatFix breadcrumb')
    if(contenedor is None):
        contenedor = soup.find(class_='path patrocinado floatFix breadcrumb')
    if(contenedor is None):
        contenedor = soup.find(class_='path tema-espacio-hsbc floatFix breadcrumb')
    elementosContenedor = contenedor.find_all("span")
    if(len(elementosContenedor) > 2):
        tag = elementosContenedor[2]
        if tag.get("itemprop", None) == "name":
            # print(tag.getText()) 
            return tag.getText()
    return "VOLANTA NO ENCONTRADA"


def getTituloDiario(url, soup):
    #soup = getHtml(url)
    if (soup is not None):
        if (soup.h1 is not None):
            return(soup.h1.getText())
        else:
            return "TITULO No Encontrado"
    else:
        return "SOUP No Encontrado 2"


def getBajadaNacion(url):
    soup = getHtml(url)
    texto = "BAJADA NO ENCONTRADA"
    if (soup is not None):
        try:
            # Clarín
            bajada = soup.find(class_="bajada")
            # porque class es una palabra reservada
            texto = ""
            texto = bajada.getText()
        except:
            print(texto)
    return texto


def getTextoDiarioLaNacion(url):
    soup = getHtml(url)
    texto = "TEXTO DIARIO NO ENCONTRADO"
    if (soup is not None):
        # La Nación
        try:
            cuerpo = soup.find(id='cuerpo')
            parrafos = cuerpo.find_all('p')
            # parrafos = soup.find_all('p')
            texto = ""
            for p in parrafos:
                # print(p.getText())
                texto = texto + p.getText()
                # print(texto)
        except:
            print(texto)
    return texto


def getTextoDiarioClarin(url, soup):
    # soup = getHtml(url)
    texto = "TEXTO DIARIO NO ENCONTRADO"
    if (soup is not None):
        try:
            # Clarín
            cuerpo = soup.find(class_='body-nota')
            # porque class es una palabra reservada
            parrafos = cuerpo.find_all('p')
            # parrafos = soup.find_all('p')
            texto = ""
            for p in parrafos:
                # print(p.getText())
                texto = texto + p.getText()
                # print(texto)
        except:
            print(texto)
    return texto


def getFechaClarin(url, soup):
    # soup = getHtml(url)
    for tag in soup.find_all("meta"):
        if tag.get("itemprop", None) == "datePublished":
            return tag.get("content", None)
    return "FECHA NO ENCONTRADA"


def getTemaClarin(url, soup):
    # soup = getHtml(url)
    texto = "TEMA  NO ENCONTRADO"
    if (soup is not None):
        try:
            # Clarín
            # contenedor = soup.find(class_='nav-content')
            tema = soup.find(class_='header-section-name')
            texto = ""
            texto = tema.getText()
        except:
            print(texto)
    return texto


def getVolantaClarin(url, soup):
    # soup = getHtml(url)
    texto = "VOLANTA NO ENCONTRADA"
    if (soup is not None):
        try:
            # Clarín
            volanta = soup.find(class_='volanta')
            texto = ""
            texto = volanta.getText()
        except:
            print(texto)
    return texto


def getBajadaDiarioClarin(url, soup):
    # soup = getHtml(url)
    texto = "BAJADA NO ENCONTRADA"
    if (soup is not None):
        try:
            # Clarín
            bajada = soup.find(class_='bajada')
            # porque class es una palabra reservada
            parrafos = bajada.find_all('p')
            # parrafos = soup.find_all('p')
            texto = ""
            for p in parrafos:
                # print(p.getText())
                texto = texto + p.getText()
                # print(texto)
        except:
            print(texto)
    return texto


def getTituloFacebook(url):
	html = getHtml2(url)
	if (html is not None):
		# divs = soup.find_all('div', { 'class' : 'mbs _6m6 _2cnj _5s6c' })
		divLink = ""
		content = bs4.BeautifulSoup(html, 'lxml')
		a = content.find_all('div', {'class': 'mbs _6m6 _2cnj _5s6c'})
		print(a)
		for div in a:
			print(div)
		# print(divs)
		# for div in divs:
		# 	print(div['class'])
			# , { "class" : "mbs _6m6 _2cnj _5s6c" })
		
		# <div class="mbs _6m6 _2cnj _5s6c">
		# for d in div:
		# 	link = d.find('a')
		# 	print(link)
		# 	return link
	else:
		return ""
        
	
def loadCsvIntoDataSet():
	data_path = ''
	csv = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'BUSCAR_LINK_FALTANTE.csv'), header=0, sep=';', quotechar='\'', encoding = "utf-8" )
	return csv.values

def unshorten_url(url):
	req = urllib.request.Request(url)
	try:
	    resp = urllib.request.urlopen(req)
	except:
		return None
	else:
		resolvedURL = urllib.request.urlopen(url)
		return resolvedURL.url


def addColumnaTitulo():
    posts = loadCsvIntoDataSet().tolist()
    for i in range(0, len(posts)-1):
        #time.sleep(3)
        try:
            # print(posts[i]) 
            print(i)
            if (not posts[i][0] == 'link') or (posts[i][0] == 'link') :
                if (not(pd.isnull(posts[i][3]))):
                    url = unshorten_url(posts[i][3])
                    parsed_uri = urlparse(url)
                    domain = '{uri.netloc}'.format(uri=parsed_uri)
                    posts[i][4] = domain
                    if(not(pd.isnull(url)) and not(url is None)):
                        if (('lanacion.com' in url) and not('blogs.lanacion' in url)):
                            posts[i].append(url)
                            soup = getHtml(url)
                            posts[i].append(getFechaNacion(url))
                            # tema o seccion Ej: política, deportes
                            posts[i].append(getTemaNacion(url))
                            posts[i].append(getVolantaNacion(url))
                            posts[i].append(getTituloDiario(url, soup))
                            posts[i].append(getBajadaNacion(url))
                            posts[i].append(getTextoDiarioLaNacion(url))
                            # print(url)
                            getTituloFacebook(posts[i][2])
                        elif('clarin.com' in url):
                            posts[i].append(url)
                            soup = getHtml(url)

                            posts[i].append(getFechaClarin(url, soup))
                            posts[i].append(getTemaClarin(url, soup))
                            posts[i].append(getVolantaClarin(url, soup))
                            posts[i].append(getTituloDiario(url, soup))
                            posts[i].append(getBajadaDiarioClarin(url, soup))
                            posts[i].append(getTextoDiarioClarin(url, soup))
                            # print(posts[i])
                            getTituloFacebook(posts[i][2])
                        else:
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                            posts[i].append("OTRO MEDIO")
                    else:
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                         posts[i].append("URL NULL")
                else:
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
                    posts[i].append("LINK NULL")
            else:
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                posts[i].append("TIPO_POST ES LINK")
                # print(posts[i])
        except Exception as ex:
            columnas = len(posts[i]) + 1
            for j in range(columnas, 13):
                posts[i].append("TIME OUT")
            print("TIME OUT")
            print(ex)

    return posts


def saveInCsv(postsFinal):
    # fecha = datetime.now().strftime("%Y%m%d-%H%M")
    fileName = 'BUSCAR_LINK_FALTANTE.csv'
    # posts = np.asarray(postsFinal)

    columns = ['tipo_post', 'post_id', 'post_link','link','link_domain', 'UrlCompleta','fecha_hora_diario','tema','volanta','titulo_diario','bajada', 'texto_diario']
    # print(columns)
    print(postsFinal)
    # print(postsFinal[10145])
    df = pd.DataFrame(data=postsFinal, columns=columns)

    df.to_csv(os.path.join(os.path.dirname(__file__), 'data', fileName), index=False, columns=columns, sep=';', quotechar='"')

saveInCsv(addColumnaTitulo())

#to do:

# 2 - link caidos
# 3 - nombre del link en facebook (en <a>)

