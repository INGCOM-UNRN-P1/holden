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
## 2. Instalación y Verificación del Entorno

````{important}
Para garantizar la reproducibilidad técnica de la cátedra, asegurate de instalar las dependencias nativas del sistema operativo antes de instalar el paquete Python.
````

### 2.1 Requisitos Previos del Sistema

Instalá los paquetes del sistema requeridos según tu distribución o entorno:

````{tab-set}
```{tab-item} Ubuntu / Debian
sudo apt update && sudo apt install -y \
    build-essential \
    gcc \
    gdb \
    valgrind \
    clang-format \
    libclang-dev \
    bubblewrap \
    typst \
    graphviz \
    python3-pip \
    python3-venv
```

```{tab-item} Arch Linux / Manjaro
sudo pacman -S --needed \
    base-devel \
    gcc \
    gdb \
    valgrind \
    clang \
    bubblewrap \
    typst \
    graphviz \
    python-pip \
    uv
```

```{tab-item} Fedora / RHEL
sudo dnf install -y \
    gcc \
    gcc-c++ \
    gdb \
    valgrind \
    clang-tools-extra \
    bubblewrap \
    typst \
    graphviz \
    python3-pip
```

```{tab-item} macOS (Homebrew)
brew install gcc gdb clang-format typst graphviz uv
```

```{tab-item} Windows (MSYS2 / WSL2)
# En WSL2 (Ubuntu): utilizar los paquetes de Ubuntu/Debian arriba.
# En MSYS2 MINGW64:
pacman -S --needed \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-gdb \
    mingw-w64-x86_64-clang-tools-extra
```
````

---

### 2.2 Métodos de Instalación de `holden`

Podés instalar `holden` mediante cualquiera de los siguientes métodos estándar:

````{tab-set}
```{tab-item} uv tool (Recomendado)
# Instalación aislada de alta velocidad con uv
uv tool install . --editable

# O instalar todo el ecosistema de herramientas de la cátedra en lote:
source ./install_tools.sh
```

```{tab-item} pip / venv
# Crear y activar un entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar en modo editable para desarrollo
pip install -e .
```

```{tab-item} pipx
# Instalación global aislada en tu PATH
pipx install --editable .
```
````

---

### 2.3 Autocompletado en la Shell

La interfaz CLI de `holden` cuenta con autocompletado nativo para comandos, flags y archivos. Para configurarlo permanentemente en tu shell:

````{code-block} bash
# Configuración automática en Bash / Zsh / Fish
holden --install-completion

# Para cargar el autocompletado en la sesión actual de inmediato:
source ./install_tools.sh
````

---

### 2.4 Verificación del Entorno con `doctor`

Toda herramienta del ecosistema cuenta con el subcomando unificado `doctor`. Ejecutalo para auditar el estado del entorno:

````{code-block} bash
holden doctor
````

#### Comprobaciones Ejecutadas por el Diagnóstico:
- **Compilador C**: Verifica disponibilidad de `gcc` o `clang` con soporte de estándares C11 y C23.
- **Depurador y Core Dumps**: Comprueba que `gdb` esté instalado y que `ulimit -c` permita generación de core dumps.
- **Herramientas de Memoria**: Valida la presencia de `valgrind` y librerías `libasan`/`libubsan`.
- **Formateo y Estilo**: Verifica el binario `clang-format` (versión 16+).
- **Sandboxing de Kernel**: Audita permisos no privilegiados de `bwrap` (Bubblewrap namespaces).
- **Generador de Tipografía y Documentos**: Comprueba `typst` ($\ge 0.11$) y `dot` (Graphviz).

#### Matriz de Resolución de Problemas:

| Síntoma / Alerta de `doctor` | Causa Raíz | Acción Correctiva |
| :--- | :--- | :--- |
| `❌ gcc / clang no encontrado` | Toolchain C faltante | Instalá `build-essential` o `base-devel`. |
| `❌ bwrap permisos insuficientes` | User namespaces desactivados | Habilitá `sysctl kernel.unprivileged_userns_clone=1`. |
| `❌ typst no disponible` | Motor de PDF faltante | Descargá Typst vía `cargo install typst-cli` o gestor de paquetes. |
| `❌ gdb no responde` | GDB sin interfaz MI/Python | Reinstalá `gdb` completo desde el repositorio oficial. |

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

