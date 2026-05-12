# Cálculos de Segmentación

## Tabla de Segmentos

| Segmento | Base (PA) | Tamaño | Crece     | Selector |
|----------|-----------|--------|-----------|----------|
| Code     | 0x4000    | 2 KB   | positivo→ | 00       |
| Heap     | 0x6000    | 3 KB   | positivo→ | 01       |
| Stack    | 0x2800    | 2 KB   | negativo← | 11       |

**Espacio virtual:** 14 bits (2 bits selector + 12 bits offset)

---

## Traducciones Paso a Paso

### VA = 0x03A0

Binario: 0000 0011 1010 0000
^^   ^^^^^^^^^^^^
00   0x3A0

Selector: 00 → Code
Offset:   0x3A0 = 928 bytes

Verificación:

- ¿Offset < Tamaño? → 928 < 2048 ✓

Cálculo PA:
PA = Base + Offset
PA = 0x4000 + 0x3A0
PA = 0x43A0 = 17,376 bytes

**Resultado:** PA = **0x43A0** ✓

---

### VA = 0x1800

Binario: 0001 1000 0000 0000
^^   ^^^^^^^^^^^^
01   0x800

Selector: 01 → Heap
Offset:   0x800 = 2048 bytes

Verificación:

- ¿Offset < Tamaño? → 2048 < 3072 ✓

Cálculo PA:
PA = Base + Offset
PA = 0x6000 + 0x800
PA = 0x6800 = 26,624 bytes

**Resultado:** PA = **0x6800** ✓

---

### VA = 0x3C00

Binario: 0011 1100 0000 0000
^^   ^^^^^^^^^^^^
11   0xC00

Selector: 11 → Stack (crece negativo)
Offset:   0xC00 = 3072 bytes

Para segmentos negativos:
Offset_real = Tamaño_max - Offset
Offset_real = 4096 - 3072 = 1024 bytes

Verificación:

- ¿Offset_real < Tamaño? → 1024 < 2048 ✓

Cálculo PA:
PA = Base - Offset_real
PA = 0x2800 - 1024
PA = 0x2800 - 0x400
PA = 0x2400 = 9,216 bytes

**Resultado:** PA = **0x2400** ✓

**Nota:** El Stack crece hacia direcciones menores. El offset se invierte:
- VA alta → PA baja (cerca de la base)
- VA baja → PA alta (alejado de la base)

---

### VA = 0x0C00

Binario: 0000 1100 0000 0000
^^   ^^^^^^^^^^^^
00   0xC00

Selector: 00 → Code
Offset:   0xC00 = 3072 bytes

Verificación:

- ¿Offset < Tamaño? → 3072 < 2048 ✗

EXCEPCIÓN: Offset excede el tamaño del segmento Code

**Resultado:** **EXCEPCIÓN** (Segmentation Fault)

---

### VA = 0x2200

Binario: 0010 0010 0000 0000
^^   ^^^^^^^^^^^^
10   0x200

Selector: 10 → ???

PROBLEMA: El selector '10' no está definido en la tabla.
Solo existen: 00 (Code), 01 (Heap), 11 (Stack)

**Resultado:** **EXCEPCIÓN** (Selector inválido)

---

## Tabla de Resultados Completa

| VA (hex) | Selector | Offset | Segmento | PA o Excepcion |
|----------|----------|--------|----------|----------------|
| 0x03A0   | 00       | 0x3A0  | Code     | 0x43A0         |
| 0x1800   | 01       | 0x800  | Heap     | 0x6800         |
| 0x3C00   | 11       | 0xC00  | Stack    | 0x2400         |
| 0x0C00   | 00       | 0xC00  | Code     | EXCEPCIÓN      |
| 0x2200   | 10       | —      | ???      | EXCEPCIÓN      |

---

## Fórmulas Utilizadas

### Segmentos de crecimiento positivo (Code, Heap):

PA = Base + Offset
(siempre que Offset < Tamaño)

### Segmentos de crecimiento negativo (Stack):

Offset_real = Tamaño_máximo - Offset
PA = Base - Offset_real
(siempre que Offset_real < Tamaño)


Donde `Tamaño_máximo = 2^(bits_offset) = 2^12 = 4096 bytes`

---

## Respuestas a Preguntas

### 1. ¿Por qué el Stack crece en dirección negativa?

El Stack crece hacia direcciones menores por razones históricas y de diseño:

- **Separación natural:** Permite que heap y stack crezcan uno hacia el otro sin colisionar prematuramente
- **Convención de arquitectura:** Las CPUs x86 utilizan instrucciones PUSH/POP que decrementan el Stack Pointer
- **Detección de colisión:** Cuando heap y stack se encuentran, se detecta desbordamiento (stack overflow)

**Ajuste especial en la fórmula:**

Offset_real = (2^12 - Offset) = 4096 - Offset
PA = Base - Offset_real


En lugar de sumar el offset a la base, se resta desde la base considerando que las direcciones virtuales altas del stack mapean a direcciones físicas bajas.

---

### 2. ¿Qué ventaja tiene la segmentación frente a base & bounds?

| Aspecto | Base & Bounds | Segmentación |
|---------|---------------|--------------|
| Granularidad | Un solo par (base, bounds) para todo el proceso | Múltiples pares, uno por segmento lógico |
| Espacio desperdiciado | Asigna memoria para todo el espacio virtual, incluso regiones no usadas entre heap y stack | Solo asigna memoria para segmentos activos |
| Protección | Protección global (todo o nada) | Protección por segmento (código read-only, datos read-write) |
| Crecimiento | Difícil redimensionar | Cada segmento crece independientemente |

**Ventaja principal:** La segmentación **reduce la fragmentación interna** al no reservar memoria para el "hueco" entre heap y stack, que puede ser enorme.

**Ejemplo:**

Base & Bounds:

```plain text
[Code|Heap|---espacio vacío---|Stack]
└─────────── todo reservado ──────────┘
```

Segmentación:

```plain text
[Code] ... [Heap] ... [Stack]
└─────┘    └────┘     └─────┘
```
Solo se asigna memoria física a regiones usadas


---

### 3. ¿Qué es la fragmentación externa?

**Fragmentación externa** ocurre cuando hay suficiente memoria total libre, pero está dividida en bloques no contiguos demasiado pequeños para satisfacer una solicitud.

**¿Por qué surge con segmentación?**

A medida que procesos se crean y terminan, se liberan segmentos de tamaños variables, dejando "huecos" en la memoria física:

Estado inicial:

```plain text
┌────────┬────────┬────────┬────────┐
│ Proc A │ Proc B │ Proc C │  Libre │
│  32KB  │  64KB  │  16KB  │  100KB │
└────────┴────────┴────────┴────────┘
```

Proc B termina:

```plain text
┌────────┬────────┬────────┬────────┐
│ Proc A │  Libre │ Proc C │  Libre │
│  32KB  │  64KB  │  16KB  │  100KB │
└────────┴────────┴────────┴────────┘
```

Proc C termina:

```plain text
┌────────┬────────┬────────┬────────┐
│ Proc A │  Libre │  Libre │  Libre │
│  32KB  │  64KB  │  16KB  │  100KB │
└────────┴────────┴────────┴────────┘
└── 64KB ─┘ └─ 16KB ──┘ └── 100KB ──┘
```

Memoria libre total: 180 KB
¡Pero no se puede asignar un segmento de 128 KB!
Los huecos están fragmentados.


**Solución:** Compactación (mover segmentos para juntar huecos) o paginación (bloques de tamaño fijo).

---

### 4. Diagrama de fragmentación externa

Ver archivo: `diagrams/fragmentation.py`
