# buscarLinksRotos
Busca una lista de links capturados de los posteos en las fanpages de Facebook en google y devuelve el link de más similitud.
Para eso busca en google el titulo del post más el dominio y toma los primeros 5 resultados. Entonces filtra aquellos resultados que son de la fecha de publicación o anteriores del dominio buscado armando una lista de resultados y elije el link de más similidad de la siguiente manera:
1- Si hay un solo link devuelvo ese
2- Si no hay links marco como irrecuperable
3- Si hay mas de un link lo tokenizo y aplico distancia TF/IDF y devuelvo el link más cercano al texto buscado.
El script toma un archivo CSV llamado "post_input.csv" y genera un archivo "post_output.csv" con las siguientes columnas:
1- post_id
2- post_link
3- link
4- post_fecha
5- post_subtitulo
6- UrlCompleta

Para ejecutar el script se necesita python3 con las librerias beautifulsoup y googlesearch.