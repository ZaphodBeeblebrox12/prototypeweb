from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'assets'/'figures'; FIG.mkdir(parents=True,exist_ok=True)
PAPER='#fbf7ef'; PANEL='#fffdf8'; INK='#29382e'; MUTED='#68766c'; GREEN='#3e6e50'; GRID='#e8e1d5'; ZONE='#efd58e'; ZEDGE='#b98e36'; DOWN='#5a6e7d'; RUST='#bd563e'; GOLD='#c69a3d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.labelsize':8,'figure.facecolor':PAPER,'axes.facecolor':PANEL,'savefig.facecolor':PAPER})

def candles(closes, seed=1, noise=.38):
    rng=np.random.default_rng(seed); c=np.array(closes,dtype=float); n=len(c)
    o=np.empty(n); h=np.empty(n); l=np.empty(n)
    o[0]=c[0]-(c[1]-c[0])*.4+rng.normal(0,.18)
    for i in range(1,n): o[i]=c[i-1]+rng.normal(0,.22)
    for i in range(n):
        # Carefully bounded wick variation; candle path is schematic and deliberate.
        upper=abs(rng.normal(.38,noise*.35)); lower=abs(rng.normal(.36,noise*.32))
        h[i]=max(o[i],c[i])+upper; l[i]=min(o[i],c[i])-lower
    return o,h,l,c

def frame(ax, zone=None, trendline=None):
    ax.set_axisbelow(True); ax.grid(axis='y',color=GRID,lw=.7); ax.grid(axis='x',color='#f3eee5',lw=.45)
    for k in ['top','right']: ax.spines[k].set_visible(False)
    for k in ['left','bottom']: ax.spines[k].set_color('#d8d0c0'); ax.spines[k].set_linewidth(.7)
    ax.tick_params(axis='both',colors=MUTED,labelsize=7,length=0,pad=4)
    if zone:
        lo,hi=zone; ax.axhspan(lo,hi,color=ZONE,alpha=.32,zorder=0); ax.axhline(lo,color=ZEDGE,lw=1,zorder=1); ax.axhline(hi,color=ZEDGE,lw=1,zorder=1)
    if trendline:
        xx,yy=trendline; ax.plot(xx,yy,color=GOLD,lw=1.4,ls=(0,(4,3)),zorder=1)
    ax.set_ylabel('Relative price',fontsize=7,color=MUTED)
    ax.set_xlabel('Bars in sequence →',fontsize=7,color=MUTED)

def draw_candles(ax, closes, seed=1, zone=None, trendline=None, overrides=None):
    o,h,l,c=candles(closes,seed)
    if overrides:
        for i,values in overrides.items():
            if 'o' in values:o[i]=values['o']
            if 'h' in values:h[i]=values['h']
            if 'l' in values:l[i]=values['l']
            if 'c' in values:c[i]=values['c']
    frame(ax,zone,trendline)
    for i,(op,hi,lo,cl) in enumerate(zip(o,h,l,c)):
        bull=cl>=op; face=PANEL if bull else DOWN; edge=GREEN if bull else DOWN
        ax.vlines(i,lo,hi,color=DOWN,lw=.9,zorder=2)
        ax.add_patch(Rectangle((i-.29,min(op,cl)),.58,max(abs(cl-op),.04),facecolor=face,edgecolor=edge,lw=.95,zorder=3))
    ax.set_xlim(-.9,len(c)-.1)
    pad=(max(h)-min(l))*.11; ax.set_ylim(min(l)-pad,max(h)+pad)
    ax.set_xticks([0,round((len(c)-1)/2),len(c)-1]); ax.set_xticklabels(['Earlier','Sequence','Later'])
    return o,h,l,c

def header(fig,title,subtitle,footer='SCHEMATIC TEACHING ILLUSTRATION · NOT MARKET DATA · NO OUTCOME IS GUARANTEED'):
    fig.suptitle(title,x=.055,y=.972,ha='left',va='top',fontsize=19,fontfamily='DejaVu Serif',color=INK)
    fig.text(.056,.925,subtitle,ha='left',va='top',fontsize=9,color=MUTED)
    fig.text(.056,.025,footer,ha='left',va='bottom',fontsize=7.2,color=MUTED,fontweight='bold')

