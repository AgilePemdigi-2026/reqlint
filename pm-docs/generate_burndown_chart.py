"""
Script Generator Burndown Chart untuk Laporan Sprint ReqLint
Author: Tim PPL ReqLint (Kelompok 3)
"""

import matplotlib.pyplot as plt

def generate_sprint1_chart(output_path: str = "burndown_chart_sprint1.png", include_acceleration: bool = False):
    plt.figure(figsize=(8.5, 5.2), dpi=300)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=300)

    # Timeline Sprint
    sprints = ['Start', 'Sprint 1', 'Sprint 2', 'Sprint 3']
    
    # Total Effort = 22 Story Points
    # Ideal linear burn: 22 -> 14.7 -> 7.3 -> 0
    ideal_burn = [22, 14.67, 7.33, 0]

    # Garis Ideal (Estimated Effort)
    ax.plot(sprints, ideal_burn, linestyle='--', marker='s', markersize=7, 
            linewidth=2, label='Estimated Effort (Ideal Burn)', color='#d93829')

    # Label angka untuk Garis Ideal
    for x, y in zip(sprints, ideal_burn):
        pts_str = f'{y:.1f} pts' if y % 1 != 0 else f'{int(y)} pts'
        ax.annotate(pts_str, (x, y), textcoords='offset points', xytext=(0, 9),
                    ha='center', fontsize=9, fontweight='bold', color='#b3261e')

    if not include_acceleration:
        # Versi Standar: Hanya menghitung backlog resmi Sprint 1 (11 poin selesai -> sisa 11 poin)
        actual_x = ['Start', 'Sprint 1']
        actual_y = [22, 11]
        ax.plot(actual_x, actual_y, marker='s', linewidth=2.5, markersize=8, 
                label='Actual Effort (Sprint 1 Completed)', color='#1a73e8')

        ax.annotate('22 pts', ('Start', 22), textcoords='offset points', xytext=(-22, 4),
                    ha='center', fontsize=9.5, fontweight='bold', color='#1558b0')
        ax.annotate('11 pts', ('Sprint 1', 11), textcoords='offset points', xytext=(0, -18),
                    ha='center', fontsize=9.5, fontweight='bold', color='#1558b0')
        title_extra = "Sprint 1 Completed (Target Met)"
    else:
        # Versi Akselerasi: Termasuk backlog Sprint 2 & 3 yang sudah dicuri start (17 poin selesai -> sisa 5 poin)
        actual_x = ['Start', 'Sprint 1']
        actual_y = [22, 5]
        ax.plot(actual_x, actual_y, marker='s', linewidth=2.5, markersize=8, 
                label='Actual Effort (With Early Accelerations)', color='#0f9d58')

        ax.annotate('22 pts', ('Start', 22), textcoords='offset points', xytext=(-22, 4),
                    ha='center', fontsize=9.5, fontweight='bold', color='#0b8043')
        ax.annotate('5 pts (Accelerated)', ('Sprint 1', 5), textcoords='offset points', xytext=(0, -18),
                    ha='center', fontsize=9.5, fontweight='bold', color='#0b8043')
        title_extra = "Sprint 1 + Early Delivery Acceleration"

    ax.set_title(f'Burndown Chart - ReqLint Project ({title_extra})', fontsize=12.5, fontweight='bold', pad=15)
    ax.set_xlabel('Sprint Timeline', fontsize=10.5, fontweight='bold', labelpad=10)
    ax.set_ylabel('Remaining Effort (Story Points)', fontsize=10.5, fontweight='bold', labelpad=10)
    ax.set_ylim(-1, 26)
    ax.grid(True, linestyle='--', alpha=0.55)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#d0d0d0')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    generate_sprint1_chart("d:/portfolio/AI/reqlint/docs/burndown_chart_sprint1.png", include_acceleration=False)
