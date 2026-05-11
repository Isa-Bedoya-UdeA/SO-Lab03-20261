# Laboratorio 3 — Gestión de Memoria

> Laboratorio de Sistemas Operativos · Universidad de Antioquia

---

## Integrantes

| Nombre completo | Correo | Documento |
| --------------- | ------ | --------- |
| Rafael Alemán | [rafael.aleman@udea.edu.co](rafael.aleman@udea.edu.co) | C.C. 1001560844 |
| Isabela Bedoya | [isabela.bedoya@udea.edu.co](isabela.bedoya@udea.edu.co) | C.C. 1020106520 |

---

## Estructura del repositorio

```plain text
SO-Lab03-20261/
├── README.md                  ← Este informe
├── QUESTIONS.md               ← Respuestas a todas las preguntas del enunciado
├── 01-address-space/
│   ├── mem_map.c              ← Programa base que imprime direcciones virtuales
│   └── test.sh                ← Script de prueba
├── 02-memory-api/
│   ├── heap_demo.c            ← Uso correcto de malloc/realloc/free
│   ├── buggy_mem.c            ← Código con 3 errores intencionales de memoria
│   ├── buggy_mem_fixed.c      ← Versión corregida de buggy_mem.c
│   └── test.sh
├── 03-base-bounds/
│   ├── base_bounds.c          ← Simulador de traducción VA→PA con base & bounds
│   └── test.sh
├── 04-segmentation/
│   └── segmentation_calc.md   ← Traducciones manuales con tabla de segmentos
├── 05-paging/
│   ├── paging_sim.c           ← Simulador de paginación con tabla de páginas
│   ├── paging_calc.md         ← Cálculos de VPN, PFN, tamaño de tabla
│   └── test.sh
├── 06-free-space/
│   ├── fragmentation.c        ← Demo de fragmentación externa en glibc
│   ├── free_list_sim.c        ← Simulador de first fit y best fit
│   └── test.sh
└── 07-tlb/
    ├── tlb_locality.c         ← Benchmark de localidad espacial vs TLB
    └── test.sh
```

---

## Compilación y ejecución

```bash
# Sección 1
cd 01-address-space && gcc -Wall -o mem_map mem_map.c && ./mem_map

# Sección 2
cd 02-memory-api
gcc -Wall -o heap_demo heap_demo.c && valgrind --leak-check=full ./heap_demo
gcc -Wall -g -o buggy_mem buggy_mem.c && valgrind --leak-check=full ./buggy_mem
gcc -Wall -g -o buggy_mem_fixed buggy_mem_fixed.c && valgrind --leak-check=full ./buggy_mem_fixed

# Sección 3
cd 03-base-bounds && gcc -Wall -o base_bounds base_bounds.c && ./base_bounds

# Sección 5
cd 05-paging && gcc -Wall -o paging_sim paging_sim.c && ./paging_sim

# Sección 6
cd 06-free-space
gcc -Wall -o fragmentation fragmentation.c && ./fragmentation
gcc -Wall -o free_list_sim free_list_sim.c && ./free_list_sim

# Sección 7
cd 07-tlb && gcc -O0 -o tlb_locality tlb_locality.c && ./tlb_locality
```

---

## Documentación de funciones desarrolladas

### 01-address-space/mem_map.c

| Función | Descripción |
| ------- | ----------- |
| `main()` | Imprime el PID y las direcciones virtuales de variables en cada segmento (código, datos globales, stack, heap). Pausa con `getchar()` para permitir inspeccionar `/proc/<pid>/maps`. |

### 02-memory-api/heap_demo.c

| Función | Descripción |
| ------- | ----------- |
| `main()` | Asigna un arreglo de 10 enteros con `malloc`, lo llena con cuadrados, lo expande a 20 con `realloc`, completa los nuevos valores y libera correctamente con `free`. |

### 02-memory-api/buggy_mem_fixed.c

| Función | Descripción |
| ------- | ----------- |
| `main()` | Versión corregida de `buggy_mem.c`: bucle con `i < 5` (no `<=`), lectura de `p[0]` antes de `free(p)`, y `free(q)` antes del return. |

### 03-base-bounds/base_bounds.c

| Función | Descripción |
| ------- | ----------- |
| `traducir(Registro r, int va)` | Aplica la fórmula PA = VA + base, validando que `0 ≤ VA < bounds`. Imprime una excepción si la VA viola el bounds. Retorna la PA o -1. |
| `main()` | Declara los registros de los Procesos A, B y C, y traduce el conjunto de VAs `{0, 10, 63, 64, 100}` para cada proceso. |

