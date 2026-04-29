# Tarea 1 Matias Vasquez

prepare_data.py (El Filtro)

Su función: Transformar el dataset masivo de Google (que tiene millones de filas de todo el mundo o del país) en un archivo pequeño y manejable de solo las 5 zonas de Santiago que pide la tarea.

    Cómo funciona: Lee el archivo original en "pedazos" (chunks) para no saturar tu RAM. Compara la latitud y longitud de cada edificio con los cuadros (bounding boxes) de Providencia, Las Condes, etc. Si el edificio cae dentro, le pone una etiqueta (Z1, Z2...) y lo guarda.

2. response_generator/main.py (El Cerebro)

Su función: Es una API (usando FastAPI) que simula el servidor de información geoespacial. Es el único que habla con la base de datos de caché (Redis).

    Cómo funciona:

        Carga inicial: Al arrancar, lee el CSV que generó el script anterior y lo sube a la RAM.

        El flujo de consulta: Cuando recibe una petición (ej. Q1), primero le pregunta a Redis: "¿Tienes el conteo de la Z1 con confianza 0.7?".

        Hit vs Miss: Si Redis dice SÍ (Hit), entrega el dato rápido. Si dice NO (Miss), usa Pandas para filtrar el DataFrame en RAM, calcula el resultado, lo guarda en Redis para la próxima vez y lo entrega.


3. traffic_generator/main.py (El Cliente)

Su función: Simular a los camiones o empresas de logística haciendo miles de preguntas por segundo para estresar el sistema.

    Cómo funciona: Tiene un bucle infinito (o por tiempo) que elige una zona y una consulta al azar.

        Distribución Uniforme: Elige Z1, Z2, Z3, Z4 o Z5 con la misma probabilidad (20% cada una). Esto hace que la caché sea menos eficiente.

        Distribución Zipf: Elige mucho más seguido la Z1 y la Z2. Esto debería disparar el "Cache Hit Rate" en tus experimentos.


4. metrics/main.py (El Auditor)

Su función: Es un observador silencioso. No calcula edificios, solo anota qué tan rápido y qué tan eficiente es el sistema.

    Cómo funciona: Recibe un aviso cada vez que el traffic_generator termina una consulta. Anota si fue "Hit" o "Miss" y cuánto demoró (latencia).

5. Como correr:
  docker-compose up --build

  En el archivo docker-compose.yml se cambia el tamaño de cache y si es Random, LRU o LFU

  En el main de trafic_generator.py se puede elegir distribucion uniforme o zipf

  
