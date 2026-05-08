# Respuestas — Laboratorio 3: Gestión de Memoria

---

## Sección 1 — Espacio de Direcciones

### 1.3 Exploración de /proc/[pid]/maps

**1. Regiones text, heap y stack — permisos y diferencias**

| Región | Permisos | Significado |
|--------|----------|-------------|
| text   | `r-xp`   | Solo lectura y ejecución, privada. El código no debe modificarse en ejecución. La ausencia de `w` previene que el proceso sobrescriba sus propias instrucciones. |
| heap   | `rw-p`   | Lectura y escritura, privada. El heap crece dinámicamente con malloc; necesita escritura pero nunca se ejecuta código desde allí. |
| stack  | `rw-p`   | Lectura y escritura, privada. Almacena variables locales y marcos de llamada; tampoco debe ser ejecutable (protección contra stack overflow exploits). |

Los permisos difieren porque cada región tiene una responsabilidad distinta. Esta separación implementa el principio W^X (Write XOR Execute): la memoria ejecutable no se puede escribir, y la memoria escribible no se puede ejecutar. Es fundamental para la seguridad del sistema.

**2. Comparación de direcciones impresas con rangos de /proc/maps**

Ejemplo de salida de `mem_map`:
```
PID del proceso  : 1234
Dir. codigo (main): 0x555555555189   → región text  (r-xp)
Dir. global_var  : 0x55555555800c   → región .data  (rw-p, datos globales inicializados)
Dir. local_var   : 0x7fffffffecfc   → stack         (rw-p, dirección alta del espacio virtual)
Dir. heap_var    : 0x55555576b2a0   → heap          (rw-p, por encima del BSS)
```

`main` cae en el segmento de código (text). `global_var` cae en el segmento `.data` (variables globales inicializadas). `local_var` está en la pila (stack), cuya dirección es alta en el espacio virtual (cercana a `0x7fff...`). `heap_var` está en el heap, cuya dirección está por encima del BSS y crece hacia arriba.

**3. Otras regiones en el mapa**

- **libc.so**: La biblioteca estándar de C mapeada en el espacio del proceso. Contiene las implementaciones de `printf`, `malloc`, etc. Se mapea con permisos `r-xp` (código) y `rw-p` (datos). Permite que múltiples procesos compartan el mismo código de libc en memoria física (páginas compartidas de solo lectura), reduciendo el uso de RAM.

- **[vdso]** (Virtual Dynamic Shared Object): Región especial que el kernel mapea en cada proceso. Contiene funciones de sistema de alta frecuencia (`gettimeofday`, `clock_gettime`) implementadas en modo usuario para evitar el costoso cambio de contexto al kernel. Tiene permisos `r-xp`.

- **[vsyscall]**: Mecanismo más antiguo (pre-vdso) con propósito similar, pero mapeado en una dirección fija (`0xffffffffff600000`) en todos los procesos. En kernels modernos es emulado por razones de seguridad, ya que ASLR no puede aleatorizarlo al ser una dirección fija.

- **[stack]**: La pila del proceso, con permisos `rw-p`. Se ubica en las direcciones altas del espacio virtual y crece hacia abajo.

- **ld-linux.so** (dynamic linker): El enlazador dinámico que carga las bibliotecas compartidas al inicio del proceso.

**4. ¿Son las direcciones virtuales iguales a las físicas?**

No. Las direcciones impresas por `mem_map` son **direcciones virtuales**, no físicas. Según el concepto de *address space* de OSTEP (capítulo vm-intro), el SO crea para cada proceso la ilusión de un espacio de memoria privado y exclusivo. El hardware de traducción de memoria (MMU) convierte cada dirección virtual en una física en el momento del acceso, usando la tabla de páginas del proceso. Por eso dos procesos distintos pueden tener la misma dirección virtual (ej. `0x555555555189` para `main`) sin conflicto, porque sus traducciones apuntan a marcos físicos diferentes. La dirección física real solo es visible desde el kernel o mediante `/proc/<pid>/pagemap`.

---

### 1.4 Comparar espacios de dos procesos simultáneos

