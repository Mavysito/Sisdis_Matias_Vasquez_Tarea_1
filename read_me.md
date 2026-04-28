prepare_data.py (El Filtro)

Su función: Transformar el dataset masivo de Google (que tiene millones de filas de todo el mundo o del país) en un archivo pequeño y manejable de solo las 5 zonas de Santiago que pide la tarea.

    Cómo funciona: Lee el archivo original en "pedazos" (chunks) para no saturar tu RAM. Compara la latitud y longitud de cada edificio con los cuadros (bounding boxes) de Providencia, Las Condes, etc. Si el edificio cae dentro, le pone una etiqueta (Z1, Z2...) y lo guarda.

    Puntos de error humano:

        Coordenadas invertidas: Confundir latitud con longitud o poner los signos incorrectos (en Chile ambos son negativos).

        Rutas de archivos: Como ya viste, que el script no "vea" el archivo Data.csv.

        Columnas: Si el CSV original tiene nombres distintos (ej: lat en vez de latitude), el script fallará.

2. response_generator/main.py (El Cerebro)

Su función: Es una API (usando FastAPI) que simula el servidor de información geoespacial. Es el único que habla con la base de datos de caché (Redis).

    Cómo funciona:

        Carga inicial: Al arrancar, lee el CSV que generó el script anterior y lo sube a la RAM.

        El flujo de consulta: Cuando recibe una petición (ej. Q1), primero le pregunta a Redis: "¿Tienes el conteo de la Z1 con confianza 0.7?".

        Hit vs Miss: Si Redis dice SÍ (Hit), entrega el dato rápido. Si dice NO (Miss), usa Pandas para filtrar el DataFrame en RAM, calcula el resultado, lo guarda en Redis para la próxima vez y lo entrega.

    Puntos de error humano:

        Host de Redis: En el código debe decir host="cache" (el nombre del servicio en el docker-compose), no localhost, porque dentro de la red de Docker los contenedores se llaman por su nombre de servicio.

        Serialización: Intentar guardar un objeto de Pandas directamente en Redis. Redis solo entiende texto (strings), por eso usamos json.dumps().

3. traffic_generator/main.py (El Cliente)

Su función: Simular a los camiones o empresas de logística haciendo miles de preguntas por segundo para estresar el sistema.

    Cómo funciona: Tiene un bucle infinito (o por tiempo) que elige una zona y una consulta al azar.

        Distribución Uniforme: Elige Z1, Z2, Z3, Z4 o Z5 con la misma probabilidad (20% cada una). Esto hace que la caché sea menos eficiente.

        Distribución Zipf: Elige mucho más seguido la Z1 y la Z2. Esto debería disparar el "Cache Hit Rate" en tus experimentos.

    Puntos de error humano:

        URLs incorrectas: Si el puerto en el docker-compose es el 8000 pero el script apunta al 5000, nunca habrá comunicación.

        Velocidad de ráfaga: Si no pones un pequeño time.sleep(), el generador puede saturar el procesador antes de que la caché pueda reaccionar.

4. metrics/main.py (El Auditor)

Su función: Es un observador silencioso. No calcula edificios, solo anota qué tan rápido y qué tan eficiente es el sistema.

    Cómo funciona: Recibe un aviso cada vez que el traffic_generator termina una consulta. Anota si fue "Hit" o "Miss" y cuánto demoró (latencia). Cuando tú entras a la URL /report, hace los cálculos matemáticos (promedios, percentiles p95) para que tú solo los copies y pegues en tu informe de LaTeX.

    Puntos de error humano:

        Reinicio de datos: Si apagas los contenedores y no guardas los logs en un volumen o base de datos, perderás los datos para el informe.

        División por cero: Si pides un reporte antes de haber enviado tráfico, el cálculo del "Hit Rate" fallará porque no hay registros.

Resumen del Flujo de Datos
Checklist Final para mañana:

    Nombres en Docker: Revisa que en el docker-compose.yml los nombres de los servicios coincidan con las URLs en los main.py.

    Dataset: Verifica que el archivo santiago_buildings.csv esté dentro de la carpeta data y que esta carpeta esté mapeada en los volumes del docker-compose.

    Redis: Asegúrate de que el límite de memoria (--maxmemory) sea pequeño al principio para que puedas ver cómo Redis borra datos (evicción), de lo contrario, si tu dataset es pequeño, nunca verás "Misses" una vez que la caché se llene.