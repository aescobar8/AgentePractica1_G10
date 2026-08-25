# Practica 1

El archivo CSV debe encontrarse en:

```text
data/raw/Venta_online_c.csv
```

## Ejecucion

Desde la carpeta `sog2_postgres_local`, ejecutar los siguientes comandos en **PowerShell**.

### 1. Crear el archivo de configuracipn

```powershell
Copy-Item .env.example .env
```

### 2. Levantar PostgreSQL

```powershell
docker compose up -d
```

 verificar que el contenedor esta activo:

```powershell
docker compose ps
```

### 3. Crear y activar el entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Cargar el CSV en PostgreSQL

```powershell
python scripts/carga_csv.py
```

### 6. Verificar la base de datos

conectarse al manejador de base de datos de eleccion y ejecutar 

```sql
SELECT * FROM ventas_online;
```


## Detener PostgreSQL

```powershell
docker compose down
```

Los datos se conservan en el volumen de Docker

## Reiniciar completamente la base

Solo usar si se necesita reconstruir la base desde cero

```powershell
docker compose down -v
docker compose up -d
python scripts/carga_csv.py
```

> `docker compose down -v` elimina la base de datos local y su volumen el script vuelve a cargar los datos desde el CSV

## Estructura principal

```text
sog2_postgres_local/
├── data/
│   └── raw/
│       └── Venta_online_c.csv
├── database/
│   └── schema.sql
├── scripts/
│   └── carga_csv.py
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```
