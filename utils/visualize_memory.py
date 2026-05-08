#!/usr/bin/env python3
"""
Herramienta de Visualización de Memoria
Laboratorio 3 - Sistemas Operativos

Genera diagramas visuales de:
1. Espacio de direcciones virtual (text, heap, stack)
2. Traducción Base & Bounds
3. Traducción con Segmentación
4. Traducción con Paginación
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import numpy as np

class MemoryVisualizer:
    """Clase para generar visualizaciones de gestión de memoria"""
    
    def __init__(self):
        self.colors = {
            'code': '#FF6B6B',
            'heap': '#4ECDC4',
            'stack': '#45B7D1',
            'data': '#FFA07A',
            'free': '#E8E8E8',
            'kernel': '#95A5A6',
            'invalid': '#FFE5E5'
        }
    
    def draw_address_space(self, filename='address_space.png'):
        """
        Dibuja el espacio de direcciones virtual de un proceso
        mostrando las regiones text, heap y stack
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        fig.suptitle('Espacio de Direcciones Virtual', 
                     fontsize=16, fontweight='bold')
        
        # ============================================
        # Panel 1: Espacio Virtual (vista lógica)
        # ============================================
        ax1.set_title('Vista Lógica del Proceso', fontweight='bold')
        ax1.set_xlim(0, 4)
        ax1.set_ylim(0, 16)
        ax1.axis('off')
        
        # Direcciones virtuales (32 bits = 4 GB)
        # Simplificado a 16 GB para visualización
        segments = [
            (0, 2, 'Code\n(text)', self.colors['code'], '0x00000000'),
            (2, 1, 'Data\n(global vars)', self.colors['data'], '0x08048000'),
            (3, 5, 'Heap\n(malloc)', self.colors['heap'], '0x08050000'),
            (8, 4, 'Libre', self.colors['free'], ''),
            (12, 3, 'Stack\n(local vars)', self.colors['stack'], '0xBFFFFFFF'),
            (15, 1, 'Kernel Space', self.colors['kernel'], '0xFFFFFFFF')
        ]
        
        for start, height, label, color, addr in segments:
            rect = FancyBboxPatch((0.5, start), 3, height,
                                  boxstyle="round,pad=0.05",
                                  facecolor=color,
                                  edgecolor='black',
                                  linewidth=2)
            ax1.add_patch(rect)
            
            ax1.text(2, start + height/2, label,
                    ha='center', va='center',
                    fontsize=11, fontweight='bold')
            
            if addr:
                ax1.text(0.3, start + height/2, addr,
                        ha='right', va='center',
                        fontsize=8, family='monospace',
                        rotation=90)
        
        # Flechas de crecimiento
        # Heap crece hacia arriba
        ax1.annotate('', xy=(3.8, 7), xytext=(3.8, 3.5),
                    arrowprops=dict(arrowstyle='->', lw=2, color='green'))
        ax1.text(3.9, 5.5, 'Heap\ncrece ↑', fontsize=9, color='green')
        
        # Stack crece hacia abajo
        ax1.annotate('', xy=(3.8, 12.5), xytext=(3.8, 14.5),
                    arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
        ax1.text(3.9, 13.5, 'Stack\ncrece ↓', fontsize=9, color='blue')
        
        # ============================================
        # Panel 2: Espacio Físico (RAM real)
        # ============================================
        ax2.set_title('Memoria Física (RAM)', fontweight='bold')
        ax2.set_xlim(0, 4)
        ax2.set_ylim(0, 16)
        ax2.axis('off')
        
        # Memoria física fragmentada (proceso A y B compartiendo)
        physical_segments = [
            (0, 1.5, 'Kernel', self.colors['kernel'], '0x00000000'),
            (1.5, 1, 'Proc A\nCode', self.colors['code'], '0x00100000'),
            (2.5, 1.5, 'Proc B\nHeap', '#9B59B6', '0x00120000'),
            (4, 2, 'Proc A\nHeap', self.colors['heap'], '0x00180000'),
            (6, 0.8, 'Libre', self.colors['free'], ''),
            (6.8, 1.2, 'Proc B\nStack', '#E67E22', '0x00240000'),
            (8, 2.5, 'Proc A\nStack', self.colors['stack'], '0x00280000'),
            (10.5, 5.5, 'Libre', self.colors['free'], '')
        ]
        
        for start, height, label, color, addr in physical_segments:
            rect = FancyBboxPatch((0.5, start), 3, height,
                                  boxstyle="round,pad=0.05",
                                  facecolor=color,
                                  edgecolor='black',
                                  linewidth=2)
            ax2.add_patch(rect)
            
            ax2.text(2, start + height/2, label,
                    ha='center', va='center',
                    fontsize=10, fontweight='bold')
            
            if addr:
                ax2.text(3.7, start + height/2, addr,
                        ha='left', va='center',
                        fontsize=7, family='monospace')
        
        ax2.text(2, -0.5, 
                'Proceso A y B comparten\nla memoria física',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Diagrama guardado como '{filename}'")
        plt.close()
    
    def draw_base_bounds_translation(self, filename='base_bounds_translation.png'):
        """
        Visualiza la traducción Base & Bounds
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('Traducción de Direcciones: Base & Bounds',
                     fontsize=16, fontweight='bold')
        
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # ============================================
        # Espacio Virtual
        # ============================================
        ax.text(2, 11, 'Espacio Virtual', fontsize=12, fontweight='bold')
        
        # Dibujar espacio virtual (bounds = 64)
        virtual_rect = Rectangle((0.5, 7), 3, 3,
                                 facecolor=self.colors['heap'],
                                 edgecolor='black', linewidth=2)
        ax.add_patch(virtual_rect)
        
        ax.text(2, 8.5, 'Proceso A\n(64 bytes)', ha='center', va='center',
               fontsize=10, fontweight='bold')
        
        # Direcciones virtuales
        for va in [0, 32, 63]:
            y_pos = 7 + (va / 63) * 3
            ax.plot([0.3, 0.5], [y_pos, y_pos], 'k-', linewidth=1)
            ax.text(0.2, y_pos, f'VA={va}', ha='right', fontsize=8,
                   family='monospace')
        
        # ============================================
        # Hardware (Registros)
        # ============================================
        ax.text(7, 11, 'Hardware (MMU)', fontsize=12, fontweight='bold')
        
        # Registro Base
        base_box = FancyBboxPatch((5.5, 9), 3, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor='lightblue',
                                  edgecolor='black', linewidth=2)
        ax.add_patch(base_box)
        ax.text(7, 9.4, 'Base = 32 KB', ha='center', va='center',
               fontsize=10, fontweight='bold', family='monospace')
        
        # Registro Bounds
        bounds_box = FancyBboxPatch((5.5, 8), 3, 0.8,
                                    boxstyle="round,pad=0.1",
                                    facecolor='lightcoral',
                                    edgecolor='black', linewidth=2)
        ax.add_patch(bounds_box)
        ax.text(7, 8.4, 'Bounds = 64 bytes', ha='center', va='center',
               fontsize=10, fontweight='bold', family='monospace')
        
        # Fórmula
        formula_box = FancyBboxPatch((5, 6.5), 4.5, 1.2,
                                     boxstyle="round,pad=0.1",
                                     facecolor='lightyellow',
                                     edgecolor='black', linewidth=2)
        ax.add_patch(formula_box)
        ax.text(7.25, 7.4, 'PA = VA + base', ha='center', va='top',
               fontsize=11, fontweight='bold', family='monospace')
        ax.text(7.25, 6.9, 'si 0 ≤ VA < bounds', ha='center', va='top',
               fontsize=9, style='italic')
        
        # ============================================
        # Memoria Física
        # ============================================
        ax.text(14, 11, 'Memoria Física', fontsize=12, fontweight='bold')
        
        # Memoria física completa
        physical_total = Rectangle((12, 1), 4, 9,
                                   facecolor=self.colors['free'],
                                   edgecolor='black', linewidth=1,
                                   linestyle='--')
        ax.add_patch(physical_total)
        
        # Región del Proceso A (base=32, bounds=64)
        proc_a_rect = Rectangle((12, 4), 4, 3,
                               facecolor=self.colors['heap'],
                               edgecolor='black', linewidth=2)
        ax.add_patch(proc_a_rect)
        
        ax.text(14, 5.5, 'Proceso A', ha='center', va='center',
               fontsize=10, fontweight='bold')
        
        # Direcciones físicas
        for offset, pa in [(0, 32), (32, 64), (63, 95)]:
            y_pos = 4 + (offset / 63) * 3
            ax.plot([16, 16.2], [y_pos, y_pos], 'k-', linewidth=1)
            ax.text(16.3, y_pos, f'PA={pa}', ha='left', fontsize=8,
                   family='monospace')
        
        # Etiquetas de otras regiones
        ax.text(14, 8, 'Libre\n(otros procesos)', ha='center', va='center',
               fontsize=9, style='italic', color='gray')
        ax.text(14, 2.5, 'Libre\n(otros procesos)', ha='center', va='center',
               fontsize=9, style='italic', color='gray')
        
        # ============================================
        # Flechas de traducción
        # ============================================
        # VA=0 → PA=32
        arrow1 = FancyArrowPatch((3.5, 7.1), (12, 4.1),
                                arrowstyle='->', lw=2, color='green',
                                connectionstyle="arc3,rad=0.3")
        ax.add_patch(arrow1)
        ax.text(7.5, 6, 'VA=0\n→ PA=32', ha='center', fontsize=8,
               color='green', fontweight='bold')
        
        # VA=32 → PA=64
        arrow2 = FancyArrowPatch((3.5, 8.5), (12, 5.5),
                                arrowstyle='->', lw=2, color='blue',
                                connectionstyle="arc3,rad=0.1")
        ax.add_patch(arrow2)
        ax.text(8, 7.5, 'VA=32\n→ PA=64', ha='center', fontsize=8,
               color='blue', fontweight='bold')
        
        # VA=63 → PA=95
        arrow3 = FancyArrowPatch((3.5, 9.9), (12, 6.9),
                                arrowstyle='->', lw=2, color='red',
                                connectionstyle="arc3,rad=-0.1")
        ax.add_patch(arrow3)
        ax.text(7.5, 9, 'VA=63\n→ PA=95', ha='center', fontsize=8,
               color='red', fontweight='bold')
        
        # ============================================
        # Ejemplo de excepción
        # ============================================
        ax.text(2, 5.5, '❌ EXCEPCIÓN', fontsize=11, fontweight='bold',
               color='red')
        ax.text(2, 5, 'VA=64 viola bounds', ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='#FFE5E5'))
        ax.text(2, 4.5, 'VA=100 viola bounds', ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='#FFE5E5'))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Diagrama guardado como '{filename}'")
        plt.close()
    
    def draw_paging_translation(self, filename='paging_translation.png'):
        """
        Visualiza la traducción con Paginación
        """
        fig, ax = plt.subplots(figsize=(16, 10))
        fig.suptitle('Traducción de Direcciones: Paginación',
                     fontsize=16, fontweight='bold')
        
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 14)
        ax.axis('off')
        
        # ============================================
        # Dirección Virtual (descomposición)
        # ============================================
        ax.text(2, 13, 'Dirección Virtual (32 bits)', 
               fontsize=12, fontweight='bold')
        
        # VA ejemplo: 0x00403A0
        va_box = Rectangle((0.5, 11.5), 3.5, 1,
                          facecolor='lightblue',
                          edgecolor='black', linewidth=2)
        ax.add_patch(va_box)
        
        # VPN parte
        vpn_section = Rectangle((0.5, 11.5), 2.5, 1,
                               facecolor='#FFE5B4',
                               edgecolor='black', linewidth=2)
        ax.add_patch(vpn_section)
        ax.text(1.75, 12, 'VPN', ha='center', va='center',
               fontsize=10, fontweight='bold')
        ax.text(1.75, 11.7, '20 bits', ha='center', va='center',
               fontsize=8, style='italic')
        
        # Offset parte
        offset_section = Rectangle((3, 11.5), 1, 1,
                                   facecolor='#B4E5FF',
                                   edgecolor='black', linewidth=2)
        ax.add_patch(offset_section)
        ax.text(3.5, 12, 'Offset', ha='center', va='center',
               fontsize=10, fontweight='bold')
        ax.text(3.5, 11.7, '12 bits', ha='center', va='center',
               fontsize=8, style='italic')
        
        # Ejemplo concreto
        ax.text(2, 10.8, 'Ejemplo: VA = 0x00403A0', 
               fontsize=9, family='monospace',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
        ax.text(2, 10.4, 'VPN = 0x004 = 4', 
               fontsize=8, family='monospace')
        ax.text(2, 10.1, 'Offset = 0x3A0 = 928', 
               fontsize=8, family='monospace')
        
        # ============================================
        # Tabla de Páginas
        # ============================================
        ax.text(7, 13, 'Page Table', fontsize=12, fontweight='bold')
        
        # Dibujar tabla (solo algunas entradas)
        page_table = [
            (0, 3, True),
            (1, -1, False),
            (2, 7, True),
            (3, 2, True),
            (4, 5, True),  # ← Nuestra traducción
            (5, -1, False),
        ]
        
        y_start = 11.5
        for vpn, pfn, valid in page_table:
            y = y_start - vpn * 0.6
            
            # Caja de entrada
            color = self.colors['heap'] if valid else self.colors['invalid']
            entry_box = Rectangle((5.5, y), 1.5, 0.5,
                                 facecolor=color,
                                 edgecolor='black', linewidth=1)
            ax.add_patch(entry_box)
            
            # VPN
            ax.text(5.8, y + 0.25, f'{vpn}', ha='left', va='center',
                   fontsize=8, family='monospace')
            
            # PFN o fault
            if valid:
                ax.text(6.6, y + 0.25, f'→ {pfn}', ha='right', va='center',
                       fontsize=8, family='monospace', fontweight='bold')
            else:
                ax.text(6.6, y + 0.25, '✗', ha='right', va='center',
                       fontsize=10, color='red')
        
        # Highlight de entrada usada (VPN=4)
        highlight = Rectangle((5.4, y_start - 4*0.6 - 0.05), 1.7, 0.6,
                             facecolor='none',
                             edgecolor='green', linewidth=3)
        ax.add_patch(highlight)
        
        # ============================================
        # Dirección Física (construcción)
        # ============================================
        ax.text(13, 13, 'Dirección Física', fontsize=12, fontweight='bold')
        
        # PA construcción
        pa_box = Rectangle((11.5, 11.5), 3.5, 1,
                          facecolor='lightgreen',
                          edgecolor='black', linewidth=2)
        ax.add_patch(pa_box)
        
        # PFN parte
        pfn_section = Rectangle((11.5, 11.5), 1.5, 1,
                               facecolor='#FFD4B4',
                               edgecolor='black', linewidth=2)
        ax.add_patch(pfn_section)
        ax.text(12.25, 12, 'PFN', ha='center', va='center',
               fontsize=10, fontweight='bold')
        ax.text(12.25, 11.7, '8 bits', ha='center', va='center',
               fontsize=8, style='italic')
        
        # Offset parte (copiado)
        offset_section2 = Rectangle((13, 11.5), 2, 1,
                                    facecolor='#B4E5FF',
                                    edgecolor='black', linewidth=2)
        ax.add_patch(offset_section2)
        ax.text(14, 12, 'Offset', ha='center', va='center',
               fontsize=10, fontweight='bold')
        ax.text(14, 11.7, '12 bits\n(copiado)', ha='center', va='center',
               fontsize=7, style='italic')
        
        # Resultado
        ax.text(13, 10.8, 'PA = 0x053A0', 
               fontsize=9, family='monospace', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        ax.text(13, 10.4, 'PFN = 5', fontsize=8, family='monospace')
        ax.text(13, 10.1, 'Offset = 0x3A0 (sin cambios)', 
               fontsize=8, family='monospace')
        
        # ============================================
        # Flechas de traducción
        # ============================================
        # VA → Tabla (VPN)
        arrow1 = FancyArrowPatch((4, 11.8), (5.5, 11.4),
                                arrowstyle='->', lw=2, color='blue',
                                connectionstyle="arc3,rad=0.2")
        ax.add_patch(arrow1)
        ax.text(4.5, 11.5, 'VPN\nindexar', ha='center', fontsize=7,
               color='blue')
        
        # Tabla → PA (PFN)
        arrow2 = FancyArrowPatch((7, 9.1), (11.5, 11.8),
                                arrowstyle='->', lw=2, color='green',
                                connectionstyle="arc3,rad=-0.3")
        ax.add_patch(arrow2)
        ax.text(9, 10, 'PFN\nobtenido', ha='center', fontsize=7,
               color='green', fontweight='bold')
        
        # Offset copiado
        arrow3 = FancyArrowPatch((3.5, 11.2), (13, 11.2),
                                arrowstyle='->', lw=1.5, color='purple',
                                linestyle='dashed',
                                connectionstyle="arc3,rad=0.5")
        ax.add_patch(arrow3)
        ax.text(8, 9.5, 'Offset copiado\nsin traducción', 
               ha='center', fontsize=7, color='purple', style='italic')
        
        # ============================================
        # Memoria Física (vista simplificada)
        # ============================================
        ax.text(10, 7.5, 'Memoria Física (marcos)', 
               fontsize=11, fontweight='bold')
        
        # Dibujar algunos marcos
        frames = [
            (0, 'Frame 0', self.colors['code']),
            (2, 'Frame 2', self.colors['data']),
            (3, 'Frame 3', self.colors['heap']),
            (5, 'Frame 5\n(nuestro acceso)', self.colors['stack']),
            (7, 'Frame 7', '#9B59B6'),
        ]
        
        x_start = 8.5
        for pfn, label, color in frames:
            x = x_start + pfn * 1.2
            frame_box = Rectangle((x, 6), 1, 1,
                                 facecolor=color,
                                 edgecolor='black', linewidth=1)
            ax.add_patch(frame_box)
            ax.text(x + 0.5, 6.5, label, ha='center', va='center',
                   fontsize=7)
            ax.text(x + 0.5, 5.7, f'PFN={pfn}', ha='center', va='center',
                   fontsize=6, family='monospace')
        
        # Highlight frame 5
        highlight_frame = Rectangle((x_start + 5*1.2 - 0.05, 5.95), 1.1, 1.1,
                                   facecolor='none',
                                   edgecolor='green', linewidth=3)
        ax.add_patch(highlight_frame)
        
        # ============================================
        # Notas al pie
        # ============================================
        notes = (
            "Nota: La traducción requiere 2 accesos a memoria:\n"
            "  1. Leer page_table[VPN] para obtener PFN\n"
            "  2. Acceder a la dirección física PA\n"
            "Solución: TLB (Translation Lookaside Buffer) cachea traducciones"
        )
        ax.text(10, 3.5, notes, ha='center', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='#FFF9E6', alpha=0.8),
               family='monospace')
        
        # Page Fault ejemplo
        ax.text(2, 8, '❌ PAGE FAULT', fontsize=10, fontweight='bold',
               color='red')
        ax.text(2, 7.5, 'VPN=1 → PTE.valid=0', ha='center', fontsize=8,
               family='monospace',
               bbox=dict(boxstyle='round', facecolor='#FFE5E5'))
        ax.text(2, 7, 'SO carga página desde disco', ha='center', fontsize=7,
               style='italic', color='red')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Diagrama guardado como '{filename}'")
        plt.close()

    def draw_all(self):
        """Genera todas las visualizaciones"""
        print("\n" + "="*50)
        print("Generando visualizaciones de memoria...")
        print("="*50 + "\n")
        
        self.draw_address_space()
        self.draw_base_bounds_translation()
        self.draw_paging_translation()
        
        print("\n" + "="*50)
        print("✓ Todas las visualizaciones completadas")
        print("="*50)


if __name__ == '__main__':
    visualizer = MemoryVisualizer()
    visualizer.draw_all()
    
    print("\nArchivos generados:")
    print("  - address_space.png")
    print("  - base_bounds_translation.png")
    print("  - paging_translation.png")