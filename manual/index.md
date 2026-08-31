---
title: "Manual de Referencia: holden"
subtitle: "Holden — Generador de Mocks de Funciones C e Inyector de Fallos de Memoria y Archivos"
author: "Cátedra de Algoritmos y Programación"
date: "2026-08-31"
---

(manual-holden)=
# Holden — Generador de Mocks de Funciones C e Inyector de Fallos de Memoria y Archivos

````{abstract}
**Rol en el ecosistema:** Generación de envoltorios (wrappers) y mocks de funciones C con linking de GCC (`-Wl,--wrap=`) para simular fallos de malloc devolviendo NULL, errores de lectura en fopen y semillas fijas de rand.
````

---

(manual-holden-proposito)=
## 1. Propósito y Filosofía Pedagógica

La herramienta **`holden`** forma parte del ecosistema oficial de software de la cátedra. Su diseño sigue principios pedagógicos rigurosos:

1. **Evidencia Técnica Directa**: Todo diagnóstico se fundamenta en la norma ISO C (C11/C23), en el modelo de memoria del sistema o en convenciones arquitectónicas formales.
2. **Acción Correctiva Concreta**: Cada advertencia incluye la prescripción técnica inmediata para resolver el defecto sin recurrir a conjeturas.
3. **Autonomía del Estudiante**: Facilita la autoevaluación local antes de la entrega final del trabajo práctico.
4. **Objetividad Docente**: Estandariza la corrección automática eliminando discrepancias subjetivas en la evaluación.

---

(manual-holden-instalacion)=
## 2. Instalación y Diagnóstico del Entorno

````{important}
Asegurate de contar con el compilador GCC/Clang y las librerías del sistema instaladas antes de ejecutar `holden`.
````

Para comprobar el estado de salud de tu entorno de trabajo y las dependencias auxiliares:

````{code-block} bash
# Comprobación de dependencias del sistema
holden doctor
````

Si se detecta la falta de alguna utilidad (como `gdb`, `valgrind`, `clang-format` o `typst`), el comando indicará el paquete exacto a instalar según tu distribución GNU/Linux o entorno MSYS2.

---

(manual-holden-comandos)=
## 3. Referencia Completa de Comandos CLI

A continuación se detallan los subcomandos principales disponibles en `holden`:

| Sintaxis del Comando | Descripción y Efecto |
| :--- | :--- |
| `holden gen-mock <header.h> --func <fn>` | Genera el wrapper `__wrap_fn` para interceptar la función en tests. |
| `holden inject-fault --type malloc -o mock_malloc.c` | Crea un mock de malloc con falla programable tras N llamadas. |
| `holden scaffold-tests <archivo.c>` | Crea la plantilla de suite de tests unitarios con mocks incorporados. |
| `holden doctor` | Comprueba compatibilidad del linker GNU ld con `--wrap`. |

````{tip}
Podés agregar el flag `--json` a la mayoría de los comandos para exportar resultados en formato estructurado o `--md` para generar reportes Markdown para el informe de entrega.
````

---

(manual-holden-tutorial)=
## 4. Tutorial Paso a Paso con Ejemplos Reales

### Caso de Estudio

Considerá el siguiente fragmento de código representativo:

````{code-block} c
:linenos:
#include <stdlib.h>
#include <stdbool.h>

// Función a probar bajo fallo simulado de malloc
char* duplicar_cadena(const char *s) {
    if (!s) return NULL;
    char *dup = malloc(100);
    if (!dup) {
        return NULL; // Camino defensivo probado con Holden
    }
    // copiar...
    return dup;
}
````

### Ejecución de la Herramienta

Ejecutá el análisis desde tu terminal:

````{code-block} bash
holden gen-mock <header.h> --func <fn>
````

### Salida Obtenida en Consola

````{code-block} text
[✓] Mock generado: mock_malloc.c (__wrap_malloc)
[✓] Configuración de linking generada: CFLAGS += -Wl,--wrap=malloc
[✓] Test unitario: Invocación #1 retornó NULL -> duplicar_cadena() manejó el error retornando NULL (PASS).
````

````{note}
Prestá atención a la explicación pedagógica generada: la herramienta no solo señala la línea del problema, sino que explica la causa raíz y el impacto en memoria o arquitectura.
````

---