**1. ¿Son las mismas direcciones virtuales?**

Sí. Al ejecutar dos instancias de `mem_map` simultáneamente, ambas imprimen direcciones virtuales idénticas (o muy similares) para `main`, `global_var` y `heap_var`. Esto demuestra que el **aislamiento del espacio de direcciones** es completo: cada proceso vive en su propio espacio virtual privado. El SO mantiene una tabla de páginas separada para cada proceso, de modo que la misma dirección virtual en el Proceso 1 apunta a un marco físico diferente que en el Proceso 2. Ambos procesos creen tener la memoria para ellos solos.

**2. ¿Podría el Proceso A leer o modificar la variable global del Proceso B?**

No. Aunque las direcciones virtuales sean numéricamente iguales, están en espacios de direcciones separados. Cuando el Proceso A usa la dirección `0x55555555800c`, la MMU la traduce al marco físico asignado a A; cuando B usa la misma dirección, la MMU la traduce al marco físico asignado a B. No hay ningún mecanismo por el cual A pueda referenciar el espacio virtual de B directamente. Para comunicarse, los procesos deben usar mecanismos explícitos del SO como memoria compartida (`mmap` con `MAP_SHARED`), pipes o sockets. Intentar acceder a la VA de otro proceso simplemente accede a la propia memoria del proceso o genera un segfault.

---

## Sección 2 — API de Memoria

### 2.2 Uso correcto de malloc y free

**1. Salida completa de Valgrind para heap_demo**

```
==683== Memcheck, a memory error detector
==683== Command: ./heap_demo
Arreglo original: 0 1 4 9 16 25 36 49 64 81
Arreglo ampliado: 0 1 4 9 16 25 36 49 64 81 100 121 144 169 196 225 256 289 324 361
==683== HEAP SUMMARY:
==683==     in use at exit: 0 bytes in 0 blocks
==683==   total heap usage: 3 allocs, 3 frees, 4,216 bytes allocated
==683== All heap blocks were freed -- no leaks are possible
==683== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

Valgrind **no reporta errores ni fugas**. El mensaje `"All heap blocks were freed"` significa que cada bloque asignado con `malloc`/`realloc` fue correctamente liberado con `free` antes de que el programa terminara. El contador muestra 3 allocs y 3 frees con balance perfecto. Esto indica una gestión correcta del heap.

**2. ¿Por qué usar sizeof(int) en lugar de 4?**

Porque el tamaño de `int` no es universalmente 4 bytes. En arquitecturas de 16 bits (sistemas embebidos) `int` puede ser 2 bytes. Al escribir `malloc(n * sizeof(int))` el código es **portable**: se calcula el tamaño correcto en cualquier plataforma donde se compile. Usar el literal `4` crearía un bug silencioso al compilar en arquitecturas donde `sizeof(int) != 4`.

**3. ¿Qué devuelve malloc cuando no hay memoria disponible?**

`malloc` devuelve `NULL`. Es crítico verificarlo antes de usar el puntero porque si se intenta desreferenciar `NULL` (ej. `arr[0] = 1` cuando `arr == NULL`), se produce un segmentation fault inmediato o, peor aún, se escribe en una dirección arbitraria causando corrupción silenciosa de datos. En sistemas embebidos o de memoria limitada la falta de memoria es un escenario real, y la verificación es una práctica defensiva estándar.

---

### 2.4 Identificar y corregir errores de memoria

**1. Mensajes de Valgrind para buggy_mem y correspondencia con errores**

```
==684== Invalid write of size 4
==684==    at 0x1091E3: main (buggy_mem.c:10)
==684==  Address 0x4a7c054 is 0 bytes after a block of size 20 alloc'd
```
→ **ERROR 1: Buffer overflow** — El bucle usa `i <= 5` en lugar de `i < 5`. Se asignaron 5 enteros (20 bytes), pero se escribe en el índice 5 (`p[5]`), que está fuera del bloque. Valgrind detecta "Invalid write" en la dirección justo después del bloque.

```
==684== Invalid read of size 4
==684==    at 0x109231: main (buggy_mem.c:19)
==684==  Address 0x4a7c040 is 0 bytes inside a block of size 20 free'd
```
→ **ERROR 3: Use-after-free** — Se accede a `p[0]` después de llamar `free(p)`. Valgrind reporta "Invalid read" indicando que la dirección pertenece a un bloque ya liberado.

```
==684== 100 bytes in 1 blocks are definitely lost in loss record 1 of 1
==684==    at 0x4846828: malloc (buggy_mem.c:13)
```
→ **ERROR 2: Memory leak** — El puntero `q` nunca se libera con `free(q)`. Valgrind lo reporta en el LEAK SUMMARY como "definitely lost". Resumen: `ERROR SUMMARY: 3 errors from 3 contexts`.

**2. buggy_mem_fixed.c — verificación con Valgrind**

Correcciones aplicadas: (1) `i <= 5` → `i < 5`, (2) agregar `free(q)` antes del return, (3) leer `p[0]` **antes** de `free(p)`.

```
==685== Command: ./buggy_mem_fixed
hola mundo
p[0] antes de free = 0
==685== HEAP SUMMARY:
==685==     in use at exit: 0 bytes in 0 blocks
==685==   total heap usage: 3 allocs, 3 frees, 4,216 bytes allocated
==685== All heap blocks were freed -- no leaks are possible
==685== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

