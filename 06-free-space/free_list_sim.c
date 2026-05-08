// free_list_sim.c
// Laboratorio 3 - Sección 6.1: Simulación de estrategias de asignación
// Simula first fit y best fit sobre la lista libre del enunciado.
#include <stdio.h>
#include <string.h>

#define MAX_BLOCKS 20

/**
 * struct Block - Representa un bloque en la lista libre.
 * @addr:   Dirección de inicio del bloque (en bytes, relativa a 0x0000).
 * @size:   Tamaño en bytes del bloque.
 * @free:   1 si el bloque está libre, 0 si está asignado.
 */
typedef struct {
    int addr;
    int size;
    int free;
} Block;

/**
 * init_list() - Inicializa la lista libre con el estado del enunciado.
 * @list:  Arreglo de bloques a inicializar.
 * @n:     Puntero al número de bloques (salida).
 *
 * Estado inicial según enunciado:
 *   0x0100 -> 100 bytes
 *   0x0200 -> 500 bytes
 *   0x0400 -> 200 bytes
 *   0x0500 -> 300 bytes
 *   0x0700 -> 600 bytes
 */
void init_list(Block list[], int *n) {
    list[0] = (Block){0x0100, 100, 1};
    list[1] = (Block){0x0200, 500, 1};
    list[2] = (Block){0x0400, 200, 1};
    list[3] = (Block){0x0500, 300, 1};
    list[4] = (Block){0x0700, 600, 1};
    *n = 5;
}

/**
 * print_list() - Imprime el estado actual de la lista libre.
 * @list:  Arreglo de bloques.
 * @n:     Número de bloques.
 */
void print_list(Block list[], int n) {
    printf("  %-8s %-8s %-8s\n", "Dirección", "Tamaño", "Estado");
    printf("  %-8s %-8s %-8s\n", "---------", "-------", "------");
    for (int i = 0; i < n; i++) {
        printf("  0x%04X   %-8d %s\n",
               list[i].addr, list[i].size,
               list[i].free ? "LIBRE" : "ASIGNADO");
    }
}

/**
 * first_fit() - Asigna memoria con estrategia first fit.
 * @list:    Arreglo de bloques.
 * @n:       Número de bloques.
 * @request: Bytes solicitados.
 *
 * Busca el PRIMER bloque libre con tamaño >= request.
 * Si el bloque es mayor, lo divide dejando el resto libre.
 *
 * Return: Dirección asignada, o -1 si no hay espacio.
 */
int first_fit(Block list[], int *n, int request) {
    for (int i = 0; i < *n; i++) {
        if (list[i].free && list[i].size >= request) {
            int addr = list[i].addr;
            int remainder = list[i].size - request;
            list[i].free = 0;
            list[i].size = request;
            /* Si sobra espacio, insertar nuevo bloque libre */
            if (remainder > 0) {
                /* Desplazar bloques siguientes */
                for (int j = *n; j > i + 1; j--)
                    list[j] = list[j-1];
                list[i+1] = (Block){addr + request, remainder, 1};
                (*n)++;
            }
            return addr;
        }
    }
    return -1; /* No hay bloque suficiente */
}

/**
 * best_fit() - Asigna memoria con estrategia best fit.
 * @list:    Arreglo de bloques.
 * @n:       Número de bloques.
 * @request: Bytes solicitados.
 *
 * Busca el bloque libre con el tamaño MÁS AJUSTADO (mínimo desperdicio).
 * Si hay empate, elige el primero encontrado.
 *
 * Return: Dirección asignada, o -1 si no hay espacio.
 */
int best_fit(Block list[], int *n, int request) {
    int best_i = -1;
    int best_size = __INT_MAX__;
    for (int i = 0; i < *n; i++) {
        if (list[i].free && list[i].size >= request) {
            if (list[i].size < best_size) {
                best_size = list[i].size;
                best_i = i;
            }
        }
    }
    if (best_i == -1) return -1;

    int addr = list[best_i].addr;
    int remainder = list[best_i].size - request;
    list[best_i].free = 0;
    list[best_i].size = request;
    if (remainder > 0) {
        for (int j = *n; j > best_i + 1; j--)
            list[j] = list[j-1];
        list[best_i+1] = (Block){addr + request, remainder, 1};
        (*n)++;
    }
    return addr;
}

/**
 * run_strategy() - Ejecuta las 4 solicitudes con la estrategia dada.
 * @name:     Nombre de la estrategia ("First Fit" o "Best Fit").
 * @strategy: Puntero a función de asignación.
 */
void run_strategy(const char *name,
                  int (*strategy)(Block[], int*, int)) {
    Block list[MAX_BLOCKS];
    int n;
    init_list(list, &n);

    int requests[] = {212, 417, 98, 426};
    int nr = 4;

    printf("\n========================================\n");
    printf("  Estrategia: %s\n", name);
    printf("========================================\n");
    printf("\nEstado inicial:\n");
    print_list(list, n);

    for (int i = 0; i < nr; i++) {
        int addr = strategy(list, &n, requests[i]);
        printf("\nmalloc(%d) -> ", requests[i]);
        if (addr != -1)
            printf("0x%04X\n", addr);
        else
            printf("FALLO (sin espacio)\n");
    }

    printf("\nEstado final (lista libre):\n");
    print_list(list, n);

    /* Contar fragmentación */
    int free_blocks = 0, free_total = 0;
    for (int i = 0; i < n; i++) {
        if (list[i].free) {
            free_blocks++;
            free_total += list[i].size;
        }
    }
    printf("\nResumen: %d bloque(s) libre(s), %d bytes libres totales\n",
           free_blocks, free_total);
}

int main() {
    printf("=== Simulación de estrategias de asignación ===\n");
    printf("Solicitudes: malloc(212), malloc(417), malloc(98), malloc(426)\n");

    run_strategy("First Fit", first_fit);
    run_strategy("Best Fit",  best_fit);

    return 0;
}
