from google.cloud import storage
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

BUCKET_NAME = "bucket-data-landorian"

INPUT_FILE = "datos_prueba_v2.csv"

OUTPUT_FILE = "processed/ventas_limpias.csv"

DAILY_SALES_FILE = "processed/ventas_diarias.csv"


# ============================================================
# 2. LEER CSV DESDE GOOGLE CLOUD STORAGE
# ============================================================

def read_csv_from_gcs(bucket_name, file_name):

    client = storage.Client()

    bucket = client.bucket(bucket_name)

    blob = bucket.blob(file_name)

    data = blob.download_as_bytes()

    df = pd.read_csv(
        BytesIO(data),
        sep=";"
    )

    return df


# ============================================================
# 3. SUBIR CSV A GOOGLE CLOUD STORAGE
# ============================================================

def upload_csv_to_gcs(df, bucket_name, file_name):

    client = storage.Client()

    bucket = client.bucket(bucket_name)

    csv_data = df.to_csv(
        index=False
    )

    blob = bucket.blob(file_name)

    blob.upload_from_string(
        csv_data,
        content_type="text/csv"
    )

    print(f"Archivo guardado en: gs://{bucket_name}/{file_name}")


# ============================================================
# 4. ELIMINAR OUTLIERS UTILIZANDO IQR
# ============================================================

def remove_outliers_iqr(df, column):

    q1 = df[column].quantile(0.25)

    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr

    upper_bound = q3 + 1.5 * iqr

    mask = df[column].between(
        lower_bound,
        upper_bound
    )

    removed = (~mask).sum()

    print(
        f"{column}: "
        f"{removed} outliers eliminados"
    )

    print(
        f"Rango permitido: "
        f"{lower_bound:.2f} - {upper_bound:.2f}"
    )

    return df[mask].copy()


# ============================================================
# 5. LEER LOS DATOS
# ============================================================

print("\n" + "=" * 60)
print("INICIO DEL ETL")
print("=" * 60)

df = read_csv_from_gcs(
    BUCKET_NAME,
    INPUT_FILE
)

print("\nArchivo leído correctamente")


# ============================================================
# 6. DIMENSIONES
# ============================================================

print("\n" + "=" * 60)
print("DIMENSIONES")
print("=" * 60)

print(f"Número de filas: {df.shape[0]}")
print(f"Número de columnas: {df.shape[1]}")


# ============================================================
# 7. TIPOS DE DATOS
# ============================================================

print("\n" + "=" * 60)
print("TIPOS DE DATOS")
print("=" * 60)

print(df.dtypes)


# ============================================================
# 8. VALORES NULOS
# ============================================================

print("\n" + "=" * 60)
print("VALORES NULOS ANTES DE LA LIMPIEZA")
print("=" * 60)

print(df.isnull().sum())


# ============================================================
# 9. CONVERTIR FECHA
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)


# ============================================================
# 10. ELIMINAR OUTLIERS
# Variables: hour, units y total
# ============================================================

print("\n" + "=" * 60)
print("ELIMINACIÓN DE OUTLIERS")
print("=" * 60)

for column in ["hour", "units", "total"]:

    df = remove_outliers_iqr(
        df,
        column
    )


# ============================================================
# 11. ELIMINAR FILAS CON site_id NULO
# ============================================================

print("\n" + "=" * 60)
print("ELIMINACIÓN DE site_id NULOS")
print("=" * 60)

before = len(df)

df = df.dropna(
    subset=["site_id"]
)

after = len(df)

print(
    f"Filas eliminadas: {before - after}"
)

print(
    f"Filas restantes: {after}"
)


# ============================================================
# 12. IMPUTACIÓN DE VALORES NULOS
# ============================================================

print("\n" + "=" * 60)
print("IMPUTACIÓN DE NULOS")
print("=" * 60)


# Imputamos units utilizando la mediana por producto

df["units"] = (
    df.groupby("product_id")["units"]
    .transform(
        lambda x: x.fillna(x.median())
    )
)


# Imputamos total utilizando la mediana por producto

df["total"] = (
    df.groupby("product_id")["total"]
    .transform(
        lambda x: x.fillna(x.median())
    )
)


# Si algún producto tuviera todos sus valores nulos,
# utilizamos la mediana global como respaldo.

df["units"] = df["units"].fillna(
    df["units"].median()
)

df["total"] = df["total"].fillna(
    df["total"].median()
)


print("\nNulos después de la imputación:")

print(df.isnull().sum())


# ============================================================
# 13. TRANSFORMAR site_id A ENTERO
# ============================================================

print("\n" + "=" * 60)
print("TRANSFORMACIÓN DE site_id")
print("=" * 60)

