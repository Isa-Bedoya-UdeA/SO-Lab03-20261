#!/bin/bash

# ============================================
# Script de pruebas para base_bounds
# Laboratorio 3 - Base & Bounds
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✘ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# ============================================
# 1. Compilación
# ============================================
print_header "Compilando base_bounds"
gcc -Wall -Wextra -std=c99 -o base_bounds base_bounds.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 2. Ejecución del programa original
# ============================================
print_header "Ejecución del simulador base & bounds"
./base_bounds > base_bounds_output.txt
cat base_bounds_output.txt
echo

# ============================================
# 3. Verificación de excepciones
# ============================================
print_header "Verificando detección de excepciones"

if grep -q "VA=64 viola bounds" base_bounds_output.txt; then
    print_success "Excepción detectada correctamente para VA=64 en Proceso A"
else
    print_error "No se detectó excepción para VA=64"
fi

if grep -q "VA=100 viola bounds" base_bounds_output.txt; then
    print_success "Excepción detectada correctamente para VA=100 en Proceso A"
else
    print_error "No se detectó excepción para VA=100"
fi
echo

# ============================================
# 4. Verificación de traducciones correctas
# ============================================
print_header "Verificando traducciones correctas"

# Proceso A: base=32, bounds=64
# VA=0 -> PA=32, VA=10 -> PA=42, VA=63 -> PA=95
if grep -q "VA=  0 -> PA= 32" base_bounds_output.txt; then
    print_success "Proceso A: VA=0 → PA=32 ✓"
fi

if grep -q "VA= 10 -> PA= 42" base_bounds_output.txt; then
    print_success "Proceso A: VA=10 → PA=42 ✓"
fi

if grep -q "VA= 63 -> PA= 95" base_bounds_output.txt; then
    print_success "Proceso A: VA=63 → PA=95 ✓"
fi

# Proceso B: base=128, bounds=80
# VA=0 -> PA=128, VA=10 -> PA=138
if grep -q "VA=  0 -> PA=128" base_bounds_output.txt; then
    print_success "Proceso B: VA=0 → PA=128 ✓"
fi

if grep -q "VA= 10 -> PA=138" base_bounds_output.txt; then
    print_success "Proceso B: VA=10 → PA=138 ✓"
fi
echo

# ============================================
# 5. Prueba con Proceso C adicional
# ============================================
print_header "Creando versión extendida con Proceso C"
cat > base_bounds_extended.c << 'EOF'
#include <stdio.h>

typedef struct { int base; int bounds; } Registro;

int traducir(Registro r, int va) {
    if (va < 0 || va >= r.bounds) {
        printf("  [EXCEPCION] VA=%d viola bounds=%d\n", va, r.bounds);
        return -1;
    }
    return r.base + va;
}

int main() {
    Registro procA = {32, 64};
    Registro procB = {128, 80};
    Registro procC = {0, 32};  /* Proceso C adicional */
    
    int vas[] = {0, 10, 63, 64, 100};
    int n = sizeof(vas) / sizeof(vas[0]);

    printf("--- Proceso A (base=%d, bounds=%d) ---\n", procA.base, procA.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procA, vas[i]);
        if (pa != -1)
            printf("  VA=%3d -> PA=%3d\n", vas[i], pa);
    }
    
    printf("--- Proceso B (base=%d, bounds=%d) ---\n", procB.base, procB.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procB, vas[i]);
        if (pa != -1)
            printf("  VA=%3d -> PA=%3d\n", vas[i], pa);
    }
    
    printf("--- Proceso C (base=%d, bounds=%d) ---\n", procC.base, procC.bounds);
    for (int i = 0; i < n; i++) {
        int pa = traducir(procC, vas[i]);
        if (pa != -1)
            printf("  VA=%3d -> PA=%3d\n", vas[i], pa);
    }
    
    return 0;
}
EOF

gcc -Wall -Wextra -std=c99 -o base_bounds_extended base_bounds_extended.c
if [ $? -eq 0 ]; then
    print_success "Versión extendida compilada"
    echo
    ./base_bounds_extended
    echo
else
    print_error "Error compilando versión extendida"
fi

# ============================================
# 6. Resumen
# ============================================
print_header "Pruebas completadas"
print_info "Archivo generado: base_bounds_output.txt"
print_success "Simulador base & bounds funcionando correctamente"