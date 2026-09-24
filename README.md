# Ocean-Squirrel — SpongeBob: Truth or Square (PSP) Reverse Engineering

Proyecto de análisis estático, descompilación y documentación del motor de *SpongeBob SquarePants: Truth or Square* (PSP) utilizando **Ghidra** y **DeepSeek LLM** via **GhidrAssist**.

##  Entorno y Configuración
- **Descompilador:** Ghidra 12.1 (CachyOS / Arch Linux)
- **Plugin:** GhidrAssist v12.1
- **LLM Provider:** DeepSeek API (`deepseek-coder` / `deepseek-chat`)
- **Arquitectura:** MIPS Allegrex (Sony PSP)
- **Base Memory Address:** `0x08804000` (RAM real de ejecutable PSP)

---

##  Progreso de Funciones Documentadas

| Dirección Base | Nombre Asignado | Categoría | Descripción |
| :--- | :--- | :--- | :--- |
| `0x00000040` | `init_global_ctors` | Sistema / `.init` | Inicialización única de constructores globales C++ (`.ctors`). Controlada por el guardián `g_is_initialized`. |
| `0x08830bd0` | `parse_stream_chunk` | I/O / Stream | Lee bloques de 116 bytes (29 palabras) de un stream, actualiza punteros de desplazamiento e invoca un callback virtual. |

---

##  Estructuras C Reconstruidas

### `StreamObject`
```c
typedef struct StreamObject {
    void **vtable;             // Offset 0x00: Tabla de métodos virtuales
    uint8_t padding[376];      // Offset 0x04 - 0x17B: Datos internos
    uint32_t dest_buffer[29];  // Offset 0x17C (0x5f * 4): Buffer de entrada (116 bytes)
} StreamObject;