**3. Consecuencias de use-after-free en sistemas reales**

- **Estabilidad**: La memoria liberada puede ser reasignada a otro objeto. Si el código antiguo escribe en ella, corrompe datos del nuevo objeto produciendo comportamiento impredecible: crashes, resultados incorrectos o corrupción silenciosa que se manifiesta mucho más tarde.

- **Seguridad**: Es una de las vulnerabilidades más explotadas (CVE frecuente en navegadores, kernels y VMs). Un atacante puede controlar qué dato se asigna en la memoria liberada. Si logra colocar allí un objeto con un puntero a función, puede redirigir la ejecución hacia código malicioso (heap spray + use-after-free). Vulnerabilidades de este tipo han permitido escapes de sandbox en Chrome, Firefox y el kernel Linux.

---

## Sección 3 — Traducción de direcciones: Base & Bounds

### 3.2 Base & Bounds — Análisis

**1. Salida completa y análisis de VA=64 y VA=100 en Proceso A**

```
--- Proceso A (base=32, bounds=64) ---
  VA=  0  ->  PA= 32
  VA= 10  ->  PA= 42
  VA= 63  ->  PA= 95
  [EXCEPCION] VA=64 viola bounds=64
  [EXCEPCION] VA=100 viola bounds=64
--- Proceso B (base=128, bounds=80) ---
  VA=  0  ->  PA=128
  VA= 10  ->  PA=138
  VA= 63  ->  PA=191
  VA= 64  ->  PA=192
  [EXCEPCION] VA=100 viola bounds=80
--- Proceso C (base=0, bounds=32) ---
  VA=  0  ->  PA=  0
  VA= 10  ->  PA= 10
  [EXCEPCION] VA=63 viola bounds=32
  [EXCEPCION] VA=64 viola bounds=32
  [EXCEPCION] VA=100 viola bounds=32
```

`VA=64` viola bounds en Proceso A porque bounds=64 y las VAs válidas son `[0, 63]`. Ante una excepción de este tipo, el SO real ejecutaría un manejador de faults: envía la señal `SIGSEGV` al proceso (segmentation fault), lo termina y libera sus recursos.

**2. Proceso C (base=0, bounds=32) — ¿puede A acceder a las direcciones de C?**

No directamente. Cuando A usa VA=0, la MMU lo traduce a PA=32 (su propio espacio físico), no a PA=0 (el espacio de C). El mecanismo base & bounds garantiza que cada proceso solo accede a sus propias PA. Para que A viera la memoria de C, el SO debería habilitarlo explícitamente (memoria compartida), lo cual está fuera del modelo base & bounds básico.

**3. Limitación principal de base & bounds que motiva la segmentación**

