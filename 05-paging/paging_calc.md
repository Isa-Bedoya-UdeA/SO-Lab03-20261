# Cálculos de Paginación

## Parámetros del Sistema

| Parámetro | Valor |
| --- | --- |
| Espacio virtual | 32 bits |
| Tamaño de página | 4 KB = 2^12 bytes |
| Espacio físico | 20 bits (1 MB) |
| Tamaño de PTE | 4 bytes |

---

## Pregunta 1: ¿Cuántos bits para VPN y offset?

### Cálculo del offset:

El offset identifica la posición dentro de una página.

Tamaño de página = 4 KB = 2^12 bytes
Offset = 12 bits

### Cálculo del VPN:

El VPN identifica qué página virtual.
Espacio virtual = 32 bits
VPN = 32 - 12 = 20 bits

**Respuesta:**
- **VPN: 20 bits**
- **Offset: 12 bits**

### Descomposición de una VA de 32 bits:

┌────────────────────┬─────────────┐
│        VPN         │   Offset    │
│      20 bits       │   12 bits   │
└────────────────────┴─────────────┘

---

## Pregunta 2: ¿Cuántas entradas tiene la tabla de páginas?

Número de entradas = 2^VPN = 2^20 = 1,048,576 entradas

Cada proceso puede direccionar hasta **1 millón de páginas virtuales** de 4 KB cada una.

**Respuesta:** **1,048,576 entradas (PTEs)**

---

## Pregunta 3: ¿Cuánta memoria ocupa la tabla de páginas?

Memoria total = Número de entradas × Tamaño de PTE
Memoria total = 1,048,576 × 4 bytes
Memoria total = 4,194,304 bytes = 4 MB

**Respuesta:** **4 MB por proceso**

### ¿Es razonable este tamaño?

**NO es razonable** para sistemas con cientos de procesos:

- **100 procesos** → 400 MB solo en tablas de páginas
- **1000 procesos** → 4 GB solo en tablas de páginas

**Problemas:**
- Consume demasiada memoria física
- La mayoría de entradas están vacías (no todos los procesos usan 4 GB completos)

**Soluciones:**
- **Tablas de páginas multinivel** (solo asignar niveles superiores cuando sea necesario)
- **TLB (Translation Lookaside Buffer):** caché de hardware para traducciones frecuentes
- **Páginas de mayor tamaño** (huge pages de 2 MB o 1 GB)

---

## Pregunta 4: ¿Cuántos bits necesita el PFN? ¿Qué almacenan los bits restantes?

### Cálculo de bits para PFN:

Espacio físico = 20 bits = 1 MB
Tamaño de página = 4 KB = 2^12 bytes

Número de marcos físicos = Espacio físico / Tamaño de página
= 2^20 / 2^12
= 2^8 = 256 marcos

Bits necesarios = log₂(256) = 8 bits

**Respuesta:** **PFN necesita 8 bits**

### Estructura de una PTE (32 bits total):

┌─────────┬──────────────────────────────┐
│   PFN   │      Bits de control         │
│ 8 bits  │         24 bits              │
└─────────┴──────────────────────────────┘

### 3 Bits de control principales:

| Bit | Nombre    | Función |
|-----|-----------|---------|
| **V** | Valid     | ¿La página está en memoria física? (1 = sí, 0 = page fault) |
| **R** | Reference | ¿Se ha accedido recientemente? (para algoritmos de reemplazo LRU) |
| **D** | Dirty     | ¿Se ha modificado la página? (si es 1, hay que escribir a disco antes de reemplazar) |
| **P** | Protection | Permisos: read, write, execute (generalmente 3 bits: rwx) |

**Otros bits posibles:**
- **User/Supervisor:** ¿Accesible desde modo usuario?
- **Cache-disable:** ¿Deshabilitar caché para E/S mapeada en memoria?
- **Global:** ¿Compartida entre procesos (no invalidar en cambio de contexto)?

**Ejemplo de PTE:**

PFN=0x42, Valid=1, Dirty=0, Referenced=1, Protection=r-x

┌──────────┬─┬─┬─┬───────┬─────────────────┐
│ 01000010 │1│0│1│ 101   │   (reservado)   │
│   PFN    │V│D│R│  rwx  │                 │
└──────────┴─┴─┴─┴───────┴─────────────────┘

---

## Resumen de Respuestas

1. **VPN:** 20 bits | **Offset:** 12 bits
2. **Entradas:** 1,048,576 PTEs
3. **Memoria:** 4 MB por tabla (NO razonable para muchos procesos)
4. **PFN:** 8 bits | **Bits de control:** Valid, Dirty, Referenced, Protection (rwx), etc.

---

## Comparación: Tabla de Páginas vs Tabla de Segmentos

| Característica | Segmentación | Paginación |
|----------------|--------------|------------|
| Tamaño de bloques | Variable (según lógica del programa) | Fijo (4 KB típico) |
| Fragmentación externa | ✅ Sí (problema grave) | ❌ No |
| Fragmentación interna | ❌ No | ✅ Sí (< 1 página por segmento) |
| Tamaño de tabla | Pequeña (pocos segmentos) | Grande (millones de entradas) |
| Protección | Por segmento lógico | Por página (menos granular) |
| Complejidad | Baja | Alta (pero más eficiente) |

**Sistemas modernos:** Combinan ambos (segmentación + paginación) o usan solo paginación multinivel.