### 05-paging/paging_sim.c

| Función | Descripción |
| ------- | ----------- |
| `traducir(int va)` | Extrae el VPN (bits altos) y el offset (bits bajos) de la VA. Consulta la tabla de páginas: si PFN == -1 reporta PAGE FAULT; si no, calcula PA = (PFN << PAGE_BITS) |
| `main()` | Ejecuta la traducción sobre el conjunto de VAs del enunciado e imprime la tabla de resultados. |

### 06-free-space/free_list_sim.c

| Función | Descripción |
| ------- | ----------- |
| `init_list(Block list[], int *n)` | Inicializa la lista libre con los 5 bloques del enunciado (0x0100→100B … 0x0700→600B). |
| `print_list(Block list[], int n)` | Imprime el estado actual de cada bloque (dirección, tamaño, libre/asignado). |
| `first_fit(Block list[], int *n, int request)` | Busca el primer bloque libre con tamaño ≥ request. Si lo encuentra, lo marca asignado y divide el remanente en un nuevo bloque libre. Retorna la dirección asignada o -1. |
| `best_fit(Block list[], int *n, int request)` | Busca el bloque libre con el tamaño más ajustado (mínimo desperdicio) ≥ request. Misma lógica de división que first_fit. Retorna dirección asignada o -1. |
| `run_strategy(name, strategy)` | Inicializa la lista, ejecuta las 4 solicitudes del enunciado con la estrategia dada, imprime cada asignación y el estado final. |

### 06-free-space/fragmentation.c

| Función | Descripción |
| ------- | ----------- |
| `main()` | Asigna 10 bloques de tamaños variados, calcula el overhead de glibc entre bloques contiguos, libera los de índice par para crear huecos no contiguos, e intenta asignar un bloque de 1500 bytes reportando el resultado. |

### 07-tlb/tlb_locality.c

| Función | Descripción |
| ------- | ----------- |
| `ms(struct timespec a, struct timespec b)` | Calcula la diferencia en milisegundos entre dos instantes de tiempo medidos con `clock_gettime`. |
| `main()` | Asigna un arreglo de 16 MB, lo recorre de forma **secuencial** (alta localidad espacial, muchos TLB hits) y luego de forma **aleatoria** usando una permutación Fisher-Yates (baja localidad, muchos TLB misses). Imprime los tiempos y el factor de diferencia. |

---

## Problemas presentados y soluciones

| Problema | Solución aplicada |
| -------- | ----------------- |
| `heap_demo.c` tenía un bug de formato: el arreglo ampliado se imprimía sin espacios entre números (`0149...` en lugar de `0 1 4 9...`) | Se corrigió el `printf` del segundo bucle usando `"%d "` y se añadió espacio después del colon en el mensaje. |
| `base_bounds.c` no incluía el Proceso C requerido en la actividad 3.2.2 | Se agregó `Registro procC = {0, 32}` y el bucle de traducción correspondiente. |
| La actividad 6.1 requería simular first fit y best fit manualmente: resultado tedioso y propenso a error | Se implementó `free_list_sim.c` que simula ambas estrategias automáticamente, mostrando cada paso de asignación y el estado final de la lista libre. |
| Valgrind no estaba disponible en el entorno de desarrollo | Se instaló con `sudo apt install valgrind` según las instrucciones del enunciado. |

---

## Pruebas realizadas

### Sección 2 — Valgrind en heap_demo (sin errores)

```plain text
ERROR SUMMARY: 0 errors from 0 contexts
All heap blocks were freed -- no leaks are possible
```

### Sección 2 — Valgrind en buggy_mem (3 errores detectados)

```plain text
Invalid write of size 4    → buffer overflow (línea 10)
Invalid read of size 4     → use-after-free (línea 19)
100 bytes definitely lost  → memory leak (línea 13)
ERROR SUMMARY: 3 errors from 3 contexts
```

### Sección 2 — Valgrind en buggy_mem_fixed (sin errores)

```plain text
ERROR SUMMARY: 0 errors from 0 contexts
All heap blocks were freed -- no leaks are possible
```

### Sección 3 — base_bounds: VAs válidas e inválidas

```plain text
Proceso A: VA=0→PA=32 ✓, VA=63→PA=95 ✓, VA=64→EXCEPCIÓN ✓
Proceso C: VA=0→PA=0 ✓, VA=10→PA=10 ✓, VA=63→EXCEPCIÓN ✓
```

### Sección 5 — paging_sim: page faults correctos

