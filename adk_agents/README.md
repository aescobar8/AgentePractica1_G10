# Agente conversacional con Google ADK

Este agente usa Gemini y consume las herramientas del MCP Server común por
medio de `McpToolset` y el transporte `stdio`.

## Configuración

```powershell
Copy-Item adk_agents/.env.example adk_agents/.env
```

Editar `adk_agents/.env` y colocar una clave válida en `GOOGLE_API_KEY`.

## Ejecutar

Desde la raíz del repositorio:

```powershell
& mcp_server/.venv-adk/Scripts/adk.exe web adk_agents --no-reload
```

Abrir la dirección que muestre la terminal, seleccionar `agente_ventas` y
probar preguntas como:

- ¿Cuál es el navegador con más clientes y cuántas compras acumula?
- Compara la media de tiempo de todos los navegadores.
- ¿Qué diferencias existen entre géneros?
- Resume el uso de boletines y vales.
