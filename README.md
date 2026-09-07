# periodico-tribunal

Plataforma de noticias basada en microservicios: gestión de contenidos (backoffice), publicación/consulta de artículos, un microservicio de IA (embeddings/RAG con LLM) y un frontend en Angular. La comunicación entre microservicios se hace mediante eventos con Kafka (Redpanda).

## 1. Contenido del proyecto

```
periodico-tribunal/
├── MicroBackOffice/            # Microservicio Spring Boot (Java 21 + Gradle) - gestión de artículos y categorías
│   ├── src/main/java/project/newspaper/
│   │   ├── application/        # Casos de uso: ArticleApplicationService, CategoryApplicationService
│   │   ├── domain/              # Entidades y eventos: Article/CategoryCreatedEvent, CreationStatus, State...
│   │   └── infraestructure/
│   │       ├── api/             # Controladores REST: ArticleController, CategoryController
│   │       └── kafka/           # Productor y listeners de confirmación (Kafka)
│   ├── src/main/resources/application.yml   # Config: puerto 8081, MySQL, Kafka
│   └── Dockerfile
│
├── MicroContent/               # Microservicio Spring Boot (Java 21 + Gradle) - contenido público, IA y memoria conversacional
│   ├── src/main/java/project/newspaper/
│   │   ├── application/        # ArticleService, CategoryService
│   │   ├── domain/              # Article, Category, MemoryDocument, eventos de indexado/embeddings
│   │   └── infraestructure/
│   │       ├── api/             # ArticleController, CategoryController, MemoryController, QuestionController
│   │       └── kafka/           # Listeners de creación de artículos/categorías, eventos de indexado
│   ├── src/main/resources/application.yml   # Config: puerto 8083, MongoDB, Kafka
│   ├── frontcontent/            # Frontend Angular 19 (SPA del periódico)
│   │   └── src/app/
│   │       ├── core/layout/     # Layout general: header, footer, categorías, chat
│   │       ├── feature/         # Portada, detalle de artículo
│   │       └── views/           # Vistas adicionales
│   └── Dockerfile
│
├── MicroLLM/                   # Microservicio Python (FastAPI) - embeddings, RAG y respuestas con LLM (Ollama)
│   ├── app/
│   │   ├── main.py              # Arranque de FastAPI, ciclo de vida Mongo/Kafka
│   │   ├── config/kafka.py
│   │   ├── kafka/                # Consumer de eventos y generación de prompts
│   │   └── services/             # mongo.py, embedding.py, cargaMongo.py, cargamasiva.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── WebScrapping/                # Ver sección 3 - scraping de artículos de Financial Times (proceso independiente)
│
├── docker-compose.yml           # Orquesta todos los servicios (MySQL, MongoDB, Redpanda, backend, frontend, LLM, Ollama)
├── build.gradle.kts / settings.gradle.kts   # Proyecto Gradle multi-módulo (raíz: "newspaper")
├── gradlew / gradlew.bat        # Wrapper de Gradle
└── requirements.txt             # Dependencias Python sueltas en la raíz (heredadas, ver nota en sección 2)
```

### Arquitectura y flujo de datos

- **MicroBackOffice** (puerto 8081, MySQL): backoffice donde se crean/gestionan artículos y categorías. Al crear un recurso, publica un evento en Kafka.
- **MicroContent** (puerto 8083, MongoDB): consume esos eventos, persiste el contenido "publicado" y expone la API pública que consume el frontend. También expone endpoints de preguntas/memoria conversacional (`QuestionController`, `MemoryController`) que se apoyan en `MicroLLM`.
- **MicroLLM** (puerto 8000, FastAPI): consume eventos de Kafka para generar embeddings de los artículos (`embedding.py`) y los guarda en Mongo; expone lógica de generación de prompts/RAG apoyándose en Ollama.
- **frontcontent** (puerto 4200, Angular 19): SPA que muestra portada, detalle de artículo, categorías y un chat que habla con `MicroLLM`/`MicroContent`.
- **Redpanda** (Kafka API en 9092, consola en 8080): bus de eventos entre los tres microservicios.
- **Ollama** (puerto 11434): sirve el modelo LLM local usado por `MicroLLM`.

## 2. Comandos necesarios para probar el proyecto

### Requisito previo: instalar Docker

Todo el proyecto está pensado para ejecutarse con **Docker** y **Docker Compose**. Antes de nada:

- Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Engine + Docker Compose) en Windows/Mac, o Docker Engine + el plugin `docker compose` en Linux.
- Verifica la instalación con:
  ```bash
  docker --version
  docker compose version
  ```
