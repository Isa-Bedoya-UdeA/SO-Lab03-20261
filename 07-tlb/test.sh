#!/bin/bash
echo "=== Sección 7: TLBs ==="
cd "$(dirname "$0")"

echo ""
echo "--- Compilando ---"
gcc -O0 -o tlb_locality tlb_locality.c && echo "tlb_locality: OK"

echo ""
echo "--- Ejecutando 3 veces para promedio ---"
for i in 1 2 3; do
    echo "Run $i:"
    ./tlb_locality
    echo ""
done
