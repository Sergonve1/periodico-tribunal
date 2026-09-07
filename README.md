# Periodico — Plataforma de noticias con microservicios y RAG

Proyecto de periódico digital compuesto por tres microservicios (dos en Spring Boot/Java y uno en Python/FastAPI), un frontend en Angular, y una infraestructura de mensajería (Kafka/Redpanda) que los conecta de forma asíncrona. Incluye un asistente conversacional (chat) que responde preguntas sobre las noticias usando embeddings semánticos y un LLM local servido por Ollama (RAG).

## Índice

- [Arquitectura](#arquitectura)
- [Estructura de carpetas](#estructura-de-carpetas)
- [Puertos](#puertos)
- [Requisitos previos](#requisitos-previos)
- [Puesta en marcha rápida (Docker Compose)](#puesta-en-marcha-rápida-docker-compose)
- [Puesta en marcha en modo desarrollo (sin Docker)](#puesta-en-marcha-en-modo-desarrollo-sin-docker)
- [Variables de entorno](#variables-de-entorno)
- [Topics de Kafka](#topics-de-kafka)
- [Endpoints principales](#endpoints-principales)
- [Aviso de seguridad](#aviso-de-seguridad)

## Arquitectura

```
                         ┌──────────────────┐
                         │  frontcontent     │  Angular (SPA pública)
                         │  puerto 4200      │
                         └────────┬──────────┘
                                  │ HTTP
                                  ▼
   ┌───────────────┐     ┌──────────────────┐      ┌──────────────────┐
   │ MicroBackOffice│     │   MicroContent    │      │     MicroLLM      │
   │  (admin, ABM)  │     │ (lectura pública, │      │  (RAG / embeddings │
   │  puerto 8081   │     │  chat, memoria)   │      │   / Ollama)        │
   │  MySQL         │     │  puerto 8083      │      │  puerto 8000       │
   └───────┬────────┘     │  MongoDB          │      │  MongoDB           │
           │              └────────┬──────────┘      └─────────┬──────────┘
           │                       │                            │
           └──────────► Redpanda / Kafka (9092) ◄────────────────┘
                                  │
                                  ▼
                             Ollama (11434) — LLM local (llama3:8b)
```

Flujo típico de creación de un artículo:
1. Un admin llama a `POST /api/v1/admin/articles/` en **MicroBackOffice**, que guarda el estado en MySQL y publica el evento `backoffice.article.created` en Kafka.
2. **MicroContent** consume ese evento, guarda el artículo en MongoDB, y publica `content.article.created.confirmation` (vuelve a BackOffice) y `article.created.embedding` (para MicroLLM).
3. **MicroLLM** consume `article.created.embedding`, calcula el embedding del texto con `sentence-transformers` y lo guarda en MongoDB.
4. Cuando un usuario pregunta algo desde el chat (`POST /api/v1/questions` en MicroContent), se publica `user.question.asked`; MicroLLM busca los artículos más similares por embedding, genera un resumen y una respuesta con Ollama (modelo `llama3:8b`), y guarda el historial de la conversación en MongoDB (expuesto luego vía `GET /api/v1/memory` en MicroContent).

## Estructura de carpetas

| Carpeta | Descripción |
|---|---|
| [`MicroBackOffice/`](MicroBackOffice) | Microservicio Spring Boot (Java 21) de administración/back-office. Expone API REST para crear artículos y categorías, persiste en **MySQL** y publica eventos en Kafka. Escucha las confirmaciones de creación que le devuelve `MicroContent` para actualizar el estado de la operación. |
| [`MicroContent/`](MicroContent) | Microservicio Spring Boot (Java 21) de contenido público. Persiste artículos/categorías en **MongoDB**, expone la API que consume el frontend (listado de artículos, categorías, detalle, preguntas del chat, memoria de conversación) y republica eventos hacia `MicroLLM`. |
| [`MicroContent/frontcontent/`](MicroContent/frontcontent) | SPA en **Angular 19** — la web pública del periódico (portada, detalle de artículo, categorías, componente de chat). Consume la API de `MicroContent` (hardcodeada a `http://localhost:8083`). |
| [`MicroLLM/`](MicroLLM) | Microservicio en **Python/FastAPI**. Consume eventos de Kafka, genera embeddings de los artículos (`sentence-transformers`), resuelve preguntas del chat mediante búsqueda semántica + resumen/generación con **Ollama** (RAG), y guarda embeddings/memoria en MongoDB. |
| `gradle/`, `gradlew*`, `settings.gradle.kts` | Build multi-módulo Gradle en la raíz que agrupa `MicroBackOffice` y `MicroContent` (proyecto raíz `newspaper`). `MicroLLM` no forma parte del build Gradle (es Python independiente). |
| [`docker-compose.yml`](docker-compose.yml) | Orquesta **todos** los servicios e infraestructura (MySQL, MongoDB, Redpanda, Redpanda Console, los 3 microservicios, el frontend y Ollama). Es la forma recomendada de levantar el proyecto completo. |
| `.venv/` | Entorno virtual de Python local (no debería estar versionado; ver aviso más abajo). No es necesario para ejecutar el proyecto vía Docker. |

## Puertos

| Servicio | Puerto host | Descripción |
|---|---|---|
| `frontcontent` (Angular) | **4200** | Web pública |
| `backoffice` (MicroBackOffice) | **8081** | API admin (Spring Boot) |
| `microcontent` (MicroContent) | **8083** | API pública / chat (Spring Boot) |
| `micro-llm` (MicroLLM) | **8000** | API FastAPI (health-check; la lógica RAG corre por Kafka) |
| `ollama` | **11434** | Servidor LLM local (modelo `llama3:8b`) |
| `mysql` | **3307** → 3306 interno | Base de datos de `MicroBackOffice` |
| `mongodb` | **27018** → 27017 interno | Base de datos `Newspaper` (`MicroContent` y `MicroLLM`) |
| `redpanda` (Kafka) | **9092** (broker), **9644** (admin) | Bus de eventos entre microservicios |
| `redpanda-console` | **8080** | UI web para inspeccionar topics/mensajes de Kafka |

## Requisitos previos

- **Docker** y **Docker Compose** (forma recomendada, no requiere instalar nada más).
- Alternativa para desarrollo local sin Docker:
  - **JDK 21** (para `MicroBackOffice` y `MicroContent`, usan Gradle wrapper incluido).
  - **Node.js 20** (para `frontcontent`, Angular CLI 19).
  - **Python 3.11** (para `MicroLLM`).
  - **Ollama** instalado localmente con el modelo `llama3:8b` descargado (`ollama pull llama3:8b`).
  - Instancias locales de **MySQL 8** y **MongoDB 6**, y un broker Kafka (p. ej. el propio `redpanda` vía Docker).

## Puesta en marcha rápida (Docker Compose)

Desde la raíz del repositorio:

```bash
docker compose up --build
```

Esto levanta, en orden de dependencias: `mysql`, `mongodb`, `redpanda`, `redpanda-console`, `backoffice`, `microcontent`, `frontcontent`, `micro-llm` y `ollama`.

Tras el arranque:

1. **Descarga el modelo en Ollama** (la primera vez, el contenedor `ollama` arranca vacío):
   ```bash
   docker exec -it ollama ollama pull llama3:8b
   ```
2. Abre la web en [http://localhost:4200](http://localhost:4200).
3. (Opcional) Inspecciona los topics de Kafka en [http://localhost:8080](http://localhost:8080) (Redpanda Console).
4. Crea contenido usando la API de `MicroBackOffice` (no hay UI de administración, ver [Endpoints principales](#endpoints-principales)):
   ```bash
   curl -X POST http://localhost:8081/api/v1/admin/articles/category -H "Content-Type: application/json" -d "{\"name\":\"Tecnologia\"}"
   ```

Para bajar el entorno: `docker compose down` (añade `-v` si además quieres borrar los volúmenes de datos, incluido el modelo de Ollama descargado).

## Puesta en marcha en modo desarrollo (sin Docker)

Útil si vas a modificar el código de un microservicio concreto y prefieres ejecutarlo fuera de Docker mientras el resto sigue en contenedores.

### 1. Infraestructura base (siempre vía Docker)

Levanta solo la infraestructura y deja los microservicios que no vas a tocar:

```bash
docker compose up mysql mongodb redpanda redpanda-console ollama
```

### 2. MicroBackOffice (Java/Spring Boot)

```bash
cd MicroBackOffice
./gradlew bootRun
```
Requiere `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD` y `SPRING_KAFKA_BOOTSTRAP_SERVERS` en el entorno (o usa los valores por defecto de [`application.yml`](MicroBackOffice/src/main/resources/application.yml), que apuntan a `localhost:3306` y necesitan que expongas Kafka en `localhost:9092`, no `redpanda:9092`). Arranca en el puerto **8081**.

### 3. MicroContent (Java/Spring Boot)

```bash
cd MicroContent
./gradlew bootRun
```
Requiere `SPRING_DATA_MONGODB_URI` y `SPRING_KAFKA_BOOTSTRAP_SERVERS` (no tienen valor por defecto en [`application.yml`](MicroContent/src/main/resources/application.yml), hay que exportarlos, p. ej. `mongodb://localhost:27018/Newspaper` y `localhost:9092`). Arranca en el puerto **8083**.

### 4. frontcontent (Angular)

```bash
cd MicroContent/frontcontent
npm install
npm start
```
Arranca en el puerto **4200**. La URL de la API (`http://localhost:8083`) está hardcodeada en los componentes (`portada.component.ts`, `articulo-detalle.component.ts`, `chat-component.component.ts`, `categorias.service.ts`), no hace falta configurar nada adicional si `MicroContent` corre en el 8083.

### 5. MicroLLM (Python/FastAPI)

```bash
cd MicroLLM
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Variables de entorno relevantes: `KAFKA_BOOTSTRAP_SERVERS` (por defecto `redpanda:9092`, cámbialo a `localhost:9092` si corres fuera de Docker). La conexión a MongoDB está hardcodeada en [`app/services/mongo.py`](MicroLLM/app/services/mongo.py) a `mongodb://mongodb:27017/Newspaper` — para ejecutarlo fuera de Docker tendrás que editar ese valor (p. ej. a `mongodb://localhost:27018/Newspaper`).

Además necesitas Ollama corriendo (local o en Docker) en `http://host.docker.internal:11434` (o cambiar la URL hardcodeada en [`app/kafka/consumer.py`](MicroLLM/app/kafka/consumer.py) si ejecutas todo en local sin Docker) con el modelo `llama3:8b` descargado.

## Variables de entorno

Configuradas en [`docker-compose.yml`](docker-compose.yml) para el modo Docker; para ejecución local hay que fijarlas a mano en el entorno de cada proceso.

| Servicio | Variable | Valor en Docker |
|---|---|---|
| backoffice | `SPRING_KAFKA_BOOTSTRAP_SERVERS` | `redpanda:9092` |
| backoffice | `SPRING_DATASOURCE_URL` | `jdbc:mysql://mysql:3306/backoffice` |
| backoffice | `SPRING_DATASOURCE_USERNAME` / `_PASSWORD` | `root` / `root` |
| microcontent | `SPRING_KAFKA_BOOTSTRAP_SERVERS` | `redpanda:9092` |
| microcontent | `SPRING_DATA_MONGODB_URI` | `mongodb://mongodb:27017/Newspaper` |
| micro-llm | `KAFKA_BOOTSTRAP_SERVERS` | `redpanda:9092` |
| micro-llm | `MONGO_URI` | `mongodb://mongodb:27017/Newspaper` (definida en compose pero **no leída** por el código actual, que usa una URI hardcodeada) |

## Topics de Kafka

| Topic | Productor | Consumidor | Propósito |
|---|---|---|---|
| `backoffice.category.created` | MicroBackOffice | MicroContent | Nueva categoría creada |
| `backoffice.article.created` | MicroBackOffice | MicroContent | Nuevo artículo creado |
| `content.category.created.confirmation` | MicroContent | MicroBackOffice | Confirma que la categoría se guardó |
| `content.article.created.confirmation` | MicroContent | MicroBackOffice | Confirma que el artículo se guardó |
| `content.article.index` | MicroContent | *(sin consumidor implementado actualmente)* | Indexación del artículo |
| `article.created.embedding` | MicroContent | MicroLLM | Dispara el cálculo de embedding del artículo |
| `user.question.asked` | MicroContent | MicroLLM | Pregunta del usuario para el chat RAG |

## Endpoints principales

**MicroBackOffice** (`http://localhost:8081`)
- `POST /api/v1/admin/articles/` — crea un artículo (asíncrono vía Kafka).
- `GET /api/v1/admin/articles/status/{id}` — estado de creación del artículo.
- `POST /api/v1/admin/articles/category` — crea una categoría (asíncrono vía Kafka).
- `GET /api/v1/admin/articles/category/status/{id}` — estado de creación de la categoría.

**MicroContent** (`http://localhost:8083`)
- `GET /articulos` — todos los artículos.
- `GET /articulos/ultimos` — últimos 30 artículos.
- `GET /articulos/categoria/{categoria}` — artículos por categoría (máx. 30).
- `GET /articulos/{id}` — detalle de artículo.
- `GET /categorias` — nombres de todas las categorías.
- `POST /api/v1/questions` — envía una pregunta al chat (asíncrono, la respuesta se genera vía Kafka/MicroLLM).
- `GET /api/v1/memory` — historial de la conversación del chat.

**MicroLLM** (`http://localhost:8000`)
- `GET /health` — health check. Toda la lógica de negocio (embeddings, RAG) se ejecuta de forma asíncrona por Kafka, no por HTTP.

## Aviso de seguridad

[`MicroLLM/descargar_tokenizador.py`](MicroLLM/descargar_tokenizador.py) contiene un token personal de Hugging Face hardcodeado y commiteado en el historial de git. Se recomienda **revocarlo** en [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) y sustituirlo por una variable de entorno (`os.environ["HF_TOKEN"]`) antes de continuar usando o compartiendo este repositorio.