- Asegúrate de que Docker Desktop está iniciado (el daemon corriendo) antes de lanzar cualquier comando `docker compose ...`.

### Opción A: todo con Docker Compose (recomendado)

Con Docker y Docker Compose ya instalados, levanta MySQL, MongoDB, Redpanda (+ consola), Ollama y los 4 servicios de la aplicación:

```bash
docker compose up --build
```

Servicios expuestos:
| Servicio            | URL/Puerto                     |
|---------------------|---------------------------------|
| Frontend (Angular)  | http://localhost:4200           |
| MicroBackOffice API | http://localhost:8081           |
| MicroContent API    | http://localhost:8083           |
| MicroLLM (FastAPI)  | http://localhost:8000/health    |
| Redpanda Console    | http://localhost:8080           |
| MySQL               | localhost:3307 (root/root)      |
| MongoDB             | localhost:27018 (db `Newspaper`)|
| Ollama               | http://localhost:11434         |

Para bajar el entorno:
```bash
docker compose down
```

> Nota: la primera vez que se usa `MicroLLM`/Ollama, hay que descargar el modelo dentro del contenedor de Ollama, p. ej.:
> ```bash
> docker exec -it ollama ollama pull <nombre-del-modelo>
> ```

### Opción B: ejecutar cada módulo por separado (desarrollo local)

Se necesita tener arrancados manualmente MySQL, MongoDB y Redpanda (se pueden levantar solo esos servicios con `docker compose up mysql mongodb redpanda redpanda-console ollama`).

**MicroBackOffice** (Java 21 + Gradle):
```bash
cd MicroBackOffice
./gradlew bootRun
```

**MicroContent** (Java 21 + Gradle):
```bash
cd MicroContent
./gradlew bootRun
```

**Frontend Angular** (`MicroContent/frontcontent`, Node 20):
```bash
cd MicroContent/frontcontent
npm install
npm run start        # ng serve --host 0.0.0.0 --port 4200
```
Otros comandos útiles del frontend: `npm run build`, `npm run watch`, `npm run test`.

**MicroLLM** (Python 3.11):
```bash
cd MicroLLM
python -m venv venv
venv\Scripts\activate        # en Windows (o `source venv/bin/activate` en Linux/Mac)
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Comprobar que arrancó: `GET http://localhost:8000/health`.

Antes de correr `MicroLLM` conviene descargar el tokenizador necesario:
```bash
python descargar_tokenizador.py
```

### Build de todo el proyecto Gradle (multi-módulo) desde la raíz

```bash
./gradlew build
```

Variables de entorno relevantes (ya configuradas por defecto en `docker-compose.yml`, o con valores por defecto en `application.yml` para ejecución local):
- `SPRING_KAFKA_BOOTSTRAP_SERVERS`
- `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD` (MicroBackOffice)
- `SPRING_DATA_MONGODB_URI` (MicroContent)
- `KAFKA_BOOTSTRAP_SERVERS`, `MONGO_URI` (MicroLLM)

> El `requirements.txt` de la raíz del repositorio parece un resto de una copia/pega anterior (contiene `fastapi`, `uvicorn`, `aiokafka`, `motor`, `transformers`, `accelerate`); las dependencias reales y actualizadas del microservicio Python están en `MicroLLM/requirements.txt`.

## 3. Configuración de la base de datos

Hay dos bases de datos: **MySQL** (usada solo por `MicroBackOffice`, como almacén interno del backoffice) y **MongoDB** (usada por `MicroContent` para el contenido publicado, y por `MicroLLM` para los embeddings y la memoria del chat).

### MySQL (MicroBackOffice)

- Con Docker Compose ya viene configurada: contenedor `mysql`, base de datos `backoffice`, usuario `root`, contraseña `root`, puerto expuesto en el host `3307` (dentro de la red Docker se accede como `mysql:3306`).
- `MicroBackOffice` usa Hibernate con `ddl-auto: update` (`application.yml`), por lo que **las tablas se crean/actualizan solas** al arrancar la aplicación; no hace falta ejecutar ningún script SQL a mano.
- Para desarrollo local (sin Docker) basta con tener un MySQL corriendo y pasar las variables de entorno, o levantar solo la base con:
  ```bash
  docker compose up mysql
  ```
  y luego arrancar `MicroBackOffice` con `./gradlew bootRun` (usará por defecto `jdbc:mysql://localhost:3306/backoffice`, root/root, según los valores por defecto de `application.yml`; si usas el contenedor de Compose, recuerda que el puerto publicado en el host es `3307`, así que tendrías que sobreescribir `SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3307/backoffice`).
