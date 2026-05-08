// base_bounds.c
// Laboratorio 3 - Sección 3: Traducción de direcciones Base & Bounds
// Simula el mecanismo hardware de traducción VA -> PA con registro base y bounds.
#include <stdio.h>

/**
 * struct Registro - Par base/bounds que describe el espacio de un proceso.
 * @base:   Dirección física donde comienza el proceso en RAM.
 * @bounds: Tamaño máximo del espacio asignado (límite de VA válida).
 */
typedef struct { int base; int bounds; } Registro;

/**
 * traducir() - Traduce una dirección virtual a física usando base & bounds.
 * @r:  Registro del proceso (base y bounds).
 * @va: Dirección virtual a traducir.
 *
 * Aplica la fórmula: PA = VA + base, válida solo si 0 <= VA < bounds.
 * Si VA está fuera del rango, imprime una excepción (segfault en SO real).
 *
 * Return: Dirección física PA, o -1 si viola bounds.
 */
int traducir(Registro r, int va) {
    if (va < 0 || va >= r.bounds) {
        printf("  [EXCEPCION] VA=%d viola bounds=%d\n", va, r.bounds);
        return -1;
    }
    return r.base + va;
}

int main() {
    Registro procA = {32,  64};   /* base=32,  bounds=64  */
    Registro procB = {128, 80};   /* base=128, bounds=80  */
    Registro procC = {0,   32};   /* base=0,   bounds=32  — agregado en 3.2.2 */

    int vas[] = {0, 10, 63, 64, 100};
    int n = sizeof(vas) / sizeof(vas[0]);

    printf("--- Proceso A (base=%d, bounds=%d) ---\n",
           procA.base, procA.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procA, vas[i]);
        if (pa != -1)
            printf("  VA=%3d  ->  PA=%3d\n", vas[i], pa);
    }

    printf("--- Proceso B (base=%d, bounds=%d) ---\n",
           procB.base, procB.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procB, vas[i]);
        if (pa != -1)
            printf("  VA=%3d  ->  PA=%3d\n", vas[i], pa);
    }

    printf("--- Proceso C (base=%d, bounds=%d) ---\n",
           procC.base, procC.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procC, vas[i]);
        if (pa != -1)
            printf("  VA=%3d  ->  PA=%3d\n", vas[i], pa);
    }

    return 0;
}