El esquema trata el espacio de direcciones como un único bloque contiguo en memoria física. Esto genera dos problemas: (1) **Fragmentación interna** — si un proceso solo usa 20 KB de un espacio de 64 KB asignado, los 44 KB restantes están desperdiciados (reservados pero no utilizados); (2) **No permite separar regiones** — no es posible dar permisos distintos a código, heap y stack, ni compartir código entre procesos (ej. libc). La segmentación resuelve esto dividiendo el espacio en segmentos lógicos, cada uno con su propio par base/bounds y permisos.

---

## Sección 4 — Segmentación

### 4.1 Traducción manual con tabla de segmentos

**Parámetros:** espacio de 14 bits = 2 bits selector + 12 bits offset.

| Segmento | Base (PA) | Tamaño | Crece    | Selector |
|----------|-----------|--------|----------|----------|
| Code     | 0x4000    | 2 KB   | positivo | 00       |
| Heap     | 0x6000    | 3 KB   | positivo | 01       |
| Stack    | 0x2800    | 2 KB   | negativo | 11       |

**Cálculos paso a paso:**

**VA = 0x03A0 → selector=00, offset=0x3A0=928**
- Segmento: Code (base=0x4000, tamaño=2048 B)
- Validación: 928 < 2048 ✓
- PA = 0x4000 + 0x3A0 = **0x43A0**

**VA = 0x1800 → selector=01, offset=0x800=2048**
- Segmento: Heap (base=0x6000, tamaño=3072 B)
- Validación: 2048 < 3072 ✓
- PA = 0x6000 + 0x800 = **0x6800**

**VA = 0x3C00 → selector=11, offset=0xC00=3072**
- Segmento: Stack (base=0x2800, tamaño=2048 B, crece negativo)
- Para stack negativo: desplazamiento = offset - tamaño_máximo_selector = 0xC00 - 0x1000 = -0x400
- PA = 0x2800 + (-0x400) = 0x2800 - 0x400 = **0x2400**
- Validación: |desplazamiento| = 1024 ≤ 2048 ✓

**VA = 0x0C00 → selector=00, offset=0xC00=3072**
- Segmento: Code (base=0x4000, tamaño=2048 B)
- Validación: 3072 ≥ 2048 ✗
- **EXCEPCIÓN: offset fuera de bounds del segmento Code**

**VA = 0x2200 → selector=10**
- El selector `10` no corresponde a ningún segmento definido (solo existen 00, 01, 11).
- **EXCEPCIÓN: selector inválido**

**Tabla completa:**

| VA (hex) | Selector | Offset | Segmento | PA o Excepción |
|----------|----------|--------|----------|----------------|
| 0x03A0   | 00       | 0x3A0  | Code     | 0x43A0 |
| 0x1800   | 01       | 0x800  | Heap     | 0x6800 |
| 0x3C00   | 11       | 0xC00  | Stack    | 0x2400 |
| 0x0C00   | 00       | 0xC00  | Code     | EXCEPCIÓN (offset ≥ bounds) |
| 0x2200   | 10       | —      | ???      | EXCEPCIÓN (selector inválido) |

**2. ¿Por qué el Stack crece en dirección negativa? Ajuste en la fórmula**

El stack crece hacia abajo porque las llamadas a función apilan datos desde las direcciones más altas hacia las más bajas. Esto permite que stack y heap crezcan en direcciones opuestas dentro del mismo espacio virtual, maximizando el uso del espacio disponible sin colisionar hasta agotar la memoria.

Para el stack negativo la fórmula se ajusta: en lugar de `PA = base + offset`, se usa `PA = base + (offset - tamaño_máximo_del_segmento)`. Esto refleja que el stack "indexa hacia atrás" desde su tope.

**3. Ventaja de segmentación frente a base & bounds**

Con base & bounds, todo el espacio virtual ocupa un único bloque contiguo en RAM, desperdiciando el espacio no usado entre heap y stack. Con segmentación, cada segmento ocupa en RAM exactamente lo que usa: el código en un lugar, el heap en otro, el stack en otro. No se reserva espacio entre segmentos. Además, el código puede compartirse entre procesos que ejecutan el mismo programa, reduciendo el uso total de RAM.

**4. Fragmentación externa con segmentación**

