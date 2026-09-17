# 🚀 Despliegue y automatización en GCP

La arquitectura final será:

```text
                  ┌──────────────────┐
                  │  Cloud Scheduler │
                  │  Ejecución diaria│
                  └────────┬─────────┘
                           │
                           ▼
┌─────────────────┐   ┌─────────────────┐
│ Cloud Storage   │──▶│    Cloud Run    │
│ datos CSV       │   │       ETL       │
└─────────────────┘   └────────┬────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │    Cloud SQL    │
                       │      MySQL      │
                       │     ventas      │
                       └─────────────────┘
```

---

## 1. Comprobar que `etl.py` no tiene errores

En Cloud Shell:

```bash
cd ~/prueba-ladorian-etl
```

Ejecuta:

```bash
python3 -m py_compile etl.py
```

### Si no aparece nada

✅ El archivo tiene sintaxis correcta.

---

# 2. Comprobar el Dockerfile

Ejecuta:

```bash
cat Dockerfile
```

Debe contener:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY etl.py .

RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    google-cloud-storage \
    mysql-connector-python \
    flask

CMD ["python", "etl.py"]
```

---

# 3. Reconstruir la imagen

Ejecuta:

```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/$(gcloud config get-value project)/etl-repo/prueba-etl:latest
```

Espera a que termine correctamente.

---

# 4. Desplegar nuevamente Cloud Run

```bash
gcloud run deploy prueba-etl \
  --image europe-west1-docker.pkg.dev/$(gcloud config get-value project)/etl-repo/prueba-etl:latest \
  --region europe-west1
```

Al finalizar debería aparecer:

```text
Service [prueba-etl] revision [...] is ready
```

---

# 5. Comprobar que Cloud Run está READY

```bash
gcloud run services describe prueba-etl \
  --region europe-west1 \
  --format="value(status.conditions)"
```

Queremos encontrar:

```text
status: True
```

y que la revisión esté lista.

---

# 6. Obtener la URL

```bash
gcloud run services describe prueba-etl \
  --region europe-west1 \
  --format="value(status.url)"
```

Obtendrás algo parecido a:

```text
https://prueba-etl-xxxxx-ew.a.run.app
```

---

# 7. Probar Cloud Run

Como el servicio está privado, podemos probarlo desde Cloud Shell:

```bash
gcloud run services proxy prueba-etl \
  --region europe-west1
```

En otra pestaña de Cloud Shell:

```bash
curl http://localhost:8080
```

Deberíamos obtener:

```text
ETL ejecutado correctamente
```

---

# ⚠️ 8. Hacer que `/` ejecute realmente el ETL

Aquí tenemos que hacer un pequeño cambio.

Ahora mismo tenemos:

```python
@app.route("/", methods=["GET"])
def ejecutar_etl():
    return "ETL ejecutado correctamente"
```

Esto **solo responde al navegador**, no ejecuta el procesamiento.

La idea final será:

```text
GET /
   ↓
ejecutar ETL
   ↓
leer CSV
   ↓
limpiar datos
   ↓
guardar CSV procesado
   ↓
insertar en Cloud SQL
   ↓
responder OK
```

Para esto tendremos que reorganizar `etl.py` ligeramente, metiendo el procesamiento dentro de una función.

---

# 9. Reconstruir después del cambio

Cada vez que modifiquemos `etl.py`:

```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/$(gcloud config get-value project)/etl-repo/prueba-etl:latest
```

Y:

```bash
gcloud run deploy prueba-etl \
  --image europe-west1-docker.pkg.dev/$(gcloud config get-value project)/etl-repo/prueba-etl:latest \
  --region europe-west1
```

---

# 10. Configurar Cloud Scheduler

Cuando Cloud Run funcione correctamente, habilitamos Scheduler:

```bash
gcloud services enable cloudscheduler.googleapis.com
```

Creamos un job, por ejemplo, diario a las 02:00:

```bash
gcloud scheduler jobs create http etl-diario \
  --location=europe-west1 \
  --schedule="0 2 * * *" \
  --uri="URL_DE_CLOUD_RUN" \
  --http-method=GET
```

Sustituiremos:

```text
URL_DE_CLOUD_RUN
```

por la URL real de nuestro servicio.

---

# 11. Arquitectura automatizada final

El resultado que puedes presentar en la prueba será:

```text
                 CLOUD SCHEDULER
                       │
                  cada día
                       │
                       ▼
                  CLOUD RUN
                      ETL
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       CLOUD STORAGE         CLOUD SQL
          CSV                  MySQL
             │                   │
             └───────┬───────────┘
                     ▼
              Datos procesados
```

### Servicios GCP utilizados

| Servicio              | Función                               |
| --------------------- | ------------------------------------- |
| **Cloud Storage**     | Almacenar CSV de entrada y resultados |
| **Cloud Run**         | Ejecutar el ETL                       |
| **Artifact Registry** | Almacenar la imagen Docker            |
| **Cloud SQL**         | Base de datos MySQL                   |
| **Cloud Scheduler**   | Ejecutar el ETL automáticamente       |

---

## 📌 Orden exacto para continuar

No hagas todos de golpe. Vamos en este orden:

**1.**

```bash
python3 -m py_compile etl.py
```

**2.** Si está OK → reconstruir Docker.

**3.** Desplegar Cloud Run.

**4.** Comprobar `READY`.

**5.** Obtener URL.

**6.** Probar.

**7.** Hacer que `/` ejecute realmente el ETL.

**8.** Finalmente configurar Scheduler.

Ese es el último tramo para dejar el proyecto **desplegado y automatizado en GCP**.