- Si usas un MySQL propio, solo necesitas crear la base de datos vacía (`CREATE DATABASE backoffice;`); el esquema lo genera Hibernate.

### MongoDB (MicroContent + MicroLLM)

- Con Docker Compose: contenedor `mongodb`, base de datos `Newspaper`, puerto expuesto en el host `27018` (dentro de la red Docker se accede como `mongodb:27017`). No requiere usuario/contraseña (sin autenticación).
- `MicroContent` se conecta usando `SPRING_DATA_MONGODB_URI` (ver `application.yml`); Spring Data crea la colección `article` automáticamente al guardar el primer documento. También existe `MicroContent/src/main/resources/mongodb-config.xml`, que parece un resto de una config alternativa (apunta a `localhost:27017`, sin usuario/contraseña) — no la usa Spring Boot directamente, así que puedes ignorarla salvo que algún componente la cargue explícitamente.
- `MicroLLM` usa Motor (Mongo async) en `app/services/mongo.py`, que se conecta a la colección `embeddings` leyendo la URI de la variable de entorno `MONGO_URI` (con `mongodb://localhost:27018/Newspaper` como valor por defecto si no está definida). Dentro de Docker Compose usa automáticamente `MONGO_URI=mongodb://mongodb:27017/Newspaper` (definida en `docker-compose.yml` para el servicio `micro-llm`); si ejecutas `MicroLLM` fuera de Docker (Opción B de la sección 2), el valor por defecto ya apunta al puerto publicado en el host (`localhost:27018`), así que no hace falta tocar nada.
- No hace falta crear la base ni las colecciones a mano: MongoDB las crea automáticamente en el primer `insert`.

### Resumen de puertos/credenciales (Docker Compose)

| Base de datos | Host/puerto (desde tu máquina) | Host/puerto (dentro de la red Docker) | Usuario/contraseña |
|---|---|---|---|
| MySQL | `localhost:3307` | `mysql:3306` | `root` / `root` |
| MongoDB | `localhost:27018` | `mongodb:27017` | sin autenticación |

## 4. Cómo poblar la base de datos (artículos y embeddings)

Al arrancar el proyecto desde cero, **MongoDB estará completamente vacía** (sin artículos ni embeddings). La forma de poblarla con datos de prueba es la carga masiva a partir de los artículos obtenidos con `WebScrapping` (o los ya incluidos en `WebScrapping/Articulos.zip`), usando los scripts de `MicroLLM/app/services`. Esto inserta tanto los artículos "en crudo" (colección `article`) como sus embeddings (colección `embeddings`), ambos en la base de datos `Newspaper` de MongoDB.

Se asume que el proyecto se levanta con Docker Compose (`docker compose up --build`, ver sección 2) y que los scripts se ejecutan **dentro del contenedor `micro-llm`**, para no tener que montar un entorno Python en local ni preocuparte por resolver el hostname `mongodb`/`redpanda`.

1. Descomprime `WebScrapping/Articulos.zip` (o genera artículos nuevos con el notebook, ver sección 6) en carpetas por empresa, p. ej. `C:\repositorio\WebScrapping\OpenAI\*.json`.
2. **Ajusta las rutas hardcodeadas** a tu máquina en:
   - `MicroLLM/app/services/cargaMongo.py` (constante `DIRECTORIO_RAIZ`, por defecto `C:\repositorio\WebScrapping`, y la lista `CARPETAS_OBJETIVO`)
   - `MicroLLM/app/services/cargamasiva.py` (rutas dentro de `procesar_articulos`)

   Como estos scripts se van a ejecutar **dentro** del contenedor `micro-llm` y no en tu máquina Windows, la ruta debe ser la ruta *dentro del contenedor*. Lo más sencillo es montar la carpeta `WebScrapping` como volumen del servicio `micro-llm` en `docker-compose.yml`, por ejemplo:
   ```yaml
   micro-llm:
     ...
     volumes:
       - ./WebScrapping:/data/WebScrapping
   ```
   y entonces usar `DIRECTORIO_RAIZ = "/data/WebScrapping"` (Linux, dentro del contenedor) en ambos scripts en lugar de la ruta de Windows.

3. Con los contenedores levantados (`docker compose up --build`), inserta los artículos "en crudo" en Mongo (colección `article`, BD `Newspaper`):
   ```bash
   docker compose exec micro-llm python -m app.services.cargaMongo
   ```
