// fragmentation.c
// Laboratorio 3 - Sección 6: Gestión de espacio libre
// Demuestra fragmentación externa en glibc (malloc/free)
#include <stdio.h>
#include <stdlib.h>
#define N 10

/**
 * main() - Demuestra la fragmentación externa en el heap.
 *
 * Asigna N bloques de tamaños variados, luego libera los de índice
 * par para crear "huecos" no contiguos en el heap. Finalmente intenta
 * asignar un bloque grande (1500 bytes) y reporta si tiene éxito.
 *
 * Objetivo: observar que aunque la memoria libre total puede ser
 * mayor que 1500 bytes, la fragmentación puede impedir la asignación
 * si los bloques libres no son contiguos.
 */
int main() {
    void *ptrs[N];
    int sizes[] = {16, 32, 64, 128, 256, 512, 1024, 512, 256, 128};

    /* Asignar N bloques de tamaños variados */
    printf("=== Asignando %d bloques ===\n", N);
    for (int i = 0; i < N; i++) {
        ptrs[i] = malloc(sizes[i]);
        printf("malloc(%4d) -> %p\n", sizes[i], ptrs[i]);
    }

    /* Calcular separación entre bloques contiguos */
    printf("\n=== Separación entre bloques consecutivos ===\n");
    for (int i = 0; i < N - 1; i++) {
        long sep = (char *)ptrs[i+1] - (char *)ptrs[i];
        printf("  ptrs[%d] -> ptrs[%d]: separación = %ld bytes "
               "(bloque=%d, overhead=%ld)\n",
               i, i+1, sep, sizes[i], sep - sizes[i]);
    }

    /* Liberar índices pares para crear huecos */
    printf("\n=== Liberando bloques en índices pares ===\n");
    long freed_total = 0;
    for (int i = 0; i < N; i += 2) {
        printf("free(ptrs[%d])  tamaño=%d bytes en %p\n",
               i, sizes[i], ptrs[i]);
        freed_total += sizes[i];
        free(ptrs[i]);
        ptrs[i] = NULL;
    }
    printf("Total liberado: %ld bytes en %d bloques no contiguos\n",
           freed_total, N / 2);

    /* Intentar asignar un bloque grande */
    printf("\n=== Intentando malloc(1500) ===\n");
    void *big = malloc(1500);
    printf("malloc(1500) -> %p [%s]\n",
           big, big ? "EXITO" : "FALLO");
    if (big) {
        printf("  (glibc pudo satisfacer la solicitud)\n");
        free(big);
    } else {
        printf("  (fragmentación externa impidió la asignación)\n");
    }

    /* Liberar bloques impares restantes */
    printf("\n=== Liberando bloques restantes ===\n");
    for (int i = 1; i < N; i += 2) {
        free(ptrs[i]);
        ptrs[i] = NULL;
    }
    printf("Todos los bloques liberados.\n");

    return 0;
}