La **fragmentación externa** ocurre cuando hay suficiente memoria libre total pero no hay un bloque contiguo suficientemente grande para una solicitud, porque la memoria libre está dividida en huecos pequeños entre segmentos activos.

Surge con segmentación porque los segmentos tienen tamaños variables: al asignar y liberar segmentos de distintos tamaños quedan huecos entre los segmentos activos.

**Diagrama:**
```
Memoria física:
┌─────────────┬──────┬────────────┬───────┬──────────────┐
│ Seg A (50K) │ 10K  │ Seg B (80K)│  5K   │ Seg C (40K)  │
│  [en uso]   │LIBRE │  [en uso]  │ LIBRE │  [en uso]    │
└─────────────┴──────┴────────────┴───────┴──────────────┘

Memoria libre total: 10K + 5K = 15K
Nueva solicitud: malloc(12K) → FALLA (ningún hueco ≥ 12K contiguos)
```

---

## Sección 5 — Paginación

### 5.1 Cálculo de la tabla de páginas

**Sistema:** espacio virtual 32 bits, página 4 KB = 2¹², espacio físico 20 bits, PTE 4 bytes.

**1. Bits para VPN y offset**
- Offset = log₂(4096) = **12 bits** (bits bajos de la VA)
- VPN = 32 − 12 = **20 bits** (bits altos de la VA)

**2. Número de entradas en la tabla de páginas**

Entradas = 2²⁰ = **1 048 576 entradas** por proceso.

**3. Tamaño total de la tabla de páginas**

Tamaño = 2²⁰ × 4 bytes = **4 MB por proceso**.

Es considerable: con 100 procesos simultáneos, solo las tablas de páginas ocuparían 400 MB de RAM. Esto motiva el uso de tablas de páginas multinivel (x86-64 usa 4 niveles), que solo instancian las entradas realmente usadas, reduciendo drásticamente el uso de memoria para procesos con espacios de direcciones dispersos.

**4. Bits para PFN y bits de control**

- Espacio físico: 20 bits → PFN = 20 − 12 = **8 bits**
- PTE = 32 bits → bits de control = 32 − 8 = **24 bits disponibles**

Bits de control relevantes:
- **Valid (V)**: indica si la página virtual está mapeada. Si V=0 y se accede, ocurre un page fault.
- **Protection (R/W/X)**: controla permisos de lectura, escritura y ejecución. Implementa W^X.
- **Dirty (D)**: marca si la página fue modificada. Útil para saber si hay que escribirla al disco en swap-out.
- **Accessed (A)**: el hardware lo pone en 1 al acceder a la página. El SO lo usa para políticas de reemplazo (LRU aproximado).
- **Present (P)**: indica si la página está en RAM o fue swapped al disco.

---

### 5.3 Simulador de paginación — Análisis

**1. Salida completa del simulador**

```
VA                     VPN    Offset   PFN    PA
------------------------------------------------------------
VA=0x00  VPN= 0  Offset= 0  -> PFN= 3  PA=0x30
VA=0x0F  VPN= 0  Offset=15  -> PFN= 3  PA=0x3F
VA=0x20  VPN= 2  Offset= 0  -> PFN= 7  PA=0x70
VA=0x35  VPN= 3  Offset= 5  -> PFN= 2  PA=0x25
VA=0x10  VPN= 1  Offset= 0  -> PAGE FAULT (pagina no presente)
VA=0xA3  VPN=10  Offset= 3  -> PFN= 4  PA=0x43
VA=0xC8  VPN=12  Offset= 8  -> PFN= 6  PA=0x68
VA=0xF0  VPN=15  Offset= 0  -> PAGE FAULT (pagina no presente)
```

**2. VAs 0x10 y 0xF0 generan PAGE FAULT**

- `VA=0x10` → VPN=1 → `page_table[1] = -1` (página no presente).
- `VA=0xF0` → VPN=15 → `page_table[15] = -1` (página no presente).

Ante un page fault, el SO real: (1) recibe la interrupción de la MMU, (2) verifica si la VA es válida, (3) si es válida: busca la página en swap, la carga en un marco físico libre, actualiza la PTE y reintenta el acceso; (4) si es inválida: envía `SIGSEGV` al proceso.

