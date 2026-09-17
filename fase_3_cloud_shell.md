
# Guía de trabajo en Google Cloud Shell

## 1. Entrar en Google Cloud

Accedemos a:

[Google Cloud Console](https://console.cloud.google.com/?utm_source=chatgpt.com)

Iniciamos sesión con nuestra cuenta de Google.

Comprobamos que el proyecto seleccionado es:

```text
prueba-ladorian
```

---

# 2. Abrir Cloud Shell

En la parte superior derecha de Google Cloud Console pulsamos el icono:

```text
>_
```

Se abre una terminal en la parte inferior de la pantalla.

Cloud Shell proporciona un entorno Linux desde el que podemos ejecutar comandos y utilizar las herramientas de Google Cloud.

---

# 3. Comprobar Python

En Cloud Shell ejecutamos:

```bash
python3 --version
```

Comprobamos que Python está disponible.

---

# 4. Comprobar pip

Ejecutamos:

```bash
pip3 --version
```

En nuestro caso obtuvimos:

```text
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

---

# 5. Comprobar acceso a Cloud Storage

Ejecutamos:

```bash
gcloud storage ls
```

Obtuvimos:

```text
gs://bucket-data-landorian/
```

Esto confirma que Cloud Shell tiene acceso al bucket de nuestro proyecto.

---

# 6. Comprobar el archivo del bucket

Ejecutamos:

```bash
gcloud storage ls gs://bucket-data-landorian/
```

El resultado muestra:

```text
gs://bucket-data-landorian/datos_prueba_v2.csv
```

---

# 7. Comprobar el tamaño del archivo

Ejecutamos:

```bash
gcloud storage du gs://bucket-data-landorian/datos_prueba_v2.csv
```

Esto permite comprobar el tamaño del archivo almacenado.

---

# 8. Comprobar el contenido del CSV

Para visualizar las primeras líneas:

```bash
gcloud storage cat gs://bucket-data-landorian/datos_prueba_v2.csv | head
```

Esto permite verificar que el archivo puede leerse correctamente desde Cloud Storage.

---

# 9. Crear la carpeta del proyecto ETL

Creamos una carpeta para nuestro código:

```bash
mkdir prueba-ladorian-etl
```

Entramos en ella:

```bash
cd prueba-ladorian-etl
```

---

# 10. Crear un entorno virtual de Python

Creamos el entorno virtual:

```bash
python3 -m venv venv
```

Lo activamos:

```bash
source venv/bin/activate
```

La terminal debe mostrar:

```text
(venv)
```

al principio de la línea.

Por ejemplo:

```text
(venv) yaneliserranotaylor@cloudshell:~/prueba-ladorian-etl$
```

---

# 11. Instalar las librerías necesarias

Ejecutamos:

```bash
pip install pandas numpy matplotlib google-cloud-storage
```

Las principales librerías utilizadas son:

* `pandas`
* `numpy`
* `matplotlib`
* `google-cloud-storage`

---

# 12. Comprobar Pandas

Ejecutamos:

```bash
python -c "import pandas as pd; print(pd.__version__)"
```

Si aparece la versión de Pandas, la instalación es correcta.

---

# 13. Crear el archivo `etl.py`

Creamos el archivo:

```bash
touch etl.py
```

Comprobamos que existe:

```bash
ls -l etl.py
```

---

# 14. Editar `etl.py`

Por ello utilizamos el editor de terminal:

```bash
nano etl.py
```

---

# 15. Editar el archivo con Nano

Dentro de `nano` podemos pegar nuestro código Python.

Para guardar:

```text
Ctrl + O
```

Después:

```text
Enter
```

Para salir:

```text
Ctrl + X
```

---

# 16. Ejecutar el ETL

Antes de ejecutar el programa nos aseguramos de estar en la carpeta:

```bash
cd ~/prueba-ladorian-etl
```

Activamos el entorno virtual:

```bash
source venv/bin/activate
```

Ejecutamos:

```bash
python etl.py
```

---

# 17. Funcionamiento del `etl.py`

Nuestro programa realiza el siguiente proceso:

```text
Cloud Storage
      │
      │ datos_prueba_v2.csv
      ▼
   Python
      │
      ▼
    Pandas
      │
      ├── dimensiones
      ├── valores nulos
      ├── outliers
      ├── limpieza
      ├── imputación
      ├── transformación
      ├── is_holidays
      └── serie temporal
      │
      ▼
Archivos procesados
      │
      ├── ventas_limpias.csv
      └── ventas_diarias.csv
      │
      ▼
Cloud Storage
```

---

# 18. Comprobar los archivos generados

Una vez finalizado el ETL:

```bash
ls -lh
```

Deberíamos encontrar:

```text
etl.py
ventas_limpias.csv
ventas_diarias.csv
```

---

# 19. Comprobar los archivos en Cloud Storage

Ejecutamos:

```bash
gcloud storage ls gs://bucket-data-landorian/processed/
```

Deberíamos encontrar:

```text
gs://bucket-data-landorian/processed/ventas_limpias.csv
gs://bucket-data-landorian/processed/ventas_diarias.csv
```

---

# 20. Comprobar el CSV limpio

Ejecutamos:

```bash
gcloud storage cat gs://bucket-data-landorian/processed/ventas_limpias.csv | head
```

---

# 21. Comprobar la serie temporal

Ejecutamos:

```bash
gcloud storage cat gs://bucket-data-landorian/processed/ventas_diarias.csv | head
```

---

# Estado actual

Hasta este punto tenemos:

```text
                    GCP
                     │
                     ▼
             prueba-ladorian
                     │
                     ▼
              Cloud Storage
                     │
                     ▼
          bucket-data-landorian
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
datos_prueba_v2.csv       processed/
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             ventas_limpias.csv   ventas_diarias.csv
```

Y el ETL se puede ejecutar desde Cloud Shell mediante:

```bash
python etl.py
```

