#!/bin/bash

# ============================================
# Script de pruebas para Memory API
# Laboratorio 3 - API de Memoria
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
# Verificar Valgrind
# ============================================
if ! command -v valgrind &> /dev/null; then
    print_error "Valgrind no está instalado"
    print_info "Instalar con: sudo apt install valgrind"
    exit 1
fi

# ============================================
# 1. Compilación de heap_demo
# ============================================
print_header "Compilando heap_demo"
gcc -Wall -g -o heap_demo heap_demo.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación de heap_demo"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 2. Prueba de heap_demo con Valgrind
# ============================================
print_header "Ejecutando heap_demo con Valgrind"
valgrind --leak-check=full --track-origins=yes --log-file=heap_demo_valgrind.log ./heap_demo
echo
cat heap_demo_valgrind.log
echo

if grep -q "All heap blocks were freed" heap_demo_valgrind.log; then
    print_success "heap_demo: Sin fugas de memoria"
else
    print_error "heap_demo: Posibles fugas detectadas"
fi
echo

# ============================================
# 3. Compilación de buggy_mem
# ============================================
print_header "Compilando buggy_mem (con errores intencionales)"
gcc -Wall -g -o buggy_mem buggy_mem.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación de buggy_mem"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 4. Prueba de buggy_mem con Valgrind
# ============================================
print_header "Ejecutando buggy_mem con Valgrind"
print_info "Se esperan 3 errores: buffer overflow, memory leak, use-after-free"
echo
valgrind --leak-check=full --track-origins=yes --log-file=buggy_mem_valgrind.log ./buggy_mem 2>&1
echo
cat buggy_mem_valgrind.log
echo

# Contar errores detectados
ERRORS=0
if grep -q "Invalid write" buggy_mem_valgrind.log; then
    print_error "ERROR 1 detectado: Buffer overflow (Invalid write)"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "definitely lost.*100 bytes" buggy_mem_valgrind.log; then
    print_error "ERROR 2 detectado: Memory leak (100 bytes de q)"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "Invalid read" buggy_mem_valgrind.log; then
    print_error "ERROR 3 detectado: Use-after-free (Invalid read)"
    ERRORS=$((ERRORS + 1))
fi

echo
print_info "Errores detectados: $ERRORS/3"
echo

# ============================================
# 5. Compilación de buggy_mem_fixed
# ============================================
print_header "Compilando buggy_mem_fixed (versión corregida)"
gcc -Wall -g -o buggy_mem_fixed buggy_mem_fixed.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación de buggy_mem_fixed"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 6. Prueba de buggy_mem_fixed con Valgrind
# ============================================
print_header "Ejecutando buggy_mem_fixed con Valgrind"
valgrind --leak-check=full --track-origins=yes --log-file=buggy_mem_fixed_valgrind.log ./buggy_mem_fixed
echo
cat buggy_mem_fixed_valgrind.log
echo

if grep -q "All heap blocks were freed" buggy_mem_fixed_valgrind.log && \
   grep -q "ERROR SUMMARY: 0 errors" buggy_mem_fixed_valgrind.log; then
    print_success "buggy_mem_fixed: Sin errores ni fugas"
else
    print_error "buggy_mem_fixed: Aún quedan errores"
fi
echo

# ============================================
# 7. Limpieza
# ============================================
print_header "Archivos generados"
print_info "Logs de Valgrind:"
echo "  - heap_demo_valgrind.log"
echo "  - buggy_mem_valgrind.log"
echo "  - buggy_mem_fixed_valgrind.log"
echo

print_success "Todas las pruebas completadas"