**3. Accesos a memoria para un load con tabla de un nivel**

Una instrucción `load` requiere **2 accesos a memoria física**: (1) acceder a la tabla de páginas en RAM para obtener el PFN, (2) acceder al dato real en el marco físico. Esto dobla el costo de cada acceso. La solución de hardware es el **TLB**: una caché asociativa de traducciones recientes. Si la traducción está en el TLB (hit), se salta el acceso a la tabla de páginas y solo se hace 1 acceso. Los TLBs modernos tienen hit rates superiores al 99%.

**4. Ventaja de paginación sobre segmentación respecto a fragmentación**

La paginación **elimina la fragmentación externa**. Como todas las páginas y marcos tienen el mismo tamaño fijo, cualquier marco libre puede satisfacer cualquier solicitud de página; no quedan huecos inutilizables. En cambio, la segmentación usa bloques de tamaño variable, lo que inevitablemente genera huecos. La paginación solo tiene **fragmentación interna** acotada a menos de 1 página (< 4 KB) por región, lo cual es manejable.

---

## Sección 6 — Gestión de Espacio Libre

### 6.1 Simulación de estrategias de asignación

**Estado inicial:** 0x0100(100B), 0x0200(500B), 0x0400(200B), 0x0500(300B), 0x0700(600B)

**1. First Fit — resultado**

| Solicitud   | Bloque elegido | Razonamiento |
|-------------|---------------|--------------|
| malloc(212) | 0x0200 (500B) | Primer bloque ≥ 212; deja 288B libre en 0x02D4 |
| malloc(417) | 0x0700 (600B) | Primer bloque ≥ 417 (0x0200 solo tiene 288B); deja 183B libre en 0x08A1 |
| malloc(98)  | 0x0100 (100B) | Primer bloque ≥ 98; deja 2B libre en 0x0162 |
| malloc(426) | **FALLO**     | Bloques libres: 2B, 288B, 200B, 300B, 183B — ninguno ≥ 426B |

Lista libre tras first fit: `0x0162(2B), 0x02D4(288B), 0x0400(200B), 0x0500(300B), 0x08A1(183B)` — Total: 973B

**2. Best Fit — resultado**

| Solicitud   | Bloque elegido | Razonamiento |
|-------------|---------------|--------------|
| malloc(212) | 0x0500 (300B) | Más ajustado ≥ 212 (desperdicio: 88B) |
| malloc(417) | 0x0200 (500B) | Más ajustado ≥ 417 (desperdicio: 83B) |
| malloc(98)  | 0x0100 (100B) | Más ajustado ≥ 98 (desperdicio: 2B) |
| malloc(426) | 0x0700 (600B) | Único bloque ≥ 426B (desperdicio: 174B) |

Lista libre tras best fit: `0x0162(2B), 0x03A1(83B), 0x0400(200B), 0x05D4(88B), 0x08AA(174B)` — Total: 547B

**3. ¿Cuál estrategia genera más fragmentación externa?**

**First fit** generó más fragmentación en este caso concreto: dejó el bloque grande de 600B partido temprano y falló en la 4.ª solicitud. **Best fit** satisfizo las 4 solicitudes porque preservó el bloque grande para la solicitud grande. En general, best fit tiende a generar muchos residuos muy pequeños (fragmentos casi inutilizables), mientras que first fit es más rápido pero menos predecible. El resultado depende del patrón de solicitudes.

**4. ¿Qué es el coalescing?**

El **coalescing** fusiona bloques libres adyacentes en uno solo mayor. Sin coalescing:

```
Antes de free():
┌────────────┬──────────────┬─────────────┐
│ 120B LIBRE │ 100B EN USO  │ 150B LIBRE  │
└────────────┴──────────────┴─────────────┘

Después de free() sin coalescing:
┌────────────┬──────────────┬─────────────┐
│ 120B LIBRE │  100B LIBRE  │ 150B LIBRE  │  ← tres bloques separados
└────────────┴──────────────┴─────────────┘
malloc(250) → FALLA aunque hay 370B libres totales

Con coalescing:
┌─────────────────────────────────────────┐
│              370B LIBRE                 │  ← un solo bloque fusionado
└─────────────────────────────────────────┘
malloc(250) → ÉXITO
```

