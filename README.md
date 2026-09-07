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

### Opción A: todo con Docker Compose (recomendado)

Requiere Docker y Docker Compose instalados. Levanta MySQL, MongoDB, Redpanda (+ consola), Ollama y los 4 servicios de la aplicación:

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

## 3. Carpeta WebScrapping

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
