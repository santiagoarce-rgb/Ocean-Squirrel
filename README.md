# Ocean-Squirrel — SpongeBob: Truth or Square (PSP) Reverse Engineering

Proyecto de análisis estático, descompilación y documentación del motor de *SpongeBob SquarePants: Truth or Square* (PSP) utilizando **Ghidra** y **qwen2.5-coder localmente gracias a Ollama** via **GhidrAssist**.

Legal Disclaimer
This repository does NOT contain any copyrighted assets, game ROMs, or original binaries from SpongeBob SquarePants: Truth or Square.

This project is strictly for educational, research, and reverse-engineering purposes to document the inner mechanics of the game engine. All code in this repository is reconstructed via static analysis. All trademarks belong to their respective owners (Nickelodeon / Paramount / THQ Wireless / Heavy Iron Studios).

##  Entorno y Configuración
- **Descompilador:** Ghidra 12.1 (CachyOS / Arch Linux)
- **Plugin:** GhidrAssist v12.1
- **LLM Provider:** DeepSeek API (`deepseek-coder` / `deepseek-chat`)
- **Arquitectura:** MIPS Allegrex (Sony PSP)
- **Base Memory Address:** `0x08804000` (RAM real de ejecutable PSP)

---

##  Progreso de Funciones Documentadas
## 📍 Mapa de Funciones y Símbolos Descompilados

| Dirección RAM | Nombre | Categoría | Descripción |
| :--- | :--- | :--- | :--- |
| `0x0880452c` | `engine_shutdown` | Core / System | Rutina de desinicialización global. Libera punteros globales, invoca destructores y llama a `heap_free`. |
| `0x08804744` | `Engine_destructor` | Core / C++ | Destructor escalar `Engine::~Engine()`. Maneja el cambio de VTables y liberación de memoria de la clase principal. |
| `0x088f628c` | `init_ui_widget_5slot` | UI / Subsystem | Inicializa componentes gráficos del HUD/Menú iterando sobre un arreglo de 5 elementos (140 bytes c/u). |
| `0x0826ff00` | `vtable_Engine_Derived` | Data / VTable | Tabla de métodos virtuales de la clase derivada principal del motor. |
| `0x08270090` | `vtable_Engine_Base` | Data / VTable | Tabla de métodos virtuales de la clase base del motor. |
| `0x0005b748` | `g_ResourceManager` | Global / Pointer | Puntero Singleton al gestor global de recursos/assets. |

---

##  Arquitectura y Patrones del Motor

### Patrones de Compilación e Infraestructura C++

* **Destrucción de Clases (VTable Swapping):** Las clases del motor restauran explícitamente sus VTables a la versión base durante el flujo de destrucción (`0x0826ff00` -> `0x08270090`) antes de llamar a la rutina de liberación de memoria (`heap_free`/`delete`).
* **Singletons con Lazy Initialization:** Los gestores globales (como `g_ResourceManager`) se instancian bajo demanda. El código valida si el puntero es `NULL`, reserva memoria mediante `heap_alloc` (offset `0x9c`) e invoca el constructor correspondiente.
* **Tratamiento de Assertions (`halt_baddata`):** Las comprobaciones de punteros nulos contienen trampas de interrupción MIPS (`teq`/`break`) que cortan el flujo de descompilación en los bloques de manejo de errores (*error paths*).
---

##  Estructuras C Reconstruidas

### `StreamObject`
```c
typedef struct StreamObject {
    void **vtable;             // Offset 0x00: Tabla de métodos virtuales
    uint8_t padding[376];      // Offset 0x04 - 0x17B: Datos internos
    uint32_t dest_buffer[29];  // Offset 0x17C (0x5f * 4): Buffer de entrada (116 bytes)
} StreamObject;