df["site_id"] = df["site_id"].astype(int)

print(
    f"Tipo de site_id: {df['site_id'].dtype}"
)


# ============================================================
# 14. CREAR is_holidays
# Festivos nacionales de España - 2022
# ============================================================

print("\n" + "=" * 60)
print("CREACIÓN DE is_holidays")
print("=" * 60)


holidays_2022 = pd.to_datetime([
    "2022-01-01",  # Año Nuevo
    "2022-01-06",  # Epifanía
    "2022-04-15",  # Viernes Santo
    "2022-08-15",  # Asunción
    "2022-10-12",  # Fiesta Nacional
    "2022-11-01",  # Todos los Santos
    "2022-12-06",  # Constitución
    "2022-12-08",  # Inmaculada
    "2022-12-26"   # Navidad trasladada
])


df["is_holidays"] = (
    df["date"]
    .isin(holidays_2022)
    .astype(int)
)


print(
    df["is_holidays"].value_counts()
)


# ============================================================
# 15. COMPROBAR LOS DÍAS MARCADOS COMO FESTIVOS
# ============================================================

print("\nFechas identificadas como festivos:")

print(
    df.loc[
        df["is_holidays"] == 1,
        ["date", "is_holidays"]
    ]
    .drop_duplicates()
    .sort_values("date")
)


# ============================================================
# 16. COMPROBACIÓN FINAL DE NULOS
# ============================================================

print("\n" + "=" * 60)
print("COMPROBACIÓN FINAL DE NULOS")
print("=" * 60)

print(df.isnull().sum())


# ============================================================
# 17. COMPROBACIÓN DEL DATASET LIMPIO
# ============================================================

print("\n" + "=" * 60)
print("DATASET LIMPIO")
print("=" * 60)

print(f"Filas finales: {df.shape[0]}")
print(f"Columnas finales: {df.shape[1]}")

print("\nPrimeras filas:")

print(df.head())


# ============================================================
# 18. GUARDAR DATASET LIMPIO LOCALMENTE
# ============================================================

df.to_csv(
    "ventas_limpias.csv",
    index=False
)

print(
    "\nDataset limpio guardado como "
    "'ventas_limpias.csv'"
)


# ============================================================
# 19. SUBIR DATASET LIMPIO A CLOUD STORAGE
# ============================================================

upload_csv_to_gcs(
    df,
    BUCKET_NAME,
    OUTPUT_FILE
)


# ============================================================
# 20. GENERAR SERIE TEMPORAL
# Ventas por fecha, tienda y categoría
# ============================================================

print("\n" + "=" * 60)
print("SERIE TEMPORAL DE VENTAS")
print("=" * 60)


daily_sales = (
    df
    .groupby(
        [
            "date",
            "site_id",
            "site_name",
            "category1_id"
        ],
        as_index=False
    )["total"]
    .sum()
    .rename(
        columns={
            "total": "daily_sales"
        }
    )
)


print("\nPrimeras filas de la serie temporal:")

print(
    daily_sales.head()
)


# ============================================================
# 21. GUARDAR SERIE TEMPORAL
# ============================================================

daily_sales.to_csv(
    "ventas_diarias.csv",
    index=False
)


upload_csv_to_gcs(
    daily_sales,
    BUCKET_NAME,
    DAILY_SALES_FILE
)


# ============================================================
# 22. GENERAR GRÁFICOS
# ============================================================

print("\n" + "=" * 60)
print("GENERANDO GRÁFICOS")
print("=" * 60)


sites = daily_sales["site_id"].unique()


for site in sites:

    site_data = daily_sales[
        daily_sales["site_id"] == site
    ]

    plt.figure(
        figsize=(14, 6)
    )

    for category in sorted(
        site_data["category1_id"].unique()
    ):

        category_data = site_data[
            site_data["category1_id"] == category
        ]

        plt.plot(
            category_data["date"],
            category_data["daily_sales"],
            label=f"Categoría {category}"
        )

    plt.title(
        f"Ventas diarias - Tienda {site}"
    )

    plt.xlabel("Fecha")

    plt.ylabel("Ventas (€)")

    plt.legend()

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        f"ventas_site_{site}.png"
    )

    plt.show()


# ============================================================
# 23. FIN
# ============================================================

print("\n" + "=" * 60)
print("ETL FINALIZADO CORRECTAMENTE")
print("=" * 60)

print(
    f"Dataset limpio: "
    f"gs://{BUCKET_NAME}/{OUTPUT_FILE}"
)

print(
    f"Serie temporal: "
    f"gs://{BUCKET_NAME}/{DAILY_SALES_FILE}"
)