```plain text
VA=0x10 (VPN=1, page_table[1]=-1) → PAGE FAULT ✓
VA=0xF0 (VPN=15, page_table[15]=-1) → PAGE FAULT ✓
```

### Sección 6 — free_list_sim: diferencia entre estrategias

```plain text
First Fit: malloc(426) → FALLO (973B libres pero fragmentados)
Best Fit:  malloc(426) → 0x0700  (satisface las 4 solicitudes)
```

### Sección 7 — tlb_locality: promedio 3 runs

```plain text
Secuencial: ~9.47 ms | Aleatorio: ~52.89 ms | Factor: ~5.6×
```

---

## Video de sustentación

[https://drive.google.com/file/d/1zVpIOgW1m31LihJUSASG7tduQY7Si40t/view?usp=sharing](https://drive.google.com/file/d/1zVpIOgW1m31LihJUSASG7tduQY7Si40t/view?usp=sharing)

---

## Manifiesto de transparencia — Uso de IA generativa

Se utilizó IA generativa (Claude) como apoyo en los siguientes puntos:

1. **Corrección de bug de formato en `heap_demo.c`**: la IA identificó que el segundo `printf` del arreglo ampliado carecía de espacios entre números.
2. **Implementación de `free_list_sim.c`**: la IA generó el simulador de first fit y best fit a partir de la descripción del enunciado, incluyendo la lógica de división de bloques y la función de inicialización.
3. **Implementación de `fragmentation.c`**: se amplió el código base del enunciado con medición de overhead de glibc y reporte detallado.
4. **Implementación de `tlb_locality.c`**: se tomó el código base del enunciado y se añadió la medición del factor de lentitud y el comentario `volatile` para evitar optimización del compilador.
5. **Redacción de respuestas en `QUESTIONS.md`**: la IA ayudó a estructurar y completar las respuestas conceptuales, que luego fueron revisadas y validadas con el material del OSTEP.
6. **Adición del Proceso C en `base_bounds.c`**: la IA identificó que el Proceso C requerido en la actividad 3.2.2 no estaba en el código fuente y lo añadió.

Todos los contenidos conceptuales fueron verificados contra el libro OSTEP y los conocimientos adquiridos en clase. El código fue compilado, ejecutado y validado por el equipo antes de incluirlo en el repositorio.

---

## Conclusiones

1. **El espacio de direcciones virtual es una abstracción fundamental del SO.** Cada proceso recibe la ilusión de un espacio privado y contiguo gracias a la MMU, aunque físicamente su memoria puede estar dispersa en RAM. Esto se confirmó empíricamente al observar que dos instancias de `mem_map` tienen las mismas direcciones virtuales pero apuntan a marcos físicos distintos.

2. **La gestión manual de memoria en C exige disciplina.** Valgrind demostró que los tres errores clásicos (buffer overflow, memory leak y use-after-free) no siempre producen un crash inmediato pero generan corrupción silenciosa o vulnerabilidades de seguridad graves. La verificación del retorno de `malloc` y el balance malloc/free son prácticas no negociables.

3. **Base & bounds es simple pero ineficiente en el uso de memoria.** Al tratar el espacio de un proceso como un único bloque contiguo, cualquier espacio no utilizado entre heap y stack queda desperdiciado. La segmentación resuelve la fragmentación interna pero introduce fragmentación externa, motivando el desarrollo de la paginación.

4. **La paginación elimina la fragmentación externa a costa de fragmentación interna acotada.** Al usar marcos de tamaño fijo, cualquier marco libre satisface cualquier solicitud de página, eliminando los huecos inutilizables que genera la segmentación. El costo (tabla de páginas de 4 MB por proceso en 32 bits) se mitiga con tablas multinivel y el TLB.

5. **El TLB es el componente de hardware más crítico para el rendimiento de la gestión de memoria.** El experimento con `tlb_locality` mostró que el acceso aleatorio es ~5.6× más lento que el secuencial, directamente atribuible a la tasa de TLB misses. Diseñar estructuras de datos y algoritmos con localidad espacial no es solo una optimización de caché de datos, sino también una optimización de traducción de direcciones.

6. **La estrategia de asignación de memoria libre impacta significativamente la fragmentación.** La simulación mostró que first fit falla ante la 4.ª solicitud mientras best fit la satisface, con la misma lista libre inicial. La ausencia de coalescing puede hacer fallar solicitudes aunque haya memoria libre suficiente en total, un caso concreto de cómo el diseño del allocator afecta la disponibilidad efectiva de memoria.