(manual-holden-ejercicios)=
## 5. Ejercicios Prácticos y Desafíos

Practicá el uso avanzado de **`holden`** resolviendo los siguientes ejercicios:

````{exercise} Desafío 1: Simulación de Memoria Agotada (OOM)
Verificar que el TDA Lista libera los nodos previos si el 5to `malloc` falla.

**Instrucción de ejecución:**
```bash
holden inject-fault --type malloc --fail-at 5 -o mock_malloc.c
```
````

````{solution} Desafío 1
```bash
holden inject-fault --type malloc --fail-at 5 -o mock_malloc.c
# Verificá que la operación concluya exitosamente con código de salida 0.
```
````

````{exercise} Desafío 2: Mock de `fopen` para Pruebas de Archivos Inexistentes
Simular fallo de permisos al abrir un archivo de configuración.

**Instrucción de ejecución:**
```bash
holden gen-mock stdio.h --func fopen
```
````

````{solution} Desafío 2
```bash
holden gen-mock stdio.h --func fopen
# Revisá el archivo generado o el informe en terminal para confirmar la resolución del problema.
```
````

````{exercise} Desafío 3: Determinismo con Mock de `rand()`
Fijar la secuencia pseudoaleatoria para pruebas unitarias reproducibles.

**Instrucción de ejecución:**
```bash
holden gen-mock stdlib.h --func rand --deterministic
```
````

````{solution} Desafío 3
```bash
holden gen-mock stdlib.h --func rand --deterministic
# Comprobá que la salida confirme la ausencia de advertencias o errores pendientes.
```
````

---

(manual-holden-makefile)=
## 6. Integración en el Flujo de Trabajo y Makefile

Para incorporar `holden` de forma automática a tu flujo de desarrollo, agregá la siguiente regla en el `Makefile` de tu proyecto:

````{code-block} makefile
check-holden:
	@echo "=== Ejecutando verificación con holden ==="
	holden check src/ include/

.PHONY: check-holden
````

Ejecutá `make check-holden` antes de cada commit para asegurar que tu código conserve el estado de aprobación.

---

(manual-holden-arquitectura)=
## 7. Arquitectura Interna y Mecanismo Técnico

La herramienta **`holden`** implementa un motor de alta precisión basado en:

- **Tecnología Núcleo:** `GNU ld Wrapping Engine (-Wl,--wrap=) + Dynamic C Mock Generator + Stub Factory`.
- **Aislamiento y Determinismo:** Diseñada para operar sin efectos colaterales en entornos de integración continua (CI), terminales de estudiantes y servidores docentes headless.
- **Manejo de Errores Pedagógico:** Todo fallo de sintaxis, memoria o lógica se traduce en una acción prescriptiva concreta con su respectiva justificación técnica.

---

(manual-holden-ecosistema)=
## 8. Integración y Conexión con el Ecosistema

````{note}
Ninguna herramienta opera de forma aislada. **`holden`** forma parte del pipeline integral de evaluación, verificación y enseñanza de la cátedra.
````

### Diagrama de Flujo e Interoperabilidad

````{mermaid}
graph TD
    HDR[Headers C: stdio.h, stdlib.h] --> HLD[Holden: Motor de Mocks]
    HLD -->|Generación de Wrappers| LD[GNU ld --wrap=malloc]
    HLD -->|Inyección de Fallos en Tests| DKD[Deckard: Suites Unitarias]
    HLD -->|Verificación Defensiva| DRD[Dredd: Calificador Masivo]
````

### Matriz de Intercambio de Datos

| Canal | Herramientas Conectadas | Tipo de Datos Transferidos |
| :--- | :--- | :--- |
| **Entradas (Inputs)** | - `Headers C y funciones del sistema (malloc, fopen, rand)` | Código fuente, AST, binarios, testcases, contratos |
| **Salidas (Outputs)** | - `deckard (plantillas de tests unitarios)`
- `dredd (evaluación de robustez)` | Informes Markdown, diagnósticos Rich, JSON, actas |
| **Sincronización** | `vasquez`, `deckard`, `vassili` | Validación cruzada, flags compartidos y autofix |

### Pipeline de Integración Recomendado

Podés encadenar `holden` con otras herramientas del ecosistema en una única línea de comando:

````{code-block} bash
# Pipeline de integración típico
holden scaffold-tests src/tda.c && make test
````

