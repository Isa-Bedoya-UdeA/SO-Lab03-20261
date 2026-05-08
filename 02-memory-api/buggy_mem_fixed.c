// buggy_mem_fixed.c -- Versión corregida
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    /* CORRECCIÓN 1: buffer overflow - usar < en lugar de <= */
    int *p = malloc(5 * sizeof(int));
    if (p == NULL) {
        perror("malloc");
        return 1;
    }
    for (int i = 0; i < 5; i++)  /* Ahora solo accede índices 0-4 */
        p[i] = i;

    /* CORRECCIÓN 2: memory leak - liberar q antes de terminar */
    char *q = malloc(100);
    if (q == NULL) {
        perror("malloc");
        free(p);
        return 1;
    }
    strcpy(q, "hola mundo");
    printf("%s\n", q);
    free(q);  /* ← Agregado: liberar memoria de q */

    /* CORRECCIÓN 3: use-after-free - NO acceder a p después de free */
    printf("p[0] antes de free = %d\n", p[0]);  /* ← Movido antes del free */
    free(p);
    /* Eliminado: printf("p[0] = %d\n", p[0]); */

    return 0;
}