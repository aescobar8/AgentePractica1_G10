# Guía del MCP Server y Google ADK - Grupo 10

## 1. Objetivo

Esta guía explica cómo funciona el MCP Server común del grupo y qué debe tomar
en cuenta cada integrante al agregar sus análisis.

La arquitectura general es:

```text
Usuario
  ↓
Google ADK + Gemini
  ↓
MCP Server común
  ↓
Herramientas de cada integrante
  ↓
PostgreSQL en la nube
```

Google ADK contiene el agente conversacional. El MCP Server publica las
herramientas disponibles y cada herramienta consulta PostgreSQL para entregar
resultados reales.

## 2. Estructura principal

```text
mcp_server/
├── templates/
│   └── herramienta_persona.py
├── __init__.py
├── .env.example
├── .gitignore
├── adk_agent_example.py
├── check_server.py
├── config.py
├── registry.py
├── requirements-adk.txt
├── requirements.txt
├── server.py
├── README.md
└── GUIA_MCP_IA.md

adk_agents/
├── agente_ventas/
│   ├── __init__.py
│   └── agent.py
├── .env.example
└── README.md
```

## 3. Función de cada archivo

### `mcp_server/server.py`

Es el punto de entrada del MCP Server.

- Crea el servidor `sog2-grupo10-ventas`.
- Descubre las herramientas de los integrantes.
- Convierte los parámetros declarados en esquemas MCP.
- Proporciona una conexión PostgreSQL a cada herramienta.
- Publica las herramientas mediante el transporte `stdio`.

Los integrantes no necesitan modificar este archivo para agregar su parte.

### `mcp_server/registry.py`

Realiza el descubrimiento automático.

Busca archivos con este patrón:

```text
personaN/ia_mcp/herramientas_*.py
```

Después valida:

- nombre de la herramienta;
- descripción;
- parámetros;
- función encargada de ejecutar la consulta;
- nombres duplicados entre integrantes.

### `mcp_server/config.py`

Administra la configuración y conexión con PostgreSQL.

Utiliza como configuración compartida:

```text
persona4/sog2_postgres_local/.env
```

También permite configurar específicamente el servidor mediante:

```text
mcp_server/.env
```

Este último tiene prioridad cuando existe.

### `mcp_server/check_server.py`

Comprueba que el servidor pueda iniciar y lista las herramientas registradas.

```powershell
& .\mcp_server\.venv\Scripts\python.exe .\mcp_server\check_server.py
```

### `mcp_server/adk_agent_example.py`

Es un ejemplo de integración entre Google ADK y el MCP Server. Muestra cómo
utilizar:

- `McpToolset`;
- `StdioConnectionParams`;
- `StdioServerParameters`;
- una ruta absoluta al servidor.

El agente utilizado por el proyecto está en:

```text
adk_agents/agente_ventas/agent.py
```

### `mcp_server/requirements.txt`

Dependencias exclusivas del MCP Server:

- SDK oficial de MCP;
- `psycopg` para PostgreSQL;
- `python-dotenv` para cargar `.env`;
- `uv` para ejecutar y probar el servidor.

### `mcp_server/requirements-adk.txt`

Dependencias exclusivas del agente de Google ADK.

ADK y el MCP Server utilizan entornos separados porque sus versiones del SDK
de MCP son diferentes. La comunicación se realiza mediante el protocolo
`stdio`, por lo que no necesitan compartir el mismo entorno virtual.

### `mcp_server/.env.example`

Ejemplo de configuración para PostgreSQL y Google:

```env
POSTGRES_HOST=servidor.ejemplo.com
POSTGRES_PORT=5432
POSTGRES_DB=nombre_base
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_SSLMODE=require
GOOGLE_API_KEY=clave_de_ejemplo
GOOGLE_MODEL=gemini-flash-latest
```

Este archivo solamente contiene ejemplos. No deben colocarse credenciales
reales dentro de él.

### `mcp_server/.gitignore`

