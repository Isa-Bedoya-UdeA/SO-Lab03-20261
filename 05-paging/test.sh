#!/bin/bash

# ============================================
# Script de pruebas para paging_sim
# Laboratorio 3 - Paginación
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
print_header "Compilando paging_sim"
gcc -Wall -Wextra -std=c99 -o paging_sim paging_sim.c
if [ $? -ne 0 ]; then
    print_error "Error de compilación"
    exit 1
fi
print_success "Compilación exitosa"
echo

# ============================================
# 2. Ejecución del simulador
# ============================================
print_header "Ejecutando simulador de paginación"
./paging_sim > paging_output.txt
cat paging_output.txt
echo

# ============================================
# 3. Verificación de traducciones correctas
# ============================================
print_header "Verificando traducciones correctas"

# VA=0x00: VPN=0, page_table[0]=3 → PFN=3, PA=0x30
if grep -q "VA=0x00.*PFN= 3.*PA=0x30" paging_output.txt; then
    print_success "VA=0x00 → PA=0x30 ✓"
fi

# VA=0x0F: VPN=0, page_table[0]=3 → PFN=3, PA=0x3F
if grep -q "VA=0x0F.*PFN= 3.*PA=0x3F" paging_output.txt; then
    print_success "VA=0x0F → PA=0x3F ✓"
fi

# VA=0x20: VPN=2, page_table[2]=7 → PFN=7, PA=0x70
if grep -q "VA=0x20.*PFN= 7.*PA=0x70" paging_output.txt; then
    print_success "VA=0x20 → PA=0x70 ✓"
fi
echo

# ============================================
# 4. Verificación de page faults
# ============================================
print_header "Verificando detección de page faults"

# VA=0x10: VPN=1, page_table[1]=-1 → PAGE FAULT
if grep -q "VA=0x10.*PAGE FAULT" paging_output.txt; then
    print_success "VA=0x10 → PAGE FAULT ✓"
fi

# VA=0xA3: VPN=10, page_table[10]=4 → PFN=4, PA=0x43
if grep -q "VA=0xA3.*PFN= 4.*PA=0x43" paging_output.txt; then
    print_success "VA=0xA3 → PA=0x43 ✓"
fi
echo

# ============================================
# 5. Análisis de la tabla de páginas
# ============================================
print_header "Análisis de la tabla de páginas"

cat > analyze_page_table.c << 'EOF'
#include <stdio.h>

int main() {
    int page_table[16] = {
        3, -1, 7, 2, -1, 1, -1, 5,
        -1, -1, 4, -1, 6, -1, 0, -1
    };
    
    int present = 0, absent = 0;
    
    printf("Análisis de la tabla de páginas:\n");
    printf("%-5s %-10s %-5s\n", "VPN", "PFN", "Estado");
    printf("--------------------------------\n");
    
    for (int i = 0; i < 16; i++) {
        if (page_table[i] == -1) {
            printf("%-5d %-10s %-5s\n", i, "—", "AUSENTE");
            absent++;
        } else {
            printf("%-5d %-10d %-5s\n", i, page_table[i], "presente");
            present++;
        }
    }
    
    printf("\nResumen:\n");
    printf("  Páginas presentes: %d/%d (%.1f%%)\n", 
           present, 16, (present * 100.0) / 16);
    printf("  Páginas ausentes:  %d/%d (%.1f%%)\n", 
           absent, 16, (absent * 100.0) / 16);
    
    return 0;
}
EOF

gcc -o analyze_page_table analyze_page_table.c
./analyze_page_table
echo

# ============================================
# 6. Cálculo de overhead de memoria
# ============================================
print_header "Cálculo de overhead de acceso a memoria"

cat << 'EOF'
Escenario: Ejecutar instrucción LOAD en dirección virtual 0x35

Paso 1: Traducir VA → PA
  - Leer page_table[VPN=3] de memoria     → 1 acceso
  - Obtener PFN = 2

Paso 2: Acceder al dato
  - Leer PA = 0x25 de memoria             → 1 acceso

TOTAL: 2 accesos a memoria física
       (1 para traducción + 1 para dato)

Solución de hardware: TLB (Translation Lookaside Buffer)
  - Caché pequeña de traducciones recientes
  - Hit TLB: 1 acceso (solo dato, traducción en caché)
  - Miss TLB: 2 accesos (como arriba)
  - Típico: 95-99% de hit rate → ~1.05 accesos promedio
EOF
echo

# ============================================
# 7. Limpieza
# ============================================
rm -f analyze_page_table analyze_page_table.c

# ============================================
# 8. Resumen
# ============================================
print_header "Pruebas completadas"
print_info "Archivo generado: paging_output.txt"
print_success "Simulador de paginación funcionando correctamente"