4. Genera los embeddings de esos mismos artículos e insértalos en Mongo (colección `embeddings`, BD `Newspaper`):
   ```bash
   docker compose exec micro-llm python -m app.services.cargamasiva
   ```
   `cargamasiva.py` ya está preparado para hacer el `insert`/`upsert` directamente en MongoDB (usa `pymongo` contra `Newspaper.embeddings`, leyendo la URI de la variable de entorno `MONGO_URI` si está definida, o `mongodb://localhost:27018/` por defecto). Dentro del contenedor `micro-llm`, `MONGO_URI` ya está definida por `docker-compose.yml` apuntando a `mongodb://mongodb:27017/Newspaper`, así que no hace falta configurar nada adicional.

Tras estos dos pasos, tanto la colección `article` como `embeddings` de la base `Newspaper` quedan pobladas, y el chat (`QuestionController` → `MicroLLM`) ya puede buscar por similitud de embeddings sobre esos artículos.

Tanto `cargaMongo.py` como `cargamasiva.py` leen la URI de conexión de la variable de entorno `MONGO_URI` (con `mongodb://localhost:27018/` como valor por defecto si no está definida). Al ejecutarlos con `docker compose exec micro-llm ...`, ya toman automáticamente el `MONGO_URI=mongodb://mongodb:27017/Newspaper` que define `docker-compose.yml` para ese servicio.

## 5. Carpeta WebScrapping

Esta carpeta **no forma parte del sistema desplegado** (no aparece en `docker-compose.yml` ni se ejecuta como microservicio): es una herramienta auxiliar y manual para **generar datos de prueba** (artículos) con los que alimentar `MicroBackOffice`/`MicroContent`.

Contenido:
- **`WebScrapping.ipynb`**: notebook de Jupyter con el scraper, escrito con Selenium (controla Chrome) para extraer artículos del Financial Times. El flujo tiene dos fases:
  1. **Búsqueda**: recorre las páginas de resultados de `ft.com/search?q=<empresa>` y guarda en un `.txt` los títulos y URLs de los artículos encontrados (`scrape_ft`).
  2. **Extracción**: visita cada URL del `.txt` generado, extrae título, resumen, cuerpo, imágenes y fecha de publicación de cada artículo, y genera **un JSON por artículo** en una carpeta con el nombre de la empresa (`scrape_articles` / `extract_article_data`). Los artículos generados usan autores, categorías y secciones simulados (definidos en el propio notebook) para poder importarlos directamente al modelo de datos del periódico.
  - Incluye utilidades para evitar bloqueos básicos del sitio: generación aleatoria de *User-Agents* (`generate_user_agents`), simulación de interacción humana con el ratón/scroll (`simulate_human_behavior`) y aceptación automática del aviso de cookies (`accept_cookies`).
- **`Articulos.zip`**: artículos ya generados por el notebook en ejecuciones previas (JSONs listos para importar).
- **`webscrapping/`**: entorno virtual de Python (`venv`) con las dependencias del scraper (Selenium, etc.) ya instaladas — **no debería estar versionado** en git ni forma parte del código fuente; es material generado localmente al crear el entorno (equivalente a un `node_modules`).
- **`.idea/`**: configuración del IDE (PyCharm), sin relevancia funcional.

**Cómo usarlo** (no forma parte del arranque normal del proyecto):
```bash
cd WebScrapping
python -m venv webscrapping
webscrapping\Scripts\activate      # Windows
pip install selenium
jupyter notebook WebScrapping.ipynb
```
Requiere tener Chrome y el *chromedriver* correspondiente instalados, y (según el notebook) una extensión de Chrome cargada desde una ruta local (`EXTENSION_PATH`) para evitar bloqueos anti-bot. El scraper guarda las rutas de salida apuntando a `C:\repositorio\WebScrapping`, por lo que conviene revisar y ajustar esas rutas antes de ejecutarlo en otra máquina.

Los JSONs resultantes se pueden usar para poblar manualmente `MicroBackOffice`/`MicroContent` vía sus APIs REST y así probar el frontend con datos realistas sin depender del scraping en cada prueba.

## 6. Endpoints de la API

Todos los ejemplos asumen los servicios levantados con `docker compose up --build` (sección 2) y usan `curl`; sustituye por Postman/Insomnia si lo prefieres.

