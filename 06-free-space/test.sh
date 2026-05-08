#!/bin/bash
echo "=== Sección 6: Gestión de Espacio Libre ==="
cd "$(dirname "$0")"

echo ""
echo "--- Compilando ---"
gcc -Wall -o fragmentation fragmentation.c && echo "fragmentation: OK"
gcc -Wall -o free_list_sim free_list_sim.c  && echo "free_list_sim: OK"

echo ""
echo "--- Ejecutando fragmentation ---"
./fragmentation

echo ""
echo "--- Ejecutando free_list_sim ---"
./free_list_sim
