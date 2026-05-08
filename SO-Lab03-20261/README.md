# SO - Lab03 - 20261

## Equipo

* Rafael Angel Alemán Castillo. [rafael.aleman@udea.edu.co](mailto:rafael.aleman@udea.edu.co). CC. 1001560844
* Isabela Bedoya Gaviria. [isabela.bedoya@udea.edu.co](mailto:isabela.bedoya@udea.edu.co). CC. 1020106520

---

## Cómo ejecutar

### Requisitos previos

* Sistema operativo Linux (o WSL en Windows).
* GCC instalado (`gcc --version`).
* Valgrind instalado (`sudo apt install valgrind`).
* Python 3 con matplotlib (para generar diagramas): `pip install matplotlib`.

### Estructura del proyecto

```plain text
SO-Lab03-20261/
├── README.md
├── QUESTIONS.md
├── 01-address-space/
│   ├── mem_map.c
│   └── test.sh
├── 02-memory-api/
│   ├── heap_demo.c
│   ├── buggy_mem.c
│   ├── buggy_mem_fixed.c
│   └── test.sh
├── 03-base-bounds/
│   ├── base_bounds.c
│   └── test.sh
├── 04-segmentation/
│   ├── segmentation_calc.md
│   └── diagrams/
│       └── fragmentation.py
└── 05-paging/
├── paging_calc.md
├── paging_sim.c
└── test.sh
```

---

## Instrucciones de ejecución

### 1. Espacio de direcciones (01-address-space)

```bash
cd 01-address-space
chmod +x test.sh
./test.sh
```

El script compila `mem_map.c`, ejecuta el programa, captura los mapas de memoria desde `/proc/[pid]/maps` y `pmap`, y compara dos procesos simultáneos.

---

### 2. API de Memoria (02-memory-api)

```bash
cd 02-memory-api
chmod +x test.sh
./test.sh
```

El script:

- Compila y ejecuta `heap_demo.c` con Valgrind
- Compila y ejecuta `buggy_mem.c` (detecta 3 errores)
- Compila y ejecuta `buggy_mem_fixed.c` (versión corregida, sin errores)

---

### 3. Base & Bounds (03-base-bounds)

```bash
cd 03-base-bounds
chmod +x test.sh
./test.sh
```

El script compila y ejecuta el simulador de traducción base & bounds, verifica excepciones y genera una versión extendida con un Proceso C adicional.

---

### 4. Segmentación (04-segmentation)

### Cálculos manuales:

```bash
cd 04-segmentation
cat segmentation_calc.md
```

### Generar diagrama de fragmentación:

```bash
cd diagrams
python3 fragmentation.py
```

Esto genera `fragmentacion_externa.png` mostrando cómo surge la fragmentación externa.

---

### 5. Paginación (05-paging)

### Cálculos de la tabla de páginas:

```bash
cd 05-paging
cat paging_calc.md
```

### Ejecutar simulador:

```bash
chmod +x test.sh
./test.sh
```

El script compila `paging_sim.c`, ejecuta traducciones, verifica page faults y analiza el overhead de acceso a memoria.

## Documentación

### Sección 1: Espacio de Direcciones

### `mem_map.c`

Programa que imprime las direcciones virtuales de diferentes regiones de memoria:

| Variable/Función | Ubicación | Descripción |
| --- | --- | --- |
| `main` | Segmento text | Código ejecutable del programa |
| `global_var` | Segmento .data | Variable global inicializada |
| `local_var` | Stack | Variable local en la pila |
| `heap_var` | Heap | Memoria asignada dinámicamente |

**Proceso:**

1. Imprime el PID del proceso
2. Imprime direcciones virtuales de cada región
3. Espera ENTER para permitir inspección con `/proc/[pid]/maps`

---

### Sección 2: API de Memoria

### `heap_demo.c`

Demuestra el uso correcto de `malloc()`, `realloc()` y `free()`.

| Función | Descripción |
| --- | --- |
| `malloc(n * sizeof(int))` | Asigna memoria para 10 enteros |
| `realloc(arr, 20 * sizeof(int))` | Redimensiona el arreglo a 20 enteros |
| `free(arr)` | Libera la memoria asignada |

**Validación:** El programa no debe tener fugas de memoria según Valgrind.

---

### `buggy_mem.c` (con errores intencionales)

