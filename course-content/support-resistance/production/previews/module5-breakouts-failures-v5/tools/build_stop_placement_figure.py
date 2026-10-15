from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'figures'/'FIG21_failed_breakout_structural_stop.png'
PAPER='#fbf7ef'; PANEL='#fffdf8'; INK='#26382f'; MUTED='#6b776e'; GREEN='#356647'; RED='#b74c35'; BLUE='#586d7b'; GOLD='#c99b3d'; ZONE='#f1e4b9'; GRID='#e9e1d3'; LINE='#d8cdb9'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig, axes=plt.subplots(1,2,figsize=(15.5,8.2),dpi=160,facecolor=PAPER)
fig.subplots_adjust(left=.045,right=.985,top=.82,bottom=.11,wspace=.12)

def draw_candles(ax, data):
    for i,(o,h,l,c) in enumerate(data):
        color=GREEN if c>=o else BLUE
        ax.vlines(i,l,h,color=BLUE,linewidth=1.3,zorder=2)
        bottom=min(o,c); height=max(abs(c-o),.035)
        ax.add_patch(Rectangle((i-.26,bottom),.52,height,facecolor=PANEL if c>=o else BLUE,edgecolor=GREEN if c>=o else BLUE,linewidth=1.4,zorder=3))
    ax.set_xlim(-.7,len(data)-.3)
    ax.grid(axis='y',color=GRID,linewidth=.8)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color(LINE); sp.set_linewidth(1)
    ax.set_facecolor(PANEL)

# left: upthrust above resistance then close back within; hypothetical short stop beyond failure extreme
left=[(8.1,8.5,7.8,8.35),(8.28,8.7,8.05,8.55),(8.50,8.84,8.32,8.40),(8.42,8.72,8.30,8.66),(8.65,9.08,8.58,8.96),(8.94,9.35,8.85,9.27),(9.25,9.62,9.14,9.54),(9.50,10.10,9.42,9.98),(9.96,10.42,9.90,10.30),(10.28,10.85,10.20,10.74),(10.72,11.20,10.62,11.05),(11.08,11.82,10.98,11.70),(11.66,11.78,10.74,10.88),(10.91,11.02,10.30,10.48),(10.50,10.62,9.92,10.10),(10.12,10.30,9.68,9.80),(9.82,10.02,9.50,9.66),(9.62,9.86,9.35,9.52)]
# right: downside push below support then reclaim, low defines structural failure extreme for hypothetical long
right=[(10.4,10.7,10.2,10.62),(10.60,10.91,10.48,10.80),(10.82,11.05,10.70,10.96),(10.95,11.24,10.83,11.12),(11.08,11.19,10.76,10.88),(10.88,10.96,10.48,10.56),(10.55,10.72,10.26,10.38),(10.4,10.50,9.75,9.88),(9.88,10.10,9.30,9.48),(9.46,9.70,8.95,9.12),(9.10,9.45,8.65,8.80),(8.84,9.58,8.78,9.42),(9.42,9.88,9.32,9.74),(9.72,10.08,9.62,9.94),(9.92,10.24,9.82,10.12),(10.10,10.45,9.98,10.30),(10.32,10.64,10.20,10.52)]
for idx,(ax,data) in enumerate(zip(axes,[left,right])):
    draw_candles(ax,data)
    ax.axhspan(9.65,10.15,color=ZONE,alpha=.55,zorder=0)
    ax.axhline(9.65,color=GOLD,linewidth=1.3,zorder=1); ax.axhline(10.15,color=GOLD,linewidth=1.3,zorder=1)
    if idx==0:
        ax.set_ylim(7.45,12.30)
        # stop line above the failure bar high
        stop=12.0
        ax.axhline(stop,color=RED,linestyle=(0,(4,3)),linewidth=1.8,zorder=5)
        ax.annotate('SL · beyond the failure high',xy=(11,stop),xytext=(12.3,12.13),color=RED,fontsize=9,ha='left',va='center',arrowprops=dict(arrowstyle='->',color=RED,lw=1.25))
        ax.scatter([11],[11.82],s=55,color=RED,zorder=6)
        ax.annotate('Failure extreme',xy=(11,11.82),xytext=(6.5,11.48),color=INK,fontsize=9,arrowprops=dict(arrowstyle='->',color=INK,lw=1.1))
        ax.annotate('Returns inside the zone',xy=(13,10.30),xytext=(14.1,10.75),color=GREEN,fontsize=9,ha='center',arrowprops=dict(arrowstyle='->',color=GREEN,lw=1.1))
        ax.set_title('FAILED UPSIDE BREAK · HYPOTHETICAL SHORT',loc='left',fontweight='bold',color=INK,pad=12,fontsize=11)
    else:
        ax.set_ylim(8.2,11.5)
        stop=8.35
        ax.axhline(stop,color=RED,linestyle=(0,(4,3)),linewidth=1.8,zorder=5)
        ax.annotate('SL · beyond the failure low',xy=(10,stop),xytext=(11.0,8.52),color=RED,fontsize=9,ha='left',va='center',arrowprops=dict(arrowstyle='->',color=RED,lw=1.25))
        ax.scatter([10],[8.65],s=55,color=RED,zorder=6)
        ax.annotate('Failure extreme',xy=(10,8.65),xytext=(5.2,8.95),color=INK,fontsize=9,arrowprops=dict(arrowstyle='->',color=INK,lw=1.1))
        ax.annotate('Reclaims support zone',xy=(11,9.58),xytext=(12.6,9.12),color=GREEN,fontsize=9,ha='center',arrowprops=dict(arrowstyle='->',color=GREEN,lw=1.1))
        ax.set_title('FAILED DOWNSIDE BREAK · HYPOTHETICAL LONG',loc='left',fontweight='bold',color=INK,pad=12,fontsize=11)
fig.suptitle('Where is the structural invalidation point?',x=.045,y=.965,ha='left',fontsize=23,color=INK,fontfamily='DejaVu Serif')
fig.text(.045,.915,'Show a stop only after the failure sequence is visible. Do not place one on ordinary breakout or retest illustrations.',ha='left',fontsize=10.5,color=MUTED)
fig.text(.045,.055,'SCHEMATIC TEACHING ILLUSTRATION · NOT MARKET DATA · STOP LEVELS ARE STRUCTURAL EXAMPLES, NOT TRADE SIGNALS',ha='left',fontsize=8.4,color=MUTED,fontweight='bold')
fig.savefig(OUT,bbox_inches='tight',facecolor=PAPER)
print(OUT)
