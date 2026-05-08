# Respuestas a Preguntas del Laboratorio 3

## Equipo
* Rafael Angel Alemán Castillo - rafael.aleman@udea.edu.co - CC. 1001560844
* Isabela Bedoya Gaviria - isabela.bedoya@udea.edu.co - CC. 1020106520

---

## Sección 1: Espacio de Direcciones

### 1.3.1 - Permisos de regiones

**Pregunta:** Identifique en la salida de /proc/maps las regiones text, heap y stack. ¿Qué permisos (r/w/x/p) tiene cada una? ¿Por qué difieren?

**Respuesta:**

[Tu respuesta aquí después de ejecutar el programa]

---

### 1.3.2 - Mapeo de variables

**Pregunta:** Compare las direcciones impresas con los rangos de /proc/maps. ¿A qué región pertenece cada variable?

**Respuesta:**

[Tu respuesta aquí]

---

### 1.3.3 - Otras regiones

**Pregunta:** ¿Qué otras regiones aparecen en el mapa (libc, [vdso], [vsyscall])? ¿Qué función cumple cada una?

**Respuesta:**

[Tu respuesta aquí]

---

### 1.3.4 - Direcciones virtuales vs físicas

**Pregunta:** ¿Son las direcciones virtuales iguales a las físicas? Explique apoyándose en el concepto de address space del OSTEP.

**Respuesta:**

[Tu respuesta aquí]

---

### 1.4.1 - Comparación de espacios

**Pregunta:** ¿Son las mismas direcciones virtuales en ambos procesos? ¿Qué conclusión saca sobre el aislamiento del espacio de direcciones?

**Respuesta:**

[Tu respuesta aquí]

---

### 1.4.2 - Acceso entre procesos

**Pregunta:** ¿Podría el Proceso A leer o modificar la variable global del Proceso B mediante su dirección virtual? Justifique.

**Respuesta:**

[Tu respuesta aquí]

---

## Sección 2: API de Memoria

### 2.2.1 - Salida de Valgrind

**Pregunta:** Muestre la salida completa de Valgrind. ¿Reporta errores o fugas de memoria? ¿Qué significa el mensaje "All heap blocks were freed"?

**Respuesta:**

[Tu respuesta aquí]

---

### 2.2.2 - sizeof vs literal

**Pregunta:** ¿Por qué se usa sizeof(int) en lugar del valor literal 4? ¿Qué ventaja ofrece en portabilidad entre arquitecturas?

**Respuesta:**

[Tu respuesta aquí]

---

### 2.2.3 - malloc retorna NULL

**Pregunta:** ¿Qué devuelve malloc cuando no hay memoria disponible? ¿Por qué es crítico verificar ese valor antes de usarlo?

**Respuesta:**

[Tu respuesta aquí]

---

### 2.4.1 - Errores de Valgrind

**Pregunta:** Transcriba los mensajes que arroja Valgrind. ¿Cuál mensaje corresponde a cada uno de los tres errores clásicos?

**Respuesta:**

[Tu respuesta aquí]

---

### 2.4.2 - Código corregido

**Pregunta:** Corrija el programa (buggy_mem_fixed.c) y verifique con Valgrind que no queda ningún error ni fuga.

**Respuesta:**

[Tu respuesta aquí - incluir salida de Valgrind]

---

### 2.4.3 - Consecuencias de use-after-free

**Pregunta:** ¿Qué consecuencias puede tener un use-after-free en un programa real en términos de seguridad y estabilidad del sistema?

**Respuesta:**

[Tu respuesta aquí]

---

## Sección 3: Base & Bounds

### 3.2.1 - Salida del simulador

**Pregunta:** Compile y ejecute. Muestre la salida completa. ¿Qué ocurre al acceder a VA=64 y VA=100 en el Proceso A? ¿Qué haría el SO real ante esta excepción?

**Respuesta:**

[Tu respuesta aquí]

---

### 3.2.2 - Proceso C

**Pregunta:** Agregue un Proceso C (base=0, bounds=32) al programa y traduzca las mismas VAs. ¿Puede el Proceso A acceder a las direcciones del Proceso C directamente? Justifique.

**Respuesta:**

[Tu respuesta aquí]

---

### 3.2.3 - Limitación de base & bounds

**Pregunta:** ¿Cuál es la limitación principal del esquema base & bounds que motiva el surgimiento de la segmentación?

**Respuesta:**

[Tu respuesta aquí]

---

## Sección 4: Segmentación

### 4.1.1 - Cálculos de traducción

**Pregunta:** Muestre el cálculo paso a paso para cada VA.

**Respuesta:**

Ver archivo `04-segmentation/segmentation_calc.md`

---

### 4.1.2 - Stack negativo

**Pregunta:** ¿Por qué el Stack crece en dirección negativa? ¿Qué ajuste especial requiere la fórmula al calcular el PA?

**Respuesta:**

Ver archivo `04-segmentation/segmentation_calc.md`

---

### 4.1.3 - Ventaja sobre base & bounds

**Pregunta:** ¿Qué ventaja tiene la segmentación frente a base & bounds en cuanto a utilización de la memoria física?

**Respuesta:**

Ver archivo `04-segmentation/segmentation_calc.md`

---

### 4.1.4 - Fragmentación externa

**Pregunta:** ¿Qué es la fragmentación externa? ¿Por qué surge con segmentación? Ilustre con un diagrama de bloques de memoria.

**Respuesta:**

Ver archivo `04-segmentation/segmentation_calc.md` y diagrama en `04-segmentation/diagrams/fragmentation.py`

---

## Sección 5: Paginación

### 5.1.1 - Bits VPN y offset

**Pregunta:** ¿Cuántos bits se necesitan para el VPN y cuántos para el offset? Muestre el cálculo.

**Respuesta:**

Ver archivo `05-paging/paging_calc.md`

---

### 5.1.2 - Entradas de tabla

**Pregunta:** ¿Cuántas entradas tiene la tabla de páginas de un proceso?

**Respuesta:**

Ver archivo `05-paging/paging_calc.md`

---

### 5.1.3 - Memoria de tabla

**Pregunta:** ¿Cuánta memoria ocupa la tabla de páginas completa? ¿Es razonable ese tamaño para cada proceso?

**Respuesta:**

Ver archivo `05-paging/paging_calc.md`

---

### 5.1.4 - Bits de control

**Pregunta:** ¿Cuántos bits necesita el PFN dentro de la PTE? ¿Qué información almacenan los bits restantes? Mencione al menos 3 bits de control y su función.

**Respuesta:**

Ver archivo `05-paging/paging_calc.md`

---

### 5.3.1 - Salida del simulador

**Pregunta:** Compile y ejecute el simulador. Muestre la salida completa.

**Respuesta:**

[Tu respuesta aquí]

---

### 5.3.2 - Page faults

**Pregunta:** ¿Qué ocurre con las VAs 0x10 y 0xA3? ¿Qué debería hacer el SO real ante un page fault?

**Respuesta:**

[Tu respuesta aquí]

---

### 5.3.3 - Overhead de acceso

**Pregunta:** ¿Cuántos accesos a memoria física requiere completar una instrucción load con tabla de páginas de un solo nivel? ¿Por qué es costoso y qué solución de hardware existe?

**Respuesta:**

[Tu respuesta aquí]

---

### 5.3.4 - Ventaja sobre segmentación

**Pregunta:** ¿Qué ventaja tiene la paginación sobre la segmentación en cuanto a la fragmentación?

**Respuesta:**

[Tu respuesta aquí]