Contiene 3 errores clásicos para detectar con Valgrind:

| Error | Línea | Descripción |
| --- | --- | --- |
| **Buffer overflow** | `for (int i = 0; i <= 5; i++)` | Accede a `p[5]` cuando solo se asignaron 5 elementos (índices 0-4) |
| **Memory leak** | `char *q = malloc(100);` sin `free(q)` | Nunca se libera la memoria de `q` |
| **Use-after-free** | `printf("p[0] = %d\n", p[0]);` después de `free(p)` | Accede a memoria ya liberada |

---

### `buggy_mem_fixed.c` (versión corregida)

**Correcciones aplicadas:**

1. Cambio `i <= 5` por `i < 5` (elimina buffer overflow)
2. Agregado `free(q)` antes del return (elimina memory leak)
3. Movido `printf("p[0]...")` antes de `free(p)` (elimina use-after-free)

---

### Sección 3: Base & Bounds

### `base_bounds.c`

Simulador de traducción de direcciones con esquema base & bounds.

| Función | Descripción |
| --- | --- |
| `int traducir(Registro r, int va)` | Traduce VA → PA usando fórmula `PA = base + VA` si `0 ≤ VA < bounds`. Retorna -1 si viola bounds. |
| `main()` | Define dos procesos (A y B) con diferentes registros base/bounds y traduce un conjunto de VAs. |

**Fórmula de traducción:**

```
SI (0 ≤ VA < bounds):
    PA = base + VA
SINO:
    EXCEPCIÓN (Segmentation Fault)
```

---

### Sección 4: Segmentación

Ver archivo completo: [`04-segmentation/segmentation_calc.md`](https://claude.ai/chat/04-segmentation/segmentation_calc.md)

**Conceptos clave:**

- Tabla de segmentos con base, tamaño, dirección de crecimiento y selector
- Segmentos de crecimiento positivo (Code, Heap): `PA = Base + Offset`
- Segmentos de crecimiento negativo (Stack): `PA = Base - (Tamaño_máx - Offset)`
- Fragmentación externa: huecos no contiguos en memoria física

---

### Sección 5: Paginación

Ver archivo completo: [`05-paging/paging_calc.md`](https://claude.ai/chat/05-paging/paging_calc.md)

### `paging_sim.c`

Simulador de paginación con páginas de 16 bytes.

| Constante | Valor | Descripción |
| --- | --- | --- |
| `PAGE_BITS` | 4 | Bits para offset (2^4 = 16 bytes por página) |
| `VA_BITS` | 8 | Espacio virtual de 8 bits (256 bytes) |
| `NUM_PAGES` | 16 | Número de páginas virtuales |

**Tabla de páginas:**

```c
int page_table[16] = {
    3, -1, 7, 2, -1, 1, -1, 5,
    -1, -1, 4, -1, 6, -1, 0, -1
};
```

- Valor ≥ 0: PFN (marco físico)
- Valor -1: Página no presente (PAGE FAULT)

**Fórmula de traducción:**

```
VPN = VA >> PAGE_BITS
Offset = VA & (PAGE_SIZE - 1)
PFN = page_table[VPN]
PA = (PFN << PAGE_BITS) | Offset
```

---

## Pruebas

Cada sección tiene su propio script de pruebas `test.sh` que:

1. **Compila** el programa con flags de debugging (`g`, `Wall`)
2. **Ejecuta** el programa (algunos con Valgrind)
3. **Verifica** salidas esperadas
4. **Genera** archivos de log con resultados

### Ejemplo de salida esperada (02-memory-api):

```
=== Ejecutando buggy_mem con Valgrind ===
...
✘ ERROR 1 detectado: Buffer overflow (Invalid write)
✘ ERROR 2 detectado: Memory leak (100 bytes de q)
✘ ERROR 3 detectado: Use-after-free (Invalid read)

Errores detectados: 3/3

=== Ejecutando buggy_mem_fixed con Valgrind ===
...
✓ buggy_mem_fixed: Sin errores ni fugas
```

---

## Problemas

[Documenta aquí cualquier problema encontrado durante el desarrollo]

---

## Video

[Enlace al video de 10 minutos sustentando el desarrollo]

---

## Manifiesto de transparencia

Se utilizó IA generativa (Claude Sonnet 4.6) en los siguientes puntos del desarrollo:

- [Lista los puntos específicos donde se usó IA]
