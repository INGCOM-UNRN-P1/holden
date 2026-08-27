# 💉 HOLDEN — Generador de Mocks e Inyección de Fallos en C

HOLDEN permite generar mocks y envoltorios de enlace (`-Wl,--wrap=symbol`) para simular condiciones adversas de ejecución en pruebas de software C (fallos de `malloc()`, errores de apertura en `fopen()`, generación pseudoaleatoria determinista).

## Uso Rápido

```bash
# 1. Generar mock de malloc que falla en la 2da llamada
holden generate malloc --fail-at 2 -o mock_malloc.c

# 2. Salida estructurada JSON
holden generate malloc --json

# 3. Listar funciones mockeables soportadas
holden list
```
