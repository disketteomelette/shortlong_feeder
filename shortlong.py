
#-*- coding: UTF-8 -*-
import urllib.request
import time
import datetime
# import requests
import os
import os.path
import hashlib

# variables para posibles configuraciones futuras

datosminimos = 30  # número de capturas mínimas para empezar las funciones de análisis
archivohistorico = "historico.db"  # nombre archivo de histórico de precios. TODO: Eliminar parte del historico cuando sea muy grande.
archivobajistas = "bajistas.db"  # nombre archivo de patrones bajistas
archivoalcistas = "alcistas.db"  # nombre archivo de patrones alcistas
espera_datosminimos = 5  # segundos entre lecturas de datos mínimos
espera_datosaprocesar = 5  # segundos entre lecturas de datos en tiempo real para procesar
dato_por_momento = 30   # número de datos individuales de precio que llenarán el momento a analizar
                        # OJO: Este dato es crítico para almacenar los hashes. Si se aprende con 18 datos,
                        # si se cambia por otro no funcionará (o dará falsos positivos por colisión de hash)
subida_interesante = 2   # A partir de qué subida porcentual debemos aprender el patrón alcista
bajada_interesante = -2  # A partir de qué bajada porcentual debemos aprender el patrón bajista

def screen_clear():
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # windows
      _ = os.system('cls')

# declaramos las variables como strings vacíos
precioanterior = hashanterior = hdmmd5 = ""

print("[i] ShortLong v.0.1b - JCRueda.com" + "\n" + "[!] Usar bajo propia responsabilidad" + "\n")
time.sleep(1)

# Detectar si tenemos archivo de datos históricos
if os.path.isfile(archivohistorico):
    # TODO: o redirigir esto, o convertir el if en elseif. o así funciona bien? probar
    print ("[i] Detectado archivo histórico:", archivohistorico)
else:
    print("[!] Archivo de datos históricos inexistente!")
    print( "[!] ADVERTENCIA: No se han encontrado datos para comparar. A continuación el programa ahora obtendrá datos hasta tener una base mínima sobre la que empezar a entrenar.")
    print("[!] ¡Los resultados del bot no son nada fiables en este momento, al no existir datos!" + "\n")
    time.sleep(4)

    while datosminimos != 0:
        # en principio obtenemos precio y volumen de los últimos 15 minutos
        apiurl = urllib.request.urlopen("https://cryptoprediction.io/binance/btc/usdt/bitcointicker")
        reading = str(apiurl.read())
        precio = float(str(reading.split(sep='BitPrice">')[2]).split(sep='<')[0])
        volumen = int(float(reading.split(sep='vol15placeholder">')[1].split(sep='<')[0].split(sep="M")[0]) * 100000) # truco para decimales
        x = str(datetime.datetime.now()).split(sep=".")[0].replace(" ", "@")
        datastring = x + "#" + str(precio) + "#" + str(int(volumen)) # + "#" + "AAAAQAAAAA#BBBBTBBBBB"
        print("[i] [ Quedan " + str(datosminimos) + " datos ]", x, "-", precio, "USD -", volumen)
        datosminimos = datosminimos - 1

        # hacemos el append de los datos
        with open(archivohistorico, 'a') as file:
            file.write(datastring + " ")
        file.close()
        time.sleep(int(espera_datosminimos))

    # aqui salimos del bucle while porque ya tenemos una base sobre la que trabajar
    print("\n" + "[i] El motor ya tiene datos mínimos para empezar a entrenar." + "\n")

# TODO EN ORDEN, EMPEZAMOS ...
print ("\n" + "[*] *** Iniciando motor de comparación ***" + "\n")
print ("[*] Escribiendo cabecera del portal web...")
time.sleep(1)