Evita subir archivos sensibles o generados automáticamente:

```text
.env
.venv/
.venv-adk/
__pycache__/
*.pyc
```

### `mcp_server/templates/herramienta_persona.py`

Plantilla que los integrantes pueden copiar para crear su módulo de
herramientas.

### `mcp_server/__init__.py`

Permite que Python trate `mcp_server` como un paquete importable.

### `mcp_server/README.md`

Contiene instrucciones rápidas de instalación, ejecución, colaboración e
integración con Google ADK.

### `mcp_server/.venv/`

Entorno virtual del MCP Server. Se genera localmente y no se sube a Git.

### `mcp_server/.venv-adk/`

Entorno virtual de Google ADK. Se genera localmente y tampoco se sube a Git.

### `__pycache__/`

Carpetas temporales creadas por Python. No se editan ni se suben a Git.

### `adk_agents/agente_ventas/agent.py`

Define el agente conversacional real.

- Selecciona el modelo de Gemini.
- Incluye las instrucciones del analista.
- Inicia el MCP Server como un subproceso.
- Descubre sus herramientas mediante `McpToolset`.
- Permite que Gemini decida qué herramienta utilizar según la pregunta.

### `adk_agents/.env`

Contiene la clave real de Gemini:

```env
GOOGLE_API_KEY=clave_real
GOOGLE_MODEL=gemini-flash-latest
```

Este archivo es privado y está ignorado por Git.

## 4. Cómo agregar la parte de un integrante

Cada integrante debe crear esta estructura:

```text
personaN/
└── ia_mcp/
    ├── __init__.py
    └── herramientas_tema.py
```

Puede copiar la plantilla:

```powershell
Copy-Item `
  .\mcp_server\templates\herramienta_persona.py `
  .\persona2\ia_mcp\herramientas_edad.py
```

No debe copiar la plantilla con el mismo nombre de herramienta sin modificarla.

## 5. Estructura de una herramienta

La función debe recibir primero `connection`:

```python
from typing import Any


def resumen_edades(
    connection: Any,
    edad_minima: int = 18,
) -> dict[str, int]:
    if not 0 <= edad_minima <= 120:
        raise ValueError("edad_minima debe estar entre 0 y 120.")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM ventas_online
            WHERE edad >= %s;
            """,
            (edad_minima,),
        )
        return {"clientes": cursor.fetchone()[0]}
```

Después debe publicarse en `TOOL_DEFINITIONS`:

```python
TOOL_DEFINITIONS = [
    {
        "name": "resumen_edades",
        "description": "Cuenta clientes desde una edad mínima.",
        "parameters": {
            "edad_minima": {
                "type": "integer",
                "default": 18,
            }
        },
        "handler": resumen_edades,
    }
]
```

Al reiniciar el servidor o Google ADK, la herramienta se descubre
automáticamente. No se debe modificar `server.py`.

## 6. Tipos de parámetros permitidos

Los parámetros pueden declarar:

```text
integer
number
string
boolean
array
object
```

Ejemplos:

```python
"limite": {"type": "integer", "default": 10}
```

```python
"mes": {"type": "integer", "required": True}
```

```python
"segmento": {"type": "string", "required": False}
```

No se recomienda declarar enumeraciones numéricas como:

```python
"enum": [0, 1, 2]
```

Gemini no acepta enumeraciones numéricas dentro de sus declaraciones de
funciones. El parámetro debe declararse como entero y validarse dentro del
`handler`.

## 7. Reglas obligatorias para las herramientas

### Nombres únicos

El nombre debe ser único en todo el proyecto:

```python
"name": "persona2_resumen_edades"
```

Se recomienda utilizar el número de persona o el tema cuando pueda existir una
colisión.

### Descripciones claras

Gemini utiliza la descripción para decidir qué herramienta llamar. Una mala
descripción puede provocar que seleccione la herramienta incorrecta.

Descripción adecuada:

```text
Compara clientes, compras y ventas por grupo de edad.
```

