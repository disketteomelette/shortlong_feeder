# shortlong_feeder
Experiment to feed a db with patterns (hashes of up/down patterns) of BTC prices using my own machine learning techniques.
![shortlong_feeder](https://github.com/disketteomelette/shortlong_feeder/blob/main/shortlong.png?raw=true)

Esta aplicación es una primera parte de un script. Se encarga de utilizar fuentes web para obtener el precio de criptomonedas (en este caso, BTC). Cuando se tiene un mínimo de datos requeridos, el programa se encarga de analizar (cuando se obtenga el siguiente dato) si el patrón anterior ha resultado ser alcista o bajista, y en su caso, genera un hash y lo guarda en un archivo de texto clasificado, a modo de base de datos. 

La segunda parte del programa (que no está subida) es muy similar a éste, pero simplemente analiza con antelación si el patrón actual coincide con otro de la base de datos que ha resultado ser alcista o bajista. Esto, en teoría, nos da una suposición de qué va a pasar con el precio en los próximos segundos. 

El programa contiene unas variables de configuración al principio. Siguiendo el principio fractal del análisis técnico, sabemos que las "figuras" o patrones se producen tanto a nivel micro como macro, por lo que resulta interesante guardar patrones en un corto espacio de tiempo y con posterioridad probar si se producen también en patrones con un intervalo mayor. Así, podemos poblar la base de datos relativamente rápido (digo relativamente, pues los cálculos que he realizado dicen que serían años) y luego modificar el intervalo de tiempo a, por ejemplo, minutos o horas, en el modo de detección. 

Este script fue discontinuado porque actualmente trabajo en otro que no sólo tiene en cuenta el precio, sino el volumen (el segundo indicador de análisis técnico más importante a la hora de analizar las gráficas) y que además tanto la parte que "enseña" como la parte que "comprueba" se encuentran en el mismo script. En este programa ya se incluye la valoración de volumen, pero no se utiliza para la representación gráfica. Para solucionar lo del tiempo, se utilizan datos históricos en csv que son procesados en segundos (viva python!). Pero eso es otra historia, y ya lo subiré.

El programa funciona de la siguiente manera: Obtiene un determinado número de precios, que se irán sustituyendo mediante FIFO (es decir, el primer precio se eliminará para dar paso al último precio). De esos precios, se obtiene el máximo y el mínimo, y se crean intervalos. Luego se analiza precio por precio y se le asigna una posición en unos intervalos de 0 a 9 que serán representados en la gráfica. Esto se hace para que, con independencia de los precios, los intervalos sean los mismos. Entonces, si el siguiente valor sube respecto al anterior, se califica el patrón anterior analizado como alcista, y si no, bajista. Si la variación es mínima o no coincide con lo establecido, no lo guarda, y sí en otro caso. 

En fin. Movidas.