**5. Fragmentación interna y slab allocator**

La **fragmentación interna** ocurre cuando se asigna un bloque mayor que lo solicitado y el espacio sobrante dentro del bloque queda inutilizable. Ejemplo: se piden 5 bytes y se asigna un bloque de 8 bytes (por alineación); los 3 bytes sobrantes no se pueden usar para otra solicitud.

Con un **slab allocator**, la fragmentación interna aparece cuando los objetos son más pequeños que el slot fijo del slab. Por ejemplo, si el slab tiene slots de 64 bytes y se almacenan objetos de 48 bytes, cada slot desperdicia 16 bytes. Esta ineficiencia se acepta a cambio de evitar completamente la fragmentación externa y reducir el overhead del allocator.

---

### 6.3 Fragmentación en glibc — Análisis

**1. ¿Son consecutivas las direcciones? Patrón de separación**

Las direcciones son aproximadamente consecutivas (el heap crece hacia arriba) pero con una separación constante de **16 bytes de overhead** adicional por bloque:

```
malloc( 16) -> 0x...2b0
malloc( 32) -> 0x...2d0   separación = 32 = 16 (pedido) + 16 (header glibc)
malloc( 64) -> 0x...300   separación = 48 = 32 (pedido) + 16 (header glibc)
```

El overhead de 16 bytes corresponde al **header de glibc** que precede a cada bloque: almacena el tamaño del bloque y flags de estado (si el bloque anterior está libre, si fue obtenido con mmap). En sistemas de 64 bits ocupa exactamente 16 bytes (2 palabras de 8 bytes).

**2. ¿Tiene éxito malloc(1500) tras liberar índices pares?**

En nuestra ejecución: **sí tuvo éxito** (`malloc(1500) -> 0x...ec0 [EXITO]`). Esto ocurre porque glibc implementa coalescing automático: al liberar bloques adyacentes los fusiona. Además, cuando no hay un bloque libre suficientemente grande en la lista interna, glibc puede expandir el heap con `sbrk()` o `mmap()`, obteniendo memoria nueva del SO. Por eso en la práctica la fragmentación extrema es menos dramática con glibc que en un allocator naïve sin coalescing.

**3. Diferencia entre allocator de usuario y del kernel**

| Aspecto | malloc / glibc (usuario) | Buddy system + slab (kernel) |
|---------|--------------------------|------------------------------|
| Unidad mínima | 16 bytes (con header) | Página (4 KB) en buddy; objeto fijo en slab |
| Granularidad | Fina: desde 1 byte | Gruesa en buddy; fina en slab |
| Velocidad | Moderada (lista enlazada) | Muy rápida en slab (pool preconstruido) |
| Fragmentación | Externa posible; coalescing la mitiga | Buddy: interna (potencias de 2); slab: nula externa |
| Contexto | Espacio usuario, por proceso | Espacio kernel, global |

Existen dos niveles porque tienen propósitos distintos: el kernel gestiona páginas físicas y objetos propios del kernel con sus allocators especializados. El allocator de usuario divide esas páginas en objetos pequeños para los programas. Esta separación permite que glibc optimice la asignación fina sin involucrar al kernel en cada `malloc`.

---

## Sección 7 — TLBs

### 7.1 Localidad y TLB — Análisis

**1. Relación de lentitud (promedio de 3 ejecuciones)**

| Ejecución | Secuencial (ms) | Aleatorio (ms) | Factor |
|-----------|----------------|----------------|--------|
| Run 1     | 9.96           | 53.61          | 5.4×   |
| Run 2     | 9.11           | 49.24          | 5.4×   |
| Run 3     | 9.33           | 55.83          | 6.0×   |
| **Promedio** | **9.47 ms** | **52.89 ms** | **~5.6×** |

El acceso aleatorio fue aproximadamente **5.6 veces más lento** que el secuencial.