def ann(ax,x,y,text,color=GREEN,xytext=None,ha='left'):
    if xytext is None: xytext=(x-4,y+1.1)
    ax.annotate(text,xy=(x,y),xytext=xytext,fontsize=7.5,color=color,ha=ha,va='bottom',
       arrowprops={'arrowstyle':'->','color':color,'lw':.95},bbox={'boxstyle':'round,pad=.28','fc':PANEL,'ec':color,'lw':.65,'alpha':.97},zorder=10)

def save(fig,name):
    path=FIG/name; fig.savefig(path,dpi=190,bbox_inches='tight',pad_inches=.12); plt.close(fig); print(path.name)

# FIG22: Range-edge upthrust sequence — enough pre-event context and subsequent reclaim attempt.
fig,ax=plt.subplots(figsize=(13.6,7.2)); fig.subplots_adjust(left=.07,right=.985,top=.83,bottom=.13)
header(fig,'A false upside break is a sequence, not a wick','Hold the prior range fixed. The interpretation changes as the close, return and reclaim attempt become visible.')
cl=[97.8,98.5,98.9,98.7,99.0,99.3,99.1,99.4,99.0,99.2,99.4,99.1,99.3,99.6,99.2,99.5,99.3,99.7,100.0,100.8,101.6,102.0,101.4,100.8,100.2,99.8,99.5,99.2,99.4,99.7,100.0,99.6,99.2,98.9,98.4,98.2,97.9,97.7]
o,h,l,c=draw_candles(ax,cl,seed=220,zone=(99.0,100.0),overrides={21:{'h':102.55,'c':101.15},22:{'o':101.35,'h':101.55,'l':100.45,'c':100.6},23:{'o':100.75,'h':101.0,'l':99.8,'c':100.1},30:{'o':99.4,'h':100.15,'l':99.2,'c':99.85},31:{'o':99.8,'h':100.05,'l':99.0,'c':99.25}})
ax.text(.015,.945,'PRIOR RANGE',transform=ax.transAxes,color=GREEN,fontweight='bold',fontsize=8,va='top')
ann(ax,13,99.55,'1 · repeated tests of the ceiling',GREEN,(6,102.0))
ann(ax,21,102.55,'2 · trades above the range',RUST,(17,103.45))
ann(ax,24,99.8,'3 · closes back inside',RUST,(26,102.0))
ann(ax,31,100.05,'4 · reclaim cannot hold',RUST,(31.5,101.5))
ax.text(.015,.035,'Read the evidence: prior ceiling → excursion → return inside → failed reclaim. A brief wick alone is not enough.',transform=ax.transAxes,fontsize=8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.35'})
save(fig,'FIG22_range_edge_upthrust.png')

# FIG23: Spring-like downside test and reclaim (no stop annotations).
fig,ax=plt.subplots(figsize=(13.6,7.2)); fig.subplots_adjust(left=.07,right=.985,top=.83,bottom=.13)
header(fig,'A downside failure begins below support—but is identified by the return','The low records the excursion. The close and the next response tell you whether price stayed below the range floor.')
cl=[103.1,102.6,102.2,101.8,101.1,101.3,101.0,100.8,101.1,100.9,101.2,101.0,100.7,100.9,100.6,100.3,99.8,99.3,98.7,97.8,97.1,97.6,98.3,99.1,99.8,100.3,100.1,100.5,100.8,100.6,100.9,101.2,101.5,101.8,102.2]
o,h,l,c=draw_candles(ax,cl,seed=231,zone=(99.0,100.0),overrides={20:{'o':98.2,'h':98.35,'l':96.25,'c':97.0},21:{'o':97.0,'h':98.0,'l':96.7,'c':97.7},22:{'o':97.6,'h':98.7,'l':97.4,'c':98.4},23:{'o':98.35,'h':99.35,'l':98.1,'c':99.15}})
ann(ax,20,96.25,'1 · probes below the floor',RUST,(12,96.1))
ann(ax,23,99.15,'2 · close returns into range',GREEN,(24,97.4))
ann(ax,26,100.5,'3 · later response improves',GREEN,(26,102.0))
ax.text(.015,.035,'“Spring” is shorthand for the observed sequence—not evidence of who acted or a promise of an advance.',transform=ax.transAxes,fontsize=8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.35'})
save(fig,'FIG23_spring_downside_reclaim.png')

# FIG24: Prior swing break quickly surrendered, not a large horizontal range.
fig,ax=plt.subplots(figsize=(13.6,7.2)); fig.subplots_adjust(left=.07,right=.985,top=.83,bottom=.13)
header(fig,'A pivot failure is different from a range breakout','The level is a previously visible swing high. Price takes it out, then gives it back; the response determines how strong the contradiction is.')
cl=[96.7,97.1,97.8,97.5,98.4,98.1,99.0,99.5,99.1,99.8,100.6,100.2,101.1,101.5,101.2,101.8,102.25,101.9,102.4,103.0,102.6,102.0,101.3,100.7,100.2,99.8,99.4,99.2,98.9,98.6,98.4,98.1]
# add prior pivot line near 102.5
O,H,L,C=draw_candles(ax,cl,seed=244,overrides={18:{'h':102.8},19:{'h':103.55,'c':102.6},20:{'o':102.55,'h':102.75,'l':101.65,'c':101.9}})
pivot=102.5; ax.axhline(pivot,color=ZEDGE,lw=1.15,ls=(0,(5,3)))
ann(ax,19,103.55,'1 · takes the prior swing high',GREEN,(10,104.1))
ann(ax,21,101.3,'2 · closes back below the pivot',RUST,(22,103.1))
ann(ax,27,99.0,'3 · follow-through adds weight',RUST,(24,97.7))
ax.text(.015,.035,'The pivot must be identifiable before the break. A wick above it is an attempt, not the complete failure test.',transform=ax.transAxes,fontsize=8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.35'})
save(fig,'FIG24_prior_swing_failure_test.png')

# FIG25: continuation pause breakout options; one expected continuation holds and the other breaks opposite way.
fig,axs=plt.subplots(1,2,figsize=(14.8,7.2)); fig.subplots_adjust(left=.06,right=.985,top=.83,bottom=.12,wspace=.18)
header(fig,'A pause does not promise continuation','The same broad pause can resolve as expected or against the original thesis. Name the boundary and then read the response.')
seq=[
([96.2,97.2,98.4,99.4,100.4,101.4,102.0,101.6,101.9,101.4,101.7,101.2,101.6,101.4,101.9,102.7,103.4,104.1,104.8], '01 · Expected break holds', 'Moves through upper pause edge; then holds and extends.',GREEN),
([96.2,97.2,98.4,99.4,100.4,101.4,102.0,101.6,101.9,101.4,101.7,101.2,101.6,101.4,100.8,100.0,99.3,98.6,97.8], '02 · Pause breaks the wrong way', 'Crosses the lower edge; the continuation idea loses support.',RUST)]
for i,(cl,title,sub,color) in enumerate(seq):
    ax=axs[i]
    if i==0:
        zone=(100.7,102.2)
    else:
        zone=(100.7,102.2)
    draw_candles(ax,cl,seed=255+i,zone=zone)
    ax.set_title(title,loc='left',color=color,fontweight='bold',pad=10)
    ax.text(.02,.035,sub,transform=ax.transAxes,fontsize=7.8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.35'})
    if i==0: ann(ax,15,102.7,'holds outside',GREEN,(9,104.6))
    else: ann(ax,15,100.0,'breaks opposite edge',RUST,(9,98.0))
save(fig,'FIG25_continuation_pause_outcomes.png')