while True:
    screen_clear()
    print ("[ ShortLong 0.01b - jcrueda.com ] ------------------------------------------------------------")
    print ("  https://github.com/disketteomelette")
    print("[?] Precio anterior a comparar con éste patrón:", precioanterior)
    print("[?] Hash anterior:", hdmmd5)
    preciomasanterior = precioanterior
    hashanterior = hdmmd5
    calificacionparaweb = ""
    tablacontenido = '<table class="table">'

    # ------------ CABECERA WEB -------------------
    # html, head, meta, body, cabecera:
    web = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="content-type" content="text/html; charset=UTF-8">' \
          '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">' \
          '<meta name="description" content=""><meta name="author" content=""><link rel="icon" href="index_files/favicon.ico">' \
          '<title>Shortlong v.0.01 - jcrueda.com</title><script type="text/javascript" src="https://www.gstatic.com/charts/loader.js">' \
          '</script><link href="index_files/bootstrap.css" rel="stylesheet"><link href="index_files/offcanvas.css" rel="stylesheet">' \
          '<META HTTP-EQUIV="REFRESH" CONTENT="30;URL=index.html"></head>'
    web = web + '<style>\n    .table td, .table th {\n        font-size: 10px;\n    }\n</style>'
    web = web + '<body class="bg-light"><nav class="navbar navbar-expand-md fixed-top navbar-dark bg-dark"><a class="navbar-brand" href="#">' \
                'Shortlong </a><button class="navbar-toggler p-0 border-0" type="button" data-toggle="offcanvas"><span class="navbar-toggler-icon">' \
                '</span></button><div class="navbar-collapse offcanvas-collapse" id="navbarsExampleDefault"><ul class="navbar-nav mr-auto">' \
                '<li class="nav-item active"><a class="nav-link" href="#">Inicio <span class="sr-only">(current)</span></a></li>' \
                '<li class="nav-item"><a class="nav-link" href="https://jcrueda.com">Acerca de</a></li></ul></div></nav>'
    # Inicio del script de la grafica de Google
    web = web + '<script type="text/javascript">\n'
    web = web + "google.charts.load('current', {'packages':['corechart']});\n"
    web = web + "google.charts.setOnLoadCallback(drawChart);\n"
    web = web + "function drawChart() {\n"
    web = web + "var data = google.visualization.arrayToDataTable([\n"
    web = web + "['Fecha', 'Posicion'],\n"

    # obtenemos el precio actual, lo añadimos a la lista
    apiurl = urllib.request.urlopen("https://cryptoprediction.io/binance/btc/usdt/bitcointicker")
    reading = str(apiurl.read())
    precio = str(reading.split(sep='BitPrice">')[2]).split(sep='<')[0]
    volumen = int(float(reading.split(sep='vol15placeholder">')[1].split(sep='<')[0].split(sep="M")[0]) * 100000)  # Truco para evitar decimales
    x = str(datetime.datetime.now()).split(sep=".")[0].replace(" ", "@")
    datastring = x + "#" + str(precio) + "#" + str(int(volumen))  # + "#" + "AAAAQAAAAA#BBTBB"
    with open(archivohistorico, 'a') as file:
        file.write(datastring + " ")
    file.close()

    # Abrimos el archivo historico
    content_variable = open(archivohistorico, "r")
    file_lines = str(content_variable.readlines()).split(" ")
    content_variable.close()

    # Contamos número de líneas para saber cuáles seleccionar, y las seleccionamos
    numerolineas = int(len(file_lines)) - 1
    numeromenos = numerolineas - int(dato_por_momento)

    # PROCESAR LOS ÚLTIMOS X DATOS (VOL MAX, PRECIO MAX, Y LUEGO REPRESENTACIÓN GRÁFICA DATO POR DATO)

    # Recorremos y obtenemos el máximo
    for barra in file_lines[numeromenos:numerolineas]:
        # Para visualizar las líneas que se van a preprocesar, descomentar abajo:
        # print(barra)

        # Con un bucle for se recorren las ultimas lineas y se va almacenando la cifra mayor de precios
        # máximos y la menor de precios bajos para establecer el rango en el que se moverá la gráfica
        precio_mayor = volumen_mayor = -1
        menorhastaahora = volminhastaahora = 99999999999999999999999999

        for barra in file_lines[numeromenos:numerolineas]:
            precioacomprobar = float(barra.split("#")[1])
            volumenacomprobar = float(barra.split("#")[2])
            if precioacomprobar > precio_mayor:
                precio_mayor = precioacomprobar + 1
            if precioacomprobar < menorhastaahora:
                menorhastaahora = precioacomprobar - 1
            if volumenacomprobar > volumen_mayor:
                volumen_mayor = volumenacomprobar + 1
            if volumenacomprobar < volminhastaahora:
                volminhastaahora = volumenacomprobar - 1

        rangodeprecios = round(precio_mayor - menorhastaahora)
        rangodevolumen = round(volumen_mayor - volminhastaahora)

    parte = rangodeprecios / 10

    print("[+] Precio máximo:", precio_mayor, " - Mínimo:", menorhastaahora, " - Rango:", rangodeprecios)
    print("[+] Dividiendo", rangodeprecios, "entre 10 puntos por columna para precio")
    print("[!] Volumen maximo:", volumen_mayor, " - Mínimo:", volminhastaahora, " - Rango:", rangodevolumen)

    # Establecemos los rangos de PRECIOS (R) donde debe caer cada lectura para asignarle un punto activo
    # TODO para la próxima: ¡Matrices!

    x0 = str(round(precio_mayor + 1)) + ":" + str(round(int(precio_mayor - parte) - 1))
    x1 = str(round(int(precio_mayor - parte) - 1)) + ":" + str(round(int(precio_mayor - (parte * 2)) - 1))
    x2 = str(round(int(precio_mayor - (parte * 2)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 3)) - 1))
    x3 = str(round(int(precio_mayor - (parte * 3)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 4)) - 1))
    x4 = str(round(int(precio_mayor - (parte * 4)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 5)) - 1))
    x5 = str(round(int(precio_mayor - (parte * 5)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 6)) - 1))
    x6 = str(round(int(precio_mayor - (parte * 6)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 7)) - 1))
    x7 = str(round(int(precio_mayor - (parte * 7)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 8)) - 1))
    x8 = str(round(int(precio_mayor - (parte * 8)) - 1)) + ":" + str(round(int(precio_mayor - (parte * 9)) - 1))
    x9 = str(round(int(precio_mayor - (parte * 9)) - 1)) + ":" + str(round(precio_mayor - (parte * 10) - 1))
    print("[i] Rangos de precios: [ x0 =", x0, "] [ x1 =", x1, "] [ x2 =", x2, "] [ x3 =", x3, "] [ x4 =", x4, "]")
    print("                       [ x5 =", x5, "] [ x6 =", x6, "] [ x7 =", x7, "] [ x8 =", x8, "] [ x9 =", x9, "] ")

    # Establecemos los rangos de VOLUMEN (V) donde debe caer cada lectura para asignarle un X

    partevolumen = int(round(rangodevolumen / 5, 2))
    print("[i] Los rangos de volumen se partirán en partes de", partevolumen, "(", str(partevolumen / 100000), " mill.)")
    v0 = str(int(round((volumen_mayor + 2), 2) - 1)) + ":" + str(int(round(volumen_mayor - partevolumen + 1, 2)))
    v1 = str(int(v0.split(sep=":")[1]) + 1) + ":" + str(int(round(float(v0.split(sep=":")[1]) - float(partevolumen), 2)))
    v2 = str(int(v1.split(sep=":")[1]) + 1) + ":" + str(int(round(float(v1.split(sep=":")[1]) - float(partevolumen), 2)))
    v3 = str(int(v2.split(sep=":")[1]) + 1) + ":" + str(int(round(float(v2.split(sep=":")[1]) - float(partevolumen), 2)))
    v4 = str(int(v3.split(sep=":")[1]) + 1) + ":" + str(int(round(float(v3.split(sep=":")[1]) - float(partevolumen) - 2, 2)))
    print("[i] Rangos de volumen: [ v0 =", v0, "] [ v1 =", v1, "] [ v2 =", v2, "] [ v3 =", v3, "] [ v4 =", v4, "]")

    # TODO: volvemos a recorrer para generar la huella de cada columna de la grafica actual
    # Primero, limpiamos la variable del hash del momento y otras

    hashdelmomento = graficoahora = bufferdatos = ""
    cuentalineas = 0
    print ("[i] Procesando", dato_por_momento, "datos para obtener su representación..." + "\n")

    for barra in file_lines[numeromenos:numerolineas]:
        bfecha = barra.split("#")[0]
        bprecio = round(float(barra.split("#")[1]))
        bvolumen = round(float(barra.split("#")[2]))
        r0 = r1 = r2 = r3 = r4 = r5 = r6 = r7 = r8 = r9 = "Z"
        va0 = va1 = va2 = va3 = va4 = va5 = va6 = va7 = va8 = va9 = "Z"

        # MARCAR EN LA BARRA LOS VALORES SEGÚN COINCIDAN EN LOS RANGOS DE PRECIO Y VOLUMEN
        if bprecio in range(int(x0.split(sep=":")[1]), int(x0.split(sep=":")[0])): r0 = "X"
        if bprecio in range(int(x1.split(sep=":")[1]), int(x1.split(sep=":")[0])): r1 = "X"
        if bprecio in range(int(x2.split(sep=":")[1]), int(x2.split(sep=":")[0])): r2 = "X"
        if bprecio in range(int(x3.split(sep=":")[1]), int(x3.split(sep=":")[0])): r3 = "X"
        if bprecio in range(int(x4.split(sep=":")[1]), int(x4.split(sep=":")[0])): r4 = "X"
        if bprecio in range(int(x5.split(sep=":")[1]), int(x5.split(sep=":")[0])): r5 = "X"
        if bprecio in range(int(x6.split(sep=":")[1]), int(x6.split(sep=":")[0])): r6 = "X"
        if bprecio in range(int(x7.split(sep=":")[1]), int(x7.split(sep=":")[0])): r7 = "X"
        if bprecio in range(int(x8.split(sep=":")[1]), int(x8.split(sep=":")[0])): r8 = "X"
        if bprecio in range(int(x9.split(sep=":")[1]), int(x9.split(sep=":")[0])): r9 = "X"
        if bvolumen in range(int(v0.split(sep=":")[1]), int(v0.split(sep=":")[0])): va0 = "X"
        if bvolumen in range(int(v1.split(sep=":")[1]), int(v1.split(sep=":")[0])): va1 = "X"
        if bvolumen in range(int(v2.split(sep=":")[1]), int(v2.split(sep=":")[0])): va2 = "X"
        if bvolumen in range(int(v3.split(sep=":")[1]), int(v3.split(sep=":")[0])): va3 = "X"
        if bvolumen in range(int(v4.split(sep=":")[1]), int(v4.split(sep=":")[0])): va4 = "X"

        # MONTAR CADA BARRA Y MOSTRARLA "BONITA"
        cuentalineas = cuentalineas + 1
        master = "A" + r0 + r1 + r2 + r3 + r4 + r5 + r6 + r7 + r8 + r9 + "B" + va0 + va1 + va2 + va3 + va4 + "C" + str(bprecio)
        rgprecio = master.split("B")[0].split("A")[1].replace("Z", " ")
        rgvolumen = master.split("B")[1].split("C")[0].replace("Z", " ")
        print(bprecio, "|", rgprecio, "|", rgvolumen, "|",  round(float(bvolumen / 100000), 1), "|", master, "|", bvolumen, "|", barra.split(sep="#")[0].replace("@", " "), "[", cuentalineas, "]",)
        hashdelmomento = hashdelmomento + master

        tablacontenido = tablacontenido + '<tr><th scope="col">' + str(barra.split(sep="#")[0].split(sep="@")[1]) + '</th><th scope="col">' + str(bprecio)
        tablacontenido = tablacontenido + '</th><th scope="col">' + str(round(float(bvolumen / 100000), 1)) + '</th><th scope="col">' + master + "</th></tr>"
        # tablacontenido = hora;precio;volumen;codigo[espacio]

        # --WEB-- Alimentar el gráfico con los datos de esta tanda
        # Buscamos la posición de X en la gráfica de precios
        posengrafica_precio = rgprecio.find("X")
        # Formateamos para quedarnos sólo con la hora después de la @
        hora_precio = barra.split(sep="@")[1].split(sep="#")[0]
        web = web + "['" + str(hora_precio) + "', " + str(posengrafica_precio) + "],\n"
        # Almacenar todas las lineas
        bufferdatos = bufferdatos + " " + master
        graficoahora = graficoahora + "A" + r0 + r1 + r2 + r3 + r4 + r5 + r6 + r7 + r8 + r9 + "B" + va0 + va1 + va2 + va3 + va4

        # TODO: limpiamos las variables para el loop?

    # recuperamos el último dato que guardamos en el buffer
    listadatos = str(bufferdatos).split(" ")
    precioanterior = listadatos[-1].split("C")[1]
    print("\n" + "[i]", len(listadatos) - 1, "elementos de patrón. Precio actual a comparar con anterior:", precioanterior, "(", listadatos[-1], ")")

    # Comparamos preciomasanterior (precio de antes) con precioanterior (precio de ahora último)
    # Pero solo actuamos si preciomasanterior es distinto de "nada"
    if preciomasanterior != "":
        experimento = int(precioanterior) - int(preciomasanterior)
        # print ("---- experimento:", experimento)
        if float(experimento) < 0:
            # Para bajista, ok
            regladetres = 100 - (float(precioanterior) * 100 / float(preciomasanterior))
            porcentaje = "-" + str(round(regladetres, 4)) + "%"
            porcentaje2 = abs(float(str(round(regladetres, 4))))
            bajada_interesante = abs(bajada_interesante)
            print("[i] El patrón anterior es bajista:", porcentaje," (", experimento, "USD ) -", hashanterior)
            calificacionparaweb = 'El patron anterior (' + hashanterior + ') es <b style="color:red">BAJISTA</b>. ' + str(porcentaje) + " (" + str(experimento) + " USD) - "

            if porcentaje2 < bajada_interesante :
                print("[x] La bajada no es interesante. Omitimos el patrón anterior porque", porcentaje2, "no es mayor que el tope de", bajada_interesante)
                calificacionparaweb = calificacionparaweb + "<b>NO</b> es un patron interesante (" + str(
                    float(str(round(regladetres, 4)))) + " < " + str(bajada_interesante) + ")"
            else:
                print("[!] La bajada es interesante porque", float(str(round(regladetres, 4))) * -1, "era menor a -", bajada_interesante)
                calificacionparaweb = calificacionparaweb + "<b>SÍ</b> es un patron interesante (" + str(
                    float(str(round(regladetres, 4)))) + " > " + str(bajada_interesante) + ")"
                with open(archivobajistas, 'a') as file:
                    file.write(hashanterior + ";" + porcentaje + "\n")
                file.close()

        else:
            regladetres = (float(precioanterior) * 100 / float(preciomasanterior)) - 100
            porcentaje = "+" + str(round(regladetres, 4)) + "%"
            print ("[i] El patrón anterior es alcista: ", porcentaje," (", experimento, "USD ) -", hashanterior)
            calificacionparaweb = 'El patron anterior (' + hashanterior + ') es <b style="color:green">ALCISTA</b>. ' + str(
                porcentaje) + " (" + str(experimento) + " USD) - "
            if float(str(round(regladetres, 4))) < subida_interesante:
                print("[x] La subida no es interesante. Omitimos el patrón anterior porque", float(str(round(regladetres, 4))), "es inferior al tope de", subida_interesante)
                calificacionparaweb = calificacionparaweb + "<b>NO</b> es un patron interesante (" + str(float(str(round(regladetres, 4)))) + " < " + str(subida_interesante) + ")"
            else:
                print("[!] La subida es interesante, porque", float(str(round(regladetres, 4))), "era mayor a", subida_interesante)
                calificacionparaweb = calificacionparaweb + "<b>SÍ</b> es un patron interesante (" + str(
                    float(str(round(regladetres, 4)))) + " > " + str(subida_interesante) + ")"
                with open(archivoalcistas, 'a') as file:
                    file.write(hashanterior + ";" + porcentaje + "\n")
                file.close()
    else:
        print("[!] Primera ejecución! En el siguiente precio se analizará la variación.")

    print ("\n" + "[i] Analisis del momento actual para comparar luego:" + "\n")

    # --- WEB --- cerramos el script
    web = web + "]);\n"
    web = web + "var options = {\n"
    web = web + "title: '',\n"
    web = web + "curveType: 'function',\n"
    web = web + "legend: { position: 'none' }\n" 
    web = web + "};\n"
    web = web + "var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));\n"
    web = web + "chart.draw(data, options);\n"
    web = web + "}\n"
    web = web + "</script>\n"

    # Generar hash del momento
    # print("[i] Momento en crudo:", hashdelmomento)  # debug
    # no guardamos el precio en sí, solo las posiciones.
    print("[i] Datos actuales:", graficoahora)
    hdmmd5 = hashlib.md5(graficoahora.encode()).hexdigest()
    print("[i] Hash actual:", hdmmd5)

    # --- WEB --- Completamos y guardamos el archivo
    # hash actual y anterior
    web = web + '<main role="main" class="container"><div class="d-flex align-items-center p-3 my-3 text-white-50 bg-purple ' \
                'rounded box-shadow"><div class="lh-100"><h6 class="mb-0 text-white lh-100">Hash actual: ' + hdmmd5
    web = web + '</h6><small>Hash anterior: ' + hashanterior + '</small></div></div>'

    # Titulo y <div> del gráfico

    web = web + '<div class="my-3 p-3 bg-white rounded box-shadow"><h6 class="border-bottom border-gray pb-2 mb-0">Analisis de patron actual' \
                '</h6><div class="media text-muted pt-3"><div id="curve_chart" style="width: 100%; height: 100%;"></div></div>'

    # --- WEB --- TEXTO BAJO LA GRÁFICA
    web = web + '<div class="media text-muted pt-3"><p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">' \
                '<strong class="d-block text-gray-dark">Datos asociados al patron actual<br></strong>'\

    # --------- DATOS ASOCIADOS AL PATRÓN ACTUAL -----------
    web = web + "Estos son los datos de referencia que se estan usando para analizar el actual patron.<br></br>"
    web = web + "Precio maximo: " + str(precio_mayor) + " - Minimo: " + str(menorhastaahora) + " - Rango: " + str(rangodeprecios) + "<br>"
    web = web + "Volumen maximo: " + str(volumen_mayor) + " - Minimo: " + str(volminhastaahora) + " - Partes: " + str(partevolumen) + "</p></div>"
    tablaheader = ""

    print(tablacontenido)

    web = web + '<div class="media text-muted pt-3"><p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">' \
                '<strong class="d-block text-gray-dark">Conclusiones del patron anterior<br></strong>Este apartado refleja las ' \
                'conclusiones y la calificacion que ha recibido el patron anterior segun el resultado del patron actual.' \
                '<br></br>' + calificacionparaweb + '</p></div>'

    # Mostrar datos sobre la configuración del script (variables modificables del principio)
    web = web + '<div class="media text-muted pt-3"><p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">' \
                '<strong class="d-block text-gray-dark">Configuracion del programa<br></strong>'
    web = web + 'Refleja los valores de las variables de configuracion del principio del script.<br></br>'
    web = web + 'Capturas minimas necesarias: ' + str(datosminimos) + "<br>"
    web = web + 'Archivo historico: ' + archivohistorico + "<br>"
    web = web + 'Archivo bajistas:' + archivobajistas + "<br>"
    web = web + "Segundos entre datos minimos: " + str(espera_datosminimos) + "<br>"
    web = web + "Segundos entre capturas a tiempo real: " + str(espera_datosaprocesar) + "<br>"
    web = web + "Numero de datos por patron: " + str(dato_por_momento) + "<br>"
    web = web + "Registrar desde porcentaje de subida: " + str(subida_interesante) + "%<br>"
    web = web + "Registrar desde porcentaje de bajada: " + str(bajada_interesante) + "%<br"
    web = web + '</p></div>'

    # MONTAR LA TABLA ------------------- WEB -----------------------------------
    web = web + '<div class="media text-muted pt-3"><a>' + tablaheader + tablacontenido + '</table></a></div>'
    # Terminamos la web ...
    web = web + '</main><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" preserveAspectRatio="none" style="display: none; visibility: hidden; position: absolute; top: -100%; left: -100%;"><defs><style type="text/css"></style></defs><text x="0" y="2" style="font-weight:bold;font-size:2pt;font-family:Arial, Helvetica, Open Sans, sans-serif">32x32</text></svg></body></html>'
    # guardo utilizando w que por lo visto reemplaza todo el contenido
    with open("index.html", 'w') as file:
        file.write(web)
    file.close()
    print("[+] Se ha escrito el index.html. Si aun no lo ha hecho, abralo. Se actualizara periodicamente.")
    time.sleep(espera_datosaprocesar)