### MicroBackOffice (`http://localhost:8081`) — administración de artículos y categorías

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/v1/admin/articles/` | Crea un artículo (asíncrono vía Kafka). Devuelve `202 Accepted` con cabecera `Location`. |
| `GET` | `/api/v1/admin/articles/status/{id}` | Consulta el estado (`PENDING`/`OK`/...) de la creación de un artículo. |
| `POST` | `/api/v1/admin/articles/category` | Crea una categoría (asíncrono vía Kafka). Devuelve `202 Accepted` con cabecera `Location`. |
| `GET` | `/api/v1/admin/articles/category/status/{id}` | Consulta el estado de creación de una categoría. |

Crear un artículo:
```bash
curl -X POST http://localhost:8081/api/v1/admin/articles/ \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Título de prueba",
        "slug": "titulo-de-prueba",
        "author": "Redacción",
        "state": "PUBLISHED",
        "body": "Cuerpo del artículo...",
        "summary": "Resumen breve",
        "category": ["Tecnología"],
        "multimedias": []
      }'
```
`state` debe ser uno de los valores del enum `State`: `DRAFT`, `REWIEW`, `PUBLISHED`, `ARCHIVED` (ver `MicroBackOffice/src/main/java/project/newspaper/domain/State.java`).

Consultar el estado de creación (usando el `id` devuelto en la cabecera `Location`):
```bash
curl http://localhost:8081/api/v1/admin/articles/status/<id>
```

Crear una categoría:
```bash
curl -X POST http://localhost:8081/api/v1/admin/articles/category \
  -H "Content-Type: application/json" \
  -d '{"name": "Tecnología"}'
```

Consultar el estado de creación de una categoría:
```bash
curl http://localhost:8081/api/v1/admin/articles/category/status/<id>
```

> Nota: crear artículos/categorías por esta vía requiere tener también `mongodb`, `redpanda` y `microcontent` levantados, ya que la escritura real en Mongo la hace `MicroContent` al consumir el evento de Kafka publicado por `MicroBackOffice`.

### MicroContent (`http://localhost:8083`) — contenido público, memoria y preguntas

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/articulos` | Lista todos los artículos. |
| `GET` | `/articulos/ultimos` | Últimos 30 artículos, ordenados por fecha de creación descendente. |
| `GET` | `/articulos/categoria/{categoria}` | Hasta 30 artículos de una categoría (case-insensitive), más recientes primero. |
| `GET` | `/articulos/{id}` | Detalle de un artículo por id. `404` si no existe. |
| `GET` | `/categorias` | Lista los nombres de todas las categorías. |
| `POST` | `/api/v1/questions` | Envía una pregunta al chat (asíncrono vía Kafka; la responde `MicroLLM` usando RAG sobre los embeddings). |
| `GET` | `/api/v1/memory` | Devuelve el historial de conversación guardado (`{"history": [...]}`). |

Ejemplos:
```bash
curl http://localhost:8083/articulos
curl http://localhost:8083/articulos/ultimos
curl http://localhost:8083/articulos/categoria/Tecnolog%C3%ADa
curl http://localhost:8083/articulos/<id>
curl http://localhost:8083/categorias

curl -X POST http://localhost:8083/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué ha anunciado OpenAI recientemente?"}'

curl http://localhost:8083/api/v1/memory
```
`POST /api/v1/questions` solo encola la pregunta (responde `202 Accepted`); la respuesta generada por el LLM y el resumen de artículos relevantes se procesan de forma asíncrona en `MicroLLM` (ver `app/kafka/consumer.py`) y se guardan en la colección `memory` de Mongo, consultable después con `GET /api/v1/memory`. Para que esto funcione hacen falta `mongodb`, `redpanda`, `micro-llm` y `ollama` levantados y con la base poblada con embeddings (sección 4).

### MicroLLM (`http://localhost:8000`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Comprobación de estado del servicio (`{"status": "OK"}`). |

```bash
curl http://localhost:8000/health
```
`MicroLLM` no expone más endpoints HTTP: toda su lógica de negocio (calcular embeddings al crear un artículo, responder preguntas del chat) se dispara escuchando los topics de Kafka `article.created.embedding` y `user.question.asked`, no vía REST.

### Frontend (`http://localhost:4200`)

SPA en Angular; no es una API, se navega desde el navegador. Consume internamente los endpoints de `MicroContent` (portada, detalle de artículo, categorías y el chat).

### Redpanda Console (`http://localhost:8080`)

UI web para inspeccionar los topics de Kafka (`backoffice.article.created`, `content.article.index`, `content.article.created.confirmation`, `article.created.embedding`, `user.question.asked`, `backoffice.category.created`, etc.), sus mensajes y consumer groups — útil para depurar el flujo de eventos entre microservicios.