Descripción poco útil:

```text
Hace el análisis.
```

### Consultas parametrizadas

Correcto:

```python
cursor.execute(
    "SELECT * FROM ventas_online WHERE edad >= %s",
    (edad_minima,),
)
```

Incorrecto:

```python
cursor.execute(
    f"SELECT * FROM ventas_online WHERE edad >= {edad_minima}"
)
```

### No crear conexiones adicionales

El servidor proporciona `connection`. La herramienta debe utilizarla y no abrir
otra conexión con `psycopg.connect()`.

### No utilizar `print()`

El transporte `stdio` utiliza la entrada y salida estándar para el protocolo
MCP. Un `print()` dentro del servidor o las herramientas puede romper la
comunicación.

Las funciones deben retornar el resultado:

```python
return {"clientes": 100}
```

### Resultados compatibles con JSON

Las herramientas deben retornar:

- diccionarios;
- listas;
- texto;
- enteros;
- decimales convertidos a `float`;
- booleanos;
- fechas convertidas con `.isoformat()`.

Ejemplo para `Decimal`:

```python
from decimal import Decimal


def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    return value
```

### Validar entradas

Aunque el esquema indique que un parámetro es entero, la herramienta debe
validar su rango:

```python
if navegador not in (0, 1, 2, 3, 4):
    raise ValueError("navegador debe estar entre 0 y 4.")
```

### No incluir secretos

Está prohibido colocar en el código:

- contraseñas de PostgreSQL;
- claves de Gemini;
- tokens;
- cadenas de conexión privadas.

## 8. Probar el MCP Server

### Verificación rápida

```powershell
& .\mcp_server\.venv\Scripts\python.exe .\mcp_server\check_server.py
```

### MCP Inspector

```powershell
$env:Path = "$PWD\mcp_server\.venv\Scripts;$env:Path"
mcp dev .\mcp_server\server.py
```

En el Inspector:

1. conectarse al servidor;
2. abrir `Tools`;
3. seleccionar una herramienta;
4. escribir sus parámetros;
5. presionar `Run Tool`.

## 9. Probar Google ADK

Configurar la clave en `adk_agents/.env` y ejecutar:

```powershell
& .\mcp_server\.venv-adk\Scripts\adk.exe web .\adk_agents --no-reload
```

En la interfaz:

1. seleccionar `agente_ventas`;
2. crear una sesión nueva;
3. realizar una pregunta relacionada con una herramienta;
4. revisar en `Events` qué herramienta MCP llamó el agente.

Ejemplos:

```text
¿Cuál es el navegador con mayor cantidad de clientes?
```

```text
Compara la media de compras entre géneros.
```

```text
Resume el uso de boletines y vales durante 2021.
```

## 10. Qué hacer después de agregar herramientas

1. Ejecutar `check_server.py`.
2. Confirmar que la herramienta aparece en la lista.
3. Probarla mediante MCP Inspector.
4. Reiniciar Google ADK.
5. Crear una sesión nueva en ADK.
6. Hacer una pregunta que requiera la herramienta.
7. Verificar que la respuesta incluya datos reales.

## 11. Antes de subir cambios a Git

Ejecutar:

```powershell
git status
```

Nunca deben aparecer:

```text
.env
.venv/
.venv-adk/
GOOGLE_API_KEY
POSTGRES_PASSWORD
```

Solo deben subirse el código, documentación, consultas, gráficas y archivos de
ejemplo que no contengan información privada.

## 12. Responsabilidad de cada integrante

Cada integrante es responsable de:

- validar sus consultas SQL;
- comprobar que los cálculos sean correctos;
- escribir descripciones claras para Gemini;
- retornar valores exactos y compatibles con JSON;
- probar su herramienta antes de integrarla;
- documentar qué pregunta puede responder;
- evitar modificaciones innecesarias al núcleo común;
- no publicar credenciales.

El MCP Server facilita la integración, pero no sustituye la validación del
análisis realizado por cada persona.
