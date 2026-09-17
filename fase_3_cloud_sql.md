# Cloud SQL - MySQL

## 1. Crear la instancia de Cloud SQL

Desde Google Cloud Console:

https://console.cloud.google.com/

Comprobar que el proyecto seleccionado es:

`prueba-ladorian`

Acceder a:

**Cloud SQL → Instancias**

Crear una nueva instancia seleccionando:

**MySQL**

Nombre de la instancia:

`prueba-ladorian-mysql`

Durante la creación se configura el usuario `root` y su contraseña.

La contraseña debe guardarse de forma segura y no incluirse directamente en un repositorio público.

---

# 2. Crear la base de datos

Una vez creada la instancia, acceder a:

**Cloud SQL → prueba-ladorian-mysql → Cloud SQL Studio**

Autenticarse con el usuario:

`root`

Crear la base de datos:

```sql
CREATE DATABASE prueba_ladorian;
````

Seleccionar la base de datos:

```sql
USE prueba_ladorian;
```

---

# 3. Crear la tabla ventas

Crear la tabla donde se almacenarán los datos procesados:

```sql
CREATE TABLE ventas (
    site_id INT NOT NULL,
    date DATE NOT NULL,
    hour INT,
    product_id INT,
    category1_id INT,
    total DECIMAL(12,2),
    units DECIMAL(12,2),
    site_name VARCHAR(255),
    is_holidays BOOLEAN
);
```

Comprobar que la tabla se ha creado correctamente:

```sql
SHOW TABLES;
```

Resultado esperado:

```text
ventas
```

---

# 4. Obtener la IP pública de Cloud SQL

Desde Cloud Shell:

```bash
gcloud sql instances describe prueba-ladorian-mysql \
  --format="value(ipAddresses[0].ipAddress)"
```

La IP obtenida fue:

```text
34.175.247.28
```

Esta es la dirección que utilizaremos para conectar Python con Cloud SQL.

---

# 5. Obtener la IP de Cloud Shell

Desde Cloud Shell:

```bash
curl -s ifconfig.me
```

La IP obtenida fue:

```text
34.14.83.16
```

---

# 6. Autorizar Cloud Shell en Cloud SQL

Se añadió la IP de Cloud Shell a las redes autorizadas de la instancia:

```bash
gcloud sql instances patch prueba-ladorian-mysql \
  --authorized-networks=34.14.83.16
```

Comprobar la configuración:

```bash
gcloud sql instances describe prueba-ladorian-mysql \
  --format="value(settings.ipConfiguration.authorizedNetworks)"
```

Debe aparecer:

```text
34.14.83.16
```

---

# 7. Instalar el conector de MySQL para Python

Dentro del entorno virtual del proyecto:

```bash
cd ~/prueba-ladorian-etl
```

Activar el entorno:

```bash
source venv/bin/activate
```

Instalar el conector:

```bash
pip install mysql-connector-python
```

Comprobar que funciona:

```bash
python -c "import mysql.connector; print('MySQL connector OK')"
```

Resultado esperado:

```text
MySQL connector OK
```

---

# 8. Crear un script para comprobar la conexión

Crear:

```bash
nano test_mysql.py
```

Código:

```python
import mysql.connector

connection = mysql.connector.connect(
    host="34.175.247.28",
    user="root",
    password="TU_CONTRASEÑA",
    database="prueba_ladorian"
)

if connection.is_connected():
    print("Conexión a Cloud SQL correcta")

cursor = connection.cursor()

cursor.execute("SHOW TABLES")

for table in cursor.fetchall():
    print(table)

cursor.close()
connection.close()
```

Sustituir:

```text
TU_CONTRASEÑA
```

por la contraseña configurada para el usuario `root`.

No se debe compartir la contraseña ni almacenarla en un repositorio público.

---

# 9. Ejecutar la prueba de conexión

Desde Cloud Shell:

```bash
python test_mysql.py
```

Resultado esperado:

```text
Conexión a Cloud SQL correcta
('ventas',)
```

Esto confirma que:

```text
Python
   │
   ▼
Cloud Shell
   │
   │ conexión MySQL
   ▼
Cloud SQL
   │
   ▼
prueba_ladorian
   │
   ▼
ventas
```

---

# 10. Conectar el ETL con Cloud SQL

El proceso ETL que ya habíamos creado en `etl.py` lee los datos desde Cloud Storage y realiza las transformaciones.

El flujo es:

```text
Cloud Storage
      │
      │ datos_prueba_v2.csv
      ▼
