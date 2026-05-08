#!/bin/bash

# ============================================
# Script de pruebas para mem_map
# Laboratorio 3 - Espacio de direcciones
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
print_header "Compilando mem_map"
gcc -Wall -Wextra -std=c99 -o mem_map mem_map.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 2. Ejecución con captura de PID
# ============================================
print_header "Ejecutando mem_map en segundo plano"
./mem_map &
PID=$!
sleep 1

if ! ps -p $PID > /dev/null; then
    print_error "El proceso no está corriendo"
    exit 1
fi
print_success "Proceso ejecutándose con PID: $PID"
echo

# ============================================
# 3. Captura de /proc/[pid]/maps
# ============================================
print_header "Capturando /proc/$PID/maps"
if [ -f /proc/$PID/maps ]; then
    cat /proc/$PID/maps > maps_output.txt
    print_success "Mapa de memoria guardado en maps_output.txt"
    echo
    cat maps_output.txt
    echo
else
    print_error "No se pudo acceder a /proc/$PID/maps"
fi

# ============================================
# 4. Captura de pmap
# ============================================
print_header "Ejecutando pmap -x $PID"
if command -v pmap &> /dev/null; then
    pmap -x $PID > pmap_output.txt 2>&1
    print_success "Salida de pmap guardada en pmap_output.txt"
    echo
    cat pmap_output.txt
    echo
else
    print_info "pmap no está disponible en este sistema"
fi

# ============================================
# 5. Análisis de regiones
# ============================================
print_header "Análisis de regiones de memoria"

# Buscar regiones principales
if grep -q "r-xp.*mem_map" maps_output.txt; then
    print_success "Región TEXT (código) encontrada"
fi

if grep -q "\[heap\]" maps_output.txt; then
    print_success "Región HEAP encontrada"
fi

if grep -q "\[stack\]" maps_output.txt; then
    print_success "Región STACK encontrada"
fi

if grep -q "libc" maps_output.txt; then
    print_success "Biblioteca libc encontrada"
fi

if grep -q "\[vdso\]" maps_output.txt; then
    print_success "VDSO encontrado"
fi
echo

# ============================================
# 6. Finalizar proceso
# ============================================
print_header "Finalizando mem_map"
echo "" > /proc/$PID/fd/0 2>/dev/null || kill $PID 2>/dev/null
wait $PID 2>/dev/null
print_success "Proceso finalizado"
echo

# ============================================
# 7. Ejecución de dos instancias simultáneas
# ============================================
print_header "Comparación de dos procesos simultáneos"
./mem_map > proc1.txt &
PID1=$!
./mem_map > proc2.txt &
PID2=$!

sleep 1

print_info "Proceso 1 (PID: $PID1):"
cat /proc/$PID1/maps | head -5 2>/dev/null || echo "No disponible"
echo

print_info "Proceso 2 (PID: $PID2):"
cat /proc/$PID2/maps | head -5 2>/dev/null || echo "No disponible"
echo

# Finalizar ambos procesos
kill $PID1 $PID2 2>/dev/null
wait $PID1 $PID2 2>/dev/null

print_success "Comparación completada"
echo

# ============================================
# 8. Resumen
# ============================================
print_header "Pruebas completadas"
print_info "Archivos generados:"
echo "  - maps_output.txt"
echo "  - pmap_output.txt (si pmap está disponible)"
echo "  - proc1.txt, proc2.txt"
echo
print_success "Todas las pruebas ejecutadas exitosamente"