**2. Explicación con el modelo del TLB**

El arreglo ocupa 16 MB. Con páginas de 4 KB hay 4096 páginas distintas.

- **Acceso secuencial**: Se accede a `arr[0]`, `arr[1]`, ..., `arr[1023]` que están en la misma página. Solo el primer acceso genera un TLB miss; los 1023 siguientes son TLB hits. Hit rate ≈ 99.9%. El costo de traducción es casi nulo.

- **Acceso aleatorio**: Cada acceso toca una página diferente. El TLB se satura rápidamente y casi cada acceso genera un TLB miss, obligando a consultar la tabla de páginas en RAM. Cada acceso cuesta ~2 accesos a RAM en lugar de 1. El hit rate cae drásticamente.

**3. ¿Mejoraría o empeoraría con páginas de 64 KB?**

Con páginas de 64 KB cada entrada del TLB cubre 16× más memoria, por lo que el TLB puede cubrir más espacio con el mismo número de entradas y el número de misses en accesos aleatorios disminuiría. Sin embargo, **empeoraría** en otros aspectos: la fragmentación interna aumenta (si un proceso usa solo 1 KB en una página se desperdician 63 KB de RAM), y cada page fault es más costoso (hay que cargar 64 KB del disco en lugar de 4 KB). El tamaño de 4 KB es un compromiso histórico equilibrado para la mayoría de cargas de trabajo.

---

### 7.2 Comportamiento de los TLBs

**1. TLB de 64 entradas con páginas de 4 KB**

Cobertura = 64 × 4 KB = **256 KB** simultáneamente.

Para un proceso moderno típico (que puede usar cientos de MB o GB), 256 KB es completamente insuficiente. Sin embargo, gracias a la **localidad de referencia** (la mayoría de accesos se concentran en pocas páginas activas), los TLBs de 64 entradas alcanzan hit rates de 95–99% en cargas típicas. Para compensar, los procesadores modernos tienen TLBs multinivel (L1 TLB de 64 entradas muy rápido; L2 TLB de 512–4096 entradas más lento pero mucho más rápido que acceder a la tabla de páginas en RAM).

**2. TLB shootdown**

Un **TLB shootdown** ocurre en sistemas multiprocesador cuando un proceso modifica su tabla de páginas (al liberar memoria con `munmap` o al hacer copy-on-write) y necesita invalidar las entradas del TLB en **todos los núcleos** que podrían tener esa traducción cacheada.

El núcleo que modifica la tabla de páginas envía una **IPI** (Inter-Processor Interrupt) a todos los demás núcleos, obligándolos a invalidar las entradas afectadas y confirmar la invalidación antes de continuar. Es costoso porque: (1) interrumpe múltiples núcleos simultáneamente, (2) requiere sincronización (barrera), y (3) los TLBs invalidados generarán misses en los siguientes accesos. En sistemas con muchos núcleos (32, 64, 128) el costo escala linealmente. Es una razón por la que operaciones como `munmap` son lentas en sistemas con muchos hilos.

**3. TLB gestionado por hardware (x86) vs. por software (MIPS)**

| Aspecto | Hardware-managed (x86/CISC) | Software-managed (MIPS/RISC) |
|---------|-----------------------------|------------------------------|
| Quién maneja el miss | La MMU recorre automáticamente la tabla de páginas | El SO recibe una excepción y ejecuta código para cargar la traducción |
| Formato de tabla de páginas | Fijo (definido por el hardware x86) | Libre (el SO elige el formato) |
| Flexibilidad para el SO | Baja | **Alta** |
| Complejidad | Hardware complejo, SW simple | Hardware simple, SW complejo |
| Ejemplo | Intel/AMD x86-64 | MIPS R2000, Sun SPARC |

El TLB gestionado por **software (RISC)** ofrece mayor flexibilidad al diseñador del SO porque el hardware no asume ningún formato de tabla de páginas. Esto permite implementar estructuras más eficientes para espacios de 64 bits (como tablas invertidas con una entrada por marco físico en lugar de por página virtual). La desventaja es que el miss handler en software añade latencia y complejidad al kernel.