Python + Pandas
      │
      ├── detectar nulos
      ├── eliminar outliers
      ├── eliminar site_id nulos
      ├── imputar valores
      ├── convertir site_id
      ├── crear is_holidays
      └── generar ventas diarias
      │
      ▼
DataFrame limpio
      │
      ▼
Cloud SQL
      │
      ▼
prueba_ladorian
      │
      ▼
ventas
```

---

# 11. Insertar los datos en Cloud SQL

En `etl.py` se utiliza:

```python
import mysql.connector
```

Configuración:

```python
MYSQL_HOST = "34.175.247.28"
MYSQL_USER = "root"
MYSQL_PASSWORD = "TU_CONTRASEÑA"
MYSQL_DATABASE = "prueba_ladorian"
```

Conexión:

```python
connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
```

---

# 12. Preparar la sentencia INSERT

```python
insert_query = """
INSERT INTO ventas (
    site_id,
    date,
    hour,
    product_id,
    category1_id,
    total,
    units,
    site_name,
    is_holidays
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
```

---

# 13. Preparar los datos del DataFrame

Utilizamos el DataFrame `df`, que ya contiene los datos limpios:

```python
data = [
    tuple(row)
    for row in df[
        [
            "site_id",
            "date",
            "hour",
            "product_id",
            "category1_id",
            "total",
            "units",
            "site_name",
            "is_holidays"
        ]
    ].itertuples(
        index=False,
        name=None
    )
]
```

---

# 14. Insertar los registros

```python
cursor.executemany(
    insert_query,
    data
)

connection.commit()
```

`executemany()` permite insertar múltiples registros utilizando la misma sentencia SQL.

---

# 15. Comprobar el número de registros insertados

Desde Python:

```python
print(
    f"Registros insertados: {cursor.rowcount}"
)
```

También podemos comprobarlo directamente desde Cloud SQL:

```sql
SELECT COUNT(*) AS total_registros
FROM ventas;
```

---

# 16. Comprobar los datos

Consultar algunos registros:

```sql
SELECT *
FROM ventas
LIMIT 10;
```

---

# 17. Comprobar que site_id es entero

```sql
SELECT
    site_id,
    site_name
FROM ventas
LIMIT 10;
```

---

# 18. Comprobar is_holidays

```sql
SELECT
    date,
    is_holidays
FROM ventas
WHERE is_holidays = 1
GROUP BY date, is_holidays
ORDER BY date;
```

---

# 19. Comprobar valores nulos

```sql
SELECT
    COUNT(*) AS filas_con_nulos
FROM ventas
WHERE site_id IS NULL
   OR date IS NULL
   OR units IS NULL
   OR total IS NULL;
```

El resultado esperado es:

```text
0
```

---

# 20. Comprobar inconsistencias entre site_id y site_name

## Un site_id asociado a varios nombres

```sql
SELECT
    site_id,
    COUNT(DISTINCT site_name) AS numero_nombres
FROM ventas
GROUP BY site_id
HAVING COUNT(DISTINCT site_name) > 1;
```

Esta consulta permite detectar casos en los que un mismo `site_id` aparece asociado a diferentes nombres de tienda.

---

## Un site_name asociado a varios IDs

```sql
SELECT
    site_name,
    COUNT(DISTINCT site_id) AS numero_ids
FROM ventas
GROUP BY site_name
HAVING COUNT(DISTINCT site_id) > 1;
```

Esta consulta permite detectar nombres de tienda asociados a diferentes identificadores.

---

# 21. Resultado de la arquitectura actual

Hasta este punto tenemos:

```text
                    GCP
                     │
       ┌─────────────┴─────────────┐
       │                           │
       ▼                           ▼
Cloud Storage                 Cloud SQL
       │                           │
       │ CSV                       │ MySQL
       ▼                           ▼
datos_prueba_v2.csv          prueba_ladorian
       │                           │
       ▼                           ▼
Python + Pandas                ventas
       │
       │ ETL
       ▼
datos limpios
       │
       └──────────────► Cloud SQL
```

La Parte 2 de la prueba queda cubierta mediante:

1. Creación de la base de datos `prueba_ladorian`.
2. Creación de la tabla `ventas`.
3. Carga de los datos procesados.
4. Comprobación de inconsistencias entre `site_id` y `site_name`.

```

**Importante:** las IP que aparecen arriba son las que utilizamos durante la práctica. La IP pública de Cloud Shell puede cambiar, así que si posteriormente vuelves a conectarte y deja de funcionar, habrá que obtener la IP actual y actualizar las redes autorizadas.
```
