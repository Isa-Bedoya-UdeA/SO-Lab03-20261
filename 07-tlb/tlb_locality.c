// tlb_locality.c
// Laboratorio 3 - Sección 7: TLBs — Translation Lookaside Buffer
// Benchmark que mide el impacto de la localidad espacial en el rendimiento
// de acceso a memoria, relacionado con el TLB hit/miss rate.
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N (1 << 22)   /* 4M enteros = 16 MB */

/**
 * ms() - Calcula la diferencia en milisegundos entre dos timespec.
 * @a: Tiempo de inicio.
 * @b: Tiempo de fin.
 *
 * Return: Diferencia en milisegundos (double).
 */
double ms(struct timespec a, struct timespec b) {
    return (b.tv_sec  - a.tv_sec ) * 1000.0
         + (b.tv_nsec - a.tv_nsec) / 1e6;
}

/**
 * main() - Ejecuta dos patrones de acceso sobre un arreglo de 16 MB.
 *
 * Patrón 1 — SECUENCIAL: recorre arr[0], arr[1], ..., arr[N-1].
 *   Alta localidad espacial: cada página de 4 KB contiene 1024 enteros,
 *   por lo que el TLB se reutiliza 1024 veces antes de necesitar una
 *   nueva traducción → hit rate cercano al 100%.
 *
 * Patrón 2 — ALEATORIO: recorre arr en orden permutado (Fisher-Yates).
 *   Baja localidad espacial: cada acceso probablemente toca una página
 *   diferente, generando un TLB miss casi en cada acceso → hit rate bajo.
 *
 * La diferencia de tiempos refleja el costo de los TLB misses (acceso
 * a la tabla de páginas en memoria RAM en lugar de usar el caché TLB).
 */
int main() {
    /* Asignar arreglo de 16 MB e inicializar */
    int *arr = (int *) malloc(N * sizeof(int));
    if (!arr) { perror("malloc arr"); return 1; }
    for (int i = 0; i < N; i++) arr[i] = i;

    struct timespec t0, t1;
    volatile long sum = 0;   /* volatile evita que el compilador elimine el loop */

    /* ------------------------------------------------------------------ */
    /* Acceso SECUENCIAL — alta localidad espacial                         */
    /* ------------------------------------------------------------------ */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; i++) sum += arr[i];
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double t_seq = ms(t0, t1);
    printf("Secuencial : %8.2f ms  (sum=%ld)\n", t_seq, sum);

    /* ------------------------------------------------------------------ */
    /* Acceso ALEATORIO — baja localidad espacial (Fisher-Yates shuffle)   */
    /* ------------------------------------------------------------------ */
    int *idx = (int *) malloc(N * sizeof(int));
    if (!idx) { perror("malloc idx"); free(arr); return 1; }

    /* Construir permutación aleatoria */
    for (int i = 0; i < N; i++) idx[i] = i;
    srand(42);
    for (int i = N - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = idx[i]; idx[i] = idx[j]; idx[j] = tmp;
    }

    sum = 0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; i++) sum += arr[idx[i]];
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double t_rand = ms(t0, t1);
    printf("Aleatorio  : %8.2f ms  (sum=%ld)\n", t_rand, sum);

    /* Relación de lentitud */
    printf("\nEl acceso aleatorio fue %.1fx más lento que el secuencial.\n",
           t_rand / t_seq);

    free(arr);
    free(idx);
    return 0;
}
