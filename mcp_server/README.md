# MCP Server común - Grupo 10

Este servidor expone al agente de Google ADK las herramientas de análisis que
cada integrante agregue al repositorio. Consulta la base PostgreSQL en la nube y
usa el transporte MCP `stdio`.

## Herramientas incluidas actualmente

El descubrimiento automático carga todos los archivos que cumplan esta ruta:

```text
personaN/ia_mcp/herramientas_*.py
```

Actualmente registra las herramientas de:

- Persona 3: navegadores, compras, ventas y tiempo.
- Persona 5: género, compras y método de pago.
- Persona 6: boletines, vales y promociones.

## Instalación

Desde la raíz del repositorio:

```powershell
py -m venv mcp_server/.venv
& mcp_server/.venv/Scripts/python.exe -m pip install -r mcp_server/requirements.txt
Copy-Item mcp_server/.env.example mcp_server/.env
```

Completar `mcp_server/.env` con las credenciales de PostgreSQL. Si no existe,
el servidor intenta utilizar `persona4/sog2_postgres_local/.env` como
configuración compartida.

## Ejecutar el MCP Server

```powershell
& mcp_server/.venv/Scripts/python.exe mcp_server/server.py
```

El proceso queda esperando mensajes MCP por entrada y salida estándar. No se
deben agregar `print()` al servidor ni a los módulos, porque romperían el
protocolo `stdio`.

## Agregar la parte de otro integrante

Crear, por ejemplo:

```text
persona2/ia_mcp/herramientas_edad.py
```

Puede copiarse `mcp_server/templates/herramienta_persona.py` como punto de
partida y luego cambiar el nombre, la consulta, los parámetros y la
descripción.

El archivo debe exponer una lista `TOOL_DEFINITIONS`:

```python
def resumen_edades(connection, edad_minima: int = 18):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM ventas_online WHERE edad >= %s",
            (edad_minima,),
        )
        return {"clientes": cursor.fetchone()[0]}


TOOL_DEFINITIONS = [
    {
        "name": "resumen_edades",
        "description": "Cuenta clientes desde una edad mínima.",
        "parameters": {
            "edad_minima": {"type": "integer", "default": 18}
        },
        "handler": resumen_edades,
    }
]
```

Reglas de colaboración:

1. El nombre de cada herramienta debe ser único en todo el grupo.
2. El primer parámetro del `handler` debe ser `connection`.
3. Las consultas deben ser parametrizadas; no concatenar entradas en SQL.
4. El resultado debe poder convertirse a JSON (`dict`, `list`, texto o números).
5. No abrir otra conexión dentro del módulo; el servidor la proporciona.
6. No colocar contraseñas ni `print()` en los módulos.

Al reiniciar el MCP Server, la herramienta nueva se descubre automáticamente.
No es necesario modificar `mcp_server/server.py`.

## Integración con Google ADK

El agente ADK utiliza un entorno separado para evitar conflictos entre las
versiones de sus dependencias y las del servidor MCP:

```powershell
py -m venv mcp_server/.venv-adk
& mcp_server/.venv-adk/Scripts/python.exe -m pip install -r mcp_server/requirements-adk.txt
```

`adk_agent_example.py` muestra la integración mediante `McpToolset`,
`StdioConnectionParams` y rutas absolutas. El agente inicia el MCP Server con
el Python de `mcp_server/.venv` y descubre automáticamente sus herramientas.
Si ese entorno está en otra ubicación, se puede definir `MCP_SERVER_PYTHON` con
la ruta absoluta de su ejecutable de Python.

## Verificación

Listar las herramientas sin iniciar un cliente externo:

```powershell
& mcp_server/.venv/Scripts/python.exe mcp_server/check_server.py
```

Para abrir MCP Inspector en Windows, activar primero el entorno para que `uv`
esté disponible en `PATH`:

```powershell
& mcp_server/.venv/Scripts/Activate.ps1
mcp dev mcp_server/server.py
```
