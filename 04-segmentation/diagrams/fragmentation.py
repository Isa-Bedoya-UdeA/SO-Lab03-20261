#!/usr/bin/env python3
"""
Visualización de Fragmentación Externa en Segmentación
Laboratorio 3 - Sistemas Operativos
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle

def draw_memory_state(ax, title, segments, total_size=512):
    """
    Dibuja el estado de la memoria física
    
    segments: lista de tuplas (inicio, tamaño, nombre, color)
    """
    ax.set_xlim(0, total_size)
    ax.set_ylim(0, 2)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Dibujar segmentos
    for start, size, name, color in segments:
        rect = Rectangle((start, 0.5), size, 1, 
                         facecolor=color, 
                         edgecolor='black', 
                         linewidth=2)
        ax.add_patch(rect)
        
        # Etiqueta
        ax.text(start + size/2, 1, name, 
               ha='center', va='center', 
               fontsize=9, fontweight='bold')
        ax.text(start + size/2, 0.3, f'{size} KB', 
               ha='center', va='center', 
               fontsize=8, color='gray')
    
    # Eje de direcciones
    ax.plot([0, total_size], [0.2, 0.2], 'k-', linewidth=1)
    for pos in [0, 128, 256, 384, total_size]:
        ax.plot([pos, pos], [0.15, 0.25], 'k-', linewidth=1)
        ax.text(pos, 0.05, f'{pos}', ha='center', fontsize=8)

# Crear figura con 4 estados
fig, axes = plt.subplots(4, 1, figsize=(14, 10))
fig.suptitle('Fragmentación Externa en Segmentación', 
             fontsize=16, fontweight='bold')

# ESTADO 1: Inicial - memoria completamente asignada
segments1 = [
    (0, 64, 'Proceso A\n(Code)', '#FF6B6B'),
    (64, 96, 'Proceso B\n(Heap)', '#4ECDC4'),
    (160, 48, 'Proceso C\n(Code)', '#45B7D1'),
    (208, 128, 'Proceso D\n(Heap)', '#FFA07A'),
    (336, 80, 'Proceso E\n(Stack)', '#98D8C8'),
    (416, 96, 'Libre', '#E8E8E8')
]
draw_memory_state(axes[0], 'Estado 1: Memoria inicial (5 procesos activos)', 
                  segments1)

# ESTADO 2: Proceso B termina
segments2 = [
    (0, 64, 'Proceso A', '#FF6B6B'),
    (64, 96, 'LIBRE', '#E8E8E8'),
    (160, 48, 'Proceso C', '#45B7D1'),
    (208, 128, 'Proceso D', '#FFA07A'),
    (336, 80, 'Proceso E', '#98D8C8'),
    (416, 96, 'Libre', '#E8E8E8')
]
draw_memory_state(axes[1], 
                  'Estado 2: Proceso B termina → hueco de 96 KB', 
                  segments2)

# ESTADO 3: Procesos C y E terminan
segments3 = [
    (0, 64, 'Proceso A', '#FF6B6B'),
    (64, 96, 'LIBRE', '#E8E8E8'),
    (160, 48, 'LIBRE', '#E8E8E8'),
    (208, 128, 'Proceso D', '#FFA07A'),
    (336, 80, 'LIBRE', '#E8E8E8'),
    (416, 96, 'LIBRE', '#E8E8E8')
]
draw_memory_state(axes[2], 
                  'Estado 3: Procesos C y E terminan → 4 huecos fragmentados', 
                  segments3)

# ESTADO 4: Intento de asignar Proceso F (150 KB)
segments4 = [
    (0, 64, 'Proceso A', '#FF6B6B'),
    (64, 96, 'LIBRE\n96 KB', '#FFE5E5'),
    (160, 48, 'LIBRE\n48 KB', '#FFE5E5'),
    (208, 128, 'Proceso D', '#FFA07A'),
    (336, 80, 'LIBRE\n80 KB', '#FFE5E5'),
    (416, 96, 'LIBRE\n96 KB', '#FFE5E5')
]
draw_memory_state(axes[3], 
                  'Estado 4: ¿Asignar Proceso F (150 KB)? ❌ IMPOSIBLE', 
                  segments4)

# Añadir análisis al último subplot
axes[3].text(256, -0.3, 
            'Memoria libre total: 96 + 48 + 80 + 96 = 320 KB\n'
            'Proceso F requiere: 150 KB\n'
            '¡Hay suficiente memoria, pero está FRAGMENTADA!',
            ha='center', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.8))

plt.tight_layout()
plt.savefig('fragmentacion_externa.png', dpi=300, bbox_inches='tight')
print("✓ Diagrama guardado como 'fragmentacion_externa.png'")
plt.show()