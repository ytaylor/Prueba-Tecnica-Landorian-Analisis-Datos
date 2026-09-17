
# Guía — Inicio del proyecto en Google Cloud

## 1. Crear el proyecto en Google Cloud

### ¿Qué es?

Un **proyecto de GCP** es el contenedor lógico donde vamos a organizar todos los recursos de nuestra solución.

En nuestro caso:

```text
Google Cloud
│
└── Proyecto: prueba-ladorian
```

Dentro del proyecto tendremos posteriormente:

```text
prueba-ladorian
│
├── Cloud Storage
├── Cloud Run
├── Cloud SQL
├── Cloud Scheduler
└── APIs / permisos
```

### ¿Cómo hacerlo?

Entramos en:

[Google Cloud Console](https://console.cloud.google.com/?utm_source=chatgpt.com)

1. Iniciar sesión con la cuenta de Google.
2. En la parte superior, seleccionar **Seleccionar proyecto**.
3. Pulsar **Nuevo proyecto**.
4. Introducir:

```text
Nombre: prueba-ladorian
```

5. Pulsar **Crear**.
6. Seleccionar posteriormente el proyecto `prueba-ladorian`.

### Comprobación

En la parte superior de la consola debemos ver:

```text
prueba-ladorian
```

Esto es importante porque **todos los recursos que creemos a partir de ahora deben estar dentro de este proyecto**.

---

# 2. Crear un bucket de Cloud Storage

## ¿Qué es Cloud Storage?

**Cloud Storage es el servicio de almacenamiento de objetos de Google Cloud.**

Para entenderlo fácilmente:

```text
Tu ordenador
└── carpeta
     └── archivo.csv
```

es parecido a:

```text
Google Cloud
└── bucket
     └── archivo.csv
```

En nuestro ETL lo vamos a utilizar como **zona de entrada de los datos originales**.

La prueba nos proporciona un CSV con los tickets de ventas. 

Por tanto:

```text
CSV original
     ↓
Cloud Storage
```

---

# 3. Entrar en Cloud Storage

Desde la consola de Google Cloud:

1. Utilizamos el buscador superior.
2. Escribimos:

```text
Cloud Storage
```

3. Entramos en **Cloud Storage → Buckets**.

También podemos acceder directamente desde:

[Cloud Storage - Buckets](https://console.cloud.google.com/storage/browser?utm_source=chatgpt.com)

---

# 4. Crear el bucket

Pulsamos:

**Crear**

Un **bucket** es el contenedor donde almacenaremos nuestros archivos.

### Nombre

En nuestro caso hemos creado:

```text
bucket-data-landorian
```

> El nombre del bucket tiene que ser único a nivel global en Google Cloud.

---

# 5. Elegir ubicación

Al crear el bucket tenemos que decidir dónde se almacenan físicamente los datos.

En nuestro caso aparece:

```text
Ubicación:
us (múltiples regiones en Estados Unidos)
```

Esto significa que el bucket está configurado en múltiples regiones de Estados Unidos.

**Para un proyecto europeo, elegiría una región europea**, especialmente porque estamos trabajando desde España.

Por ejemplo:

```text
europe-southwest1
```

si está disponible para la configuración que estamos utilizando.

¿Por qué?

Porque la ubicación de los recursos es una decisión arquitectónica y puede afectar a:

* latencia,
* costes de transferencia,
* residencia de datos,
* cumplimiento normativo.

---

# 6. Clase de almacenamiento

Seleccionamos:

```text
Standard
```

## ¿Qué significa?

Google tiene diferentes clases de almacenamiento dependiendo de cuánto accedamos a los datos.

Para nuestro caso:

```text
Standard
```

tiene sentido porque vamos a trabajar frecuentemente con el CSV.

No necesitamos almacenamiento de archivo histórico que casi nunca se consulte.

---

# 7. Acceso público

Configuramos el bucket como:

```text
No público
```

Esto es importante.

Nuestro CSV contiene datos de ventas, así que **no queremos que cualquiera pueda acceder a él desde Internet**.

La arquitectura será:

```text
                  Google Cloud
                       │
                 ┌─────▼─────┐
                 │   Bucket  │
                 │ Privado   │
                 └─────┬─────┘
                       │
                       ▼
                   ETL / Cloud Run
```

No:

```text
Internet
    │
    ▼
CSV público ❌
```

---

# 8. Subir el archivo CSV

Una vez creado el bucket:

1. Entramos en el bucket.
2. Pulsamos **Subir**.
3. Seleccionamos:

```text
datos_prueba_v2.csv
```

4. Esperamos a que termine la carga.

---

# 9. Comprobación final

Nuestro bucket actualmente tiene:

```text
bucket-data-landorian
│
└── datos_prueba_v2.csv
```

En tu captura se ve correctamente el archivo, con un tamaño aproximado de **5,9 MB**, así que esta parte está hecha. ✅

---

# 10. ¿Qué hemos construido hasta ahora?

Aunque parezca poco, ya hemos empezado la arquitectura.

Tenemos:

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
              ▼
   datos_prueba_v2.csv
```

Este sería nuestro **origen de datos**.

---

# 11. ¿Dónde encaja esto dentro del ETL?

La prueba nos pide automatizar un proceso que:

> lea un archivo → lo procese → lo cargue en una base de datos. 

Por ahora hemos hecho solamente:

### E — Extract

```text
CSV
 ↓
Cloud Storage
```

Después construiremos:

### T — Transform

```text
Cloud Storage
      ↓
Python + Pandas
      ↓
limpieza
      ↓
transformación
```

Aquí haremos exactamente lo que hemos trabajado en la Parte 1:

* detectar nulos,
* eliminar outliers,
* eliminar `site_id` nulos,
* imputar valores,
* convertir `site_id`,
* crear `is_holidays`,
* generar las series temporales.

Y finalmente:

### L — Load

```text
Python
   ↓
Cloud SQL
   ↓
MySQL
   ↓
ventas
```

-
