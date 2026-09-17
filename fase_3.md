
La Parte 3 de la prueba te pide dos cosas: diseñar un ETL en GCP que lea un archivo, lo procese y lo cargue en una base de datos, y después diseñar una API que consulte esos datos desde Cloud. 

## 1. Primero: ¿qué es GCP?

**GCP = Google Cloud Platform.**

Es la plataforma de servicios en la nube de Google.

La idea sencilla es:

> En lugar de tener tú un ordenador/servidor encendido con MySQL, Python, almacenamiento, etc., alquilas esos recursos a Google y los utilizas por Internet.

Por ejemplo, ahora mismo tú podrías tener:

```text
TU MAC
│
├── CSV
├── Python
├── Jupyter
├── MySQL
└── API
```

Y en la nube tendrías:

```text
GOOGLE CLOUD
│
├── Cloud Storage → guarda CSV
├── Cloud Run → ejecuta Python/API
├── Cloud SQL → MySQL
└── Cloud Scheduler → automatiza procesos
```

La gracia de GCP es que **no tienes que comprar ni mantener físicamente los servidores**.

---

# 2. Vamos a entender el ejercicio

La empresa te dice:

> "Tengo un CSV con ventas. Quiero que automáticamente llegue a una base de datos y después quiero poder consultar esas ventas mediante una API."

Eso es todo.

Tu trabajo consiste en construir esto:

```text
CSV
 ↓
ALMACENAMIENTO
 ↓
PROCESAMIENTO
 ↓
BASE DE DATOS
 ↓
API
 ↓
USUARIO / APLICACIÓN
```

Ahora vamos a construir cada pieza.

---

# PARTE A — ¿Dónde guardo el CSV?

## Cloud Storage

**Cloud Storage** es como un disco duro en Internet.

En tu ordenador tienes:

```text
/Users/Yanelis/datos_prueba_v2.csv
```

En GCP tendrías algo parecido a:

```text
Cloud Storage
└── bucket
    └── datos_prueba_v2.csv
```

Un **bucket** es básicamente un contenedor donde guardas archivos.

Por ejemplo:

```text
Bucket: prueba-ladorian

    /raw
        datos_prueba_v2.csv

    /processed
        ventas_limpias.csv
```

### ¿Por qué lo necesitamos?

Porque no queremos que nuestro proceso dependa de:

> "El CSV está en mi Mac."

Queremos:

> "El CSV está disponible en la nube."

---

# PARTE B — ¿Quién procesa el CSV?

Aquí entra **Cloud Run** o **Dataflow**.

Y aquí quiero que entiendas una distinción importante.

## Cloud Run

Cloud Run permite ejecutar una aplicación o código **sin que tú tengas que administrar un servidor**.

Por ejemplo, puedes crear un programa Python:

```python
import pandas as pd

df = pd.read_csv("datos.csv")

# limpiar
# transformar
# etc.
```

Lo empaquetas en un contenedor Docker.

Google ejecuta ese contenedor cuando lo necesitas.

Conceptualmente:

```text
Cloud Storage
      │
      │ CSV
      ▼
   Cloud Run
      │
      │ Python + Pandas
      ▼
datos procesados
```

---

# ¿Y Dataflow?

Dataflow está pensado específicamente para **procesamiento de datos**, especialmente pipelines ETL/ELT.

Por ejemplo:

```text
CSV
 ↓
leer
 ↓
limpiar
 ↓
transformar
 ↓
agrupar
 ↓
cargar
```

Y puede trabajar con cantidades de datos mucho mayores.


---

# PARTE C — ¿Dónde guardo los datos?

## Cloud SQL

Esto conecta directamente con lo que estás haciendo ahora con MySQL.

**Cloud SQL es un servicio de Google que te proporciona una base de datos gestionada.**

Puedes tener:

* MySQL
* PostgreSQL
* SQL Server

En tu caso:

```text
Cloud SQL
   │
   └── MySQL
        │
        └── prueba_ladorian
             │
             └── ventas
```

Es decir:

### En tu ordenador

```text
MySQL
└── prueba_ladorian
    └── ventas
```

### En GCP

```text
Cloud SQL
└── MySQL
    └── prueba_ladorian
        └── ventas
```

La diferencia es que **Google administra el servidor por ti**.

---

# PARTE D — ¿Cómo se ejecuta automáticamente?

Aquí aparece **Cloud Scheduler**.

Imagina que la empresa recibe un CSV todos los días:

```text
lunes → ventas.csv
martes → ventas.csv
miércoles → ventas.csv
...
```

No queremos que una persona tenga que decir:

> "Voy a abrir Jupyter y ejecutar el código."

Queremos:

```text
02:00
  ↓
Cloud Scheduler
  ↓
ejecuta proceso ETL
  ↓
lee CSV
  ↓
limpia
  ↓
Cloud SQL
```


---

# PARTE E — ¿Cómo sé si ha fallado?

Aquí tenemos **Cloud Logging** y **Cloud Monitoring**.

Por ejemplo:

```text
ETL empieza
    ↓
lee CSV
    ↓
ERROR: columna total no encontrada
    ↓
Cloud Logging registra el error
```

Y tú puedes revisar qué ha pasado.

Esto es importante porque en producción las cosas fallan.

---

# Entonces nuestra primera arquitectura sería

```text
                   GCP
────────────────────────────────────

             Cloud Storage
                  │
                  │ CSV
                  ▼
             Cloud Run
                  │
             Python ETL
                  │
       ┌──────────┴──────────┐
       │                     │
   limpiar                 validar
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
              Cloud SQL
                MySQL
                  │
                  ▼
               ventas


       Cloud Scheduler
              │
              └──────► ejecuta Cloud Run

       Cloud Logging
              ▲
              │
         monitoriza ETL
```

---

# Ahora viene la segunda parte: LA API

La empresa dice:

> "Los datos están en Cloud SQL. Ahora quiero que otra aplicación pueda consultar las ventas."

Aquí aparece una API.

---

# ¿Qué es una API?

Una API es una forma de que **un programa pueda pedirle datos a otro programa**.

Por ejemplo, tú tienes:

```text
Base de datos
```

con 100.000 ventas.

Una aplicación no debería conectarse directamente a MySQL y hacer:

```sql
SELECT * FROM ventas;
```

Queremos poner una capa intermedia:

```text
Aplicación
    ↓
   API
    ↓
Cloud SQL
```

---

# ¿Qué tecnología utilizaríamos?

Yo usaría:

**Python + FastAPI**

Ya que tú conoces Python y la API es muy sencilla de construir con FastAPI.

Podríamos tener:

```text
GET /ventas
```

que devuelve ventas.

O:

```text
GET /ventas/dia
```

que devuelve:

```json
[
    {
        "date": "2022-01-01",
        "total": 12543.50
    }
]
```

---

# ¿Dónde ejecutamos la API?

Otra vez:

## Cloud Run

Puedes meter nuestra API FastAPI dentro de un contenedor:

```text
FastAPI
   ↓
Docker
   ↓
Cloud Run
```

Y quedaría:

```text
                    INTERNET
                       │
                       ▼
                  Cloud Run
                       │
                  FastAPI
                       │
                       ▼
                   Cloud SQL
                     MySQL
                       │
                    ventas
```

---

# ¿Y qué pasa cuando alguien hace una petición?

Por ejemplo:

```http
GET /ventas/daily
```

El recorrido sería:

```text
Usuario
   │
   │ GET /ventas/daily
   ▼
Cloud Run
   │
   ▼
FastAPI
   │
   │ SQL
   ▼
Cloud SQL
   │
   │ resultado
   ▼
FastAPI
   │
   │ JSON
   ▼
Usuario
```

Eso es una API.

---

