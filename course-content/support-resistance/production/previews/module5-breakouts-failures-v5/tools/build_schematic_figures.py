from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'assets'/'figures'; FIG.mkdir(parents=True,exist_ok=True)
PAPER='#fbf7ef'; PANEL='#fffdf8'; INK='#29382e'; MUTED='#68766c'; GREEN='#3e6e50'; GREEN_SOFT='#dce9d8'; GRID='#e8e1d5'; ZONE='#efd58e'; ZEDGE='#b98e36'; DOWN='#5a6e7d'; RUST='#bd563e'; RUST_SOFT='#f5e1d9'; GOLD='#c69a3d'; GREYVOL='#b9b6aa'; BLUE='#8ba4b0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':8,'figure.facecolor':PAPER,'axes.facecolor':PANEL,'savefig.facecolor':PAPER})

def make_ohlc(anchors, n=40, seed=1, noise=.44, vol_scale=1.0, gap_points=None):
    rng=np.random.default_rng(seed)
    ax=np.array([a[0] for a in anchors],float)*(n-1); ay=np.array([a[1] for a in anchors],float)
    x=np.arange(n)
    base=np.interp(x,ax,ay)
    raw=rng.normal(0,1,n)
    smooth=np.convolve(raw,np.array([.18,.64,.18]),mode='same')
    close=base+smooth*noise
    opens=np.empty(n); highs=np.empty(n); lows=np.empty(n)
    gaps=gap_points or {}
    for i in range(n):
        prev=close[i-1] if i else close[i]-(base[1]-base[0])+rng.normal(0,.25)
        opens[i]=prev+rng.normal(0,.28)
        if i in gaps: opens[i]=gaps[i]
        # Let close remain attached to designed structural path but keep candle bodies variable.
        if i in gaps: close[i]+=rng.normal(0,.18)
        upwick=abs(rng.normal(.47,.23)); downwick=abs(rng.normal(.45,.22))
        highs[i]=max(opens[i],close[i])+upwick
        lows[i]=min(opens[i],close[i])-downwick
    vol=(.72+np.abs(rng.normal(.0,.26,n))+np.abs(np.diff(np.r_[close[0],close]))*.45)*100*vol_scale
    return {'Open':opens,'High':highs,'Low':lows,'Close':close,'Volume':vol}

def style_ax(ax, show_y=True):
    ax.set_facecolor(PANEL); ax.set_axisbelow(True)
    ax.grid(axis='y',color=GRID,lw=.7); ax.grid(axis='x',color='#f3eee5',lw=.45)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    for s in ('left','bottom'): ax.spines[s].set_color('#d8d0c0'); ax.spines[s].set_linewidth(.65)
    ax.tick_params(axis='both',colors=MUTED,labelsize=7,length=0,pad=4)
    ax.set_xlim(-.8, None)
    if not show_y: ax.set_yticklabels([])

def draw_candles(ax, d, zone=None, show_x=False, width=.58, alpha=1.0):
    n=len(d['Close']); xs=np.arange(n)
    if zone:
        lo,hi=zone; ax.axhspan(lo,hi,color=ZONE,alpha=.32,zorder=0)
        ax.axhline(lo,color=ZEDGE,lw=.95,zorder=1); ax.axhline(hi,color=ZEDGE,lw=.95,zorder=1)
    for i,(o,h,l,c) in enumerate(zip(d['Open'],d['High'],d['Low'],d['Close'])):
        bullish=c>=o; fill=PANEL if bullish else DOWN; edge=GREEN if bullish else DOWN
        ax.vlines(i,l,h,color=DOWN,linewidth=.9,alpha=alpha,zorder=2)
        rect=Rectangle((i-width/2,min(o,c)),width,max(abs(c-o),.035),facecolor=fill,edgecolor=edge,linewidth=.9,alpha=alpha,zorder=3)
        ax.add_patch(rect)
    if show_x:
        ticks=[0,round((n-1)/2),n-1]
        ax.set_xticks(ticks); ax.set_xticklabels(['Earlier','Sequence','Later'])
    else:
        ax.set_xticks([0,n-1]); ax.set_xticklabels(['Earlier','Later'])
    # no pseudo-precision in the charts: label relative/schematic price
    ax.set_ylabel('Relative price',fontsize=7,color=MUTED,labelpad=5)
    style_ax(ax)

def fighead(fig,title,sub,footer='SCHEMATIC TEACHING ILLUSTRATION · NOT MARKET DATA · NO OUTCOME IS GUARANTEED'):
    fig.suptitle(title,x=.055,y=.978,ha='left',va='top',fontsize=19,fontfamily='DejaVu Serif',color=INK)
    fig.text(.056,.931,sub,ha='left',va='top',fontsize=9,color=MUTED)
    fig.text(.056,.025,footer,ha='left',va='bottom',fontsize=7.3,color=MUTED,fontweight='bold')

def save(fig,name):
    path=FIG/name; fig.savefig(path,dpi=180,bbox_inches='tight',pad_inches=.12); plt.close(fig); return path

def annotate(ax, x,y,text,color=GREEN,xytext=None,ha='left'):
    if xytext is None: xytext=(max(.5,x-3),y+1.3)
    ax.annotate(text,xy=(x,y),xytext=xytext,fontsize=7.6,color=color,ha=ha,va='bottom',
        arrowprops={'arrowstyle':'->','color':color,'lw':.9},bbox={'boxstyle':'round,pad=.25','fc':PANEL,'ec':color,'lw':.5,'alpha':.96},zorder=10)

# FIG01: evidence ladder, three 36-bar tapes, common prior range
fig,axs=plt.subplots(1,3,figsize=(15.2,6.8)); fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.22)
fighead(fig,'A breakout is an evidence sequence—not a candle shape','Keep the same prior zone fixed. Each panel changes what the candles establish, not what the future must do.')
zone=(99.4,101.0)
seqs=[
 ([(0,97.4),(.12,98.6),(.24,99.7),(.38,98.9),(.52,99.8),(.64,99.4),(.76,99.8),(.86,100.1),(.90,99.6),(1,99.4)],'01 · Intrabar excursion','High moved through; close returned inside.',101.9),
 ([(0,97.4),(.12,98.6),(.24,99.7),(.38,98.9),(.52,99.8),(.64,99.4),(.76,100.1),(.84,101.7),(.90,100.5),(1,99.8)],'02 · Close outside','The close adds evidence; the return complicates it.',None),
 ([(0,97.4),(.12,98.6),(.24,99.7),(.38,98.9),(.52,99.8),(.64,99.4),(.76,100.1),(.83,101.8),(.9,102.6),(1,103.0)],'03 · Follow-through','Later bars continue to hold beyond the band.',None)]
for i,(anc,title,sub,wick) in enumerate(seqs):
    d=make_ohlc(anc,40,seed=40+i,noise=.36)
    if wick is not None:
        k=35; d['High'][k]=102.1; d['Close'][k]=100.5; d['Open'][k]=99.8; d['Low'][k]=99.35
    draw_candles(axs[i],d,zone,show_x=True)
    axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10)
    axs[i].text(.02,.035,sub,transform=axs[i].transAxes,ha='left',va='bottom',fontsize=7.3,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
    axs[i].set_ylim(95.3,104.4)
save(fig,'FIG01_breakout_evidence_ladder.png')

# FIG02: confirmation filters with same path and thresholds
fig,axs=plt.subplots(1,3,figsize=(15.2,6.8)); fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.22)
fighead(fig,'Confirmation filters move the decision point; they do not remove risk','A stricter rule may avoid some borderline crosses, recognise the move later, and still admit a move that fails.')
anc=[(0,97.0),(.12,99.0),(.25,98.5),(.38,99.6),(.52,99.0),(.64,99.7),(.72,101.8),(.79,102.6),(.86,100.8),(.92,99.4),(1,98.7)]
for i,(title,subtitle,cut,mark) in enumerate([
 ('01 · One close outside','Earlier recognition · still provisional',29,'close'),
 ('02 · Two closes outside','Later recognition · still provisional',32,'two'),
 ('03 · Require a return test','Some clean moves never return',33,'retest')]):
    d=make_ohlc(anc,42,seed=110,noise=.28)
    draw_candles(axs[i],d,(99.5,100.7),show_x=True)
    axs[i].set_ylim(95.6,104.2); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10)
    if i==0:
        axs[i].axvline(29,color=GREEN,ls='--',lw=1); annotate(axs[i],29,d['Close'][29],'First close',GREEN,(20,103.3))
    elif i==1:
        axs[i].axvline(32,color=GOLD,ls='--',lw=1); annotate(axs[i],32,d['Close'][32],'Second close',GOLD,(24,103.25))
    else:
        axs[i].axvline(31,color=RUST,ls='--',lw=1); annotate(axs[i],31,d['Low'][31],'No return needed',RUST,(20,103.35))
    axs[i].text(.02,.035,subtitle,transform=axs[i].transAxes,fontsize=7.3,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG02_filter_tradeoffs.png')

# FIG03: same local move in different context
fig,axs=plt.subplots(1,2,figsize=(14.4,6.9)); fig.subplots_adjust(left=.06,right=.98,top=.82,bottom=.12,wspace=.2)
fighead(fig,'The local breakout may not be the larger breakout','Changing the viewing scale changes the question. Mark the structure you are actually interpreting.')
anc=[(0,98.0),(.1,100),(.18,98.9),(.3,101),(.4,99.8),(.5,101.2),(.58,100.1),(.65,101.3),(.72,100.9),(.79,102.2),(.88,103.5),(1,104.4)]
d=make_ohlc(anc,58,seed=221,noise=.5)
# local zoom of final 32 bars
local={k:v[-32:] for k,v in d.items()}
draw_candles(axs[0],local,(101.0,102.0),show_x=True); axs[0].set_ylim(97.6,105.7)
axs[0].set_title('01 · Local view',loc='left',color=INK,fontweight='bold',pad=10)
axs[0].text(.02,.035,'A local swing high is crossed.',transform=axs[0].transAxes,fontsize=8,color=GREEN,bbox={'fc':PANEL,'ec':'#d4e2cf','boxstyle':'round,pad=.3'})
draw_candles(axs[1],d,(105.7,107.0),show_x=True); axs[1].axhspan(96.4,107.0,color='#e8e0cb',alpha=.18,zorder=-1); axs[1].set_ylim(95.5,109.2)
axs[1].set_title('02 · Wider context',loc='left',color=INK,fontweight='bold',pad=10)
axs[1].axhspan(97.5,98.5,color=ZONE,alpha=.25); axs[1].axhline(97.5,color=ZEDGE,lw=.8); axs[1].axhline(98.5,color=ZEDGE,lw=.8)
axs[1].text(.02,.035,'Still below the broader range ceiling.',transform=axs[1].transAxes,fontsize=8,color=RUST,bbox={'fc':PANEL,'ec':'#ead0c8','boxstyle':'round,pad=.3'})
# Actually broad resistance is at 105.7-107.0 and price at 104.4; annotate
annotate(axs[1],53,104.4,'Local break remains inside\nthe wider range',(RUST), (33,108.0))
save(fig,'FIG03_context_changes_the_question.png')

# FIG04: four stage sequence of break-return-response
fig,axs=plt.subplots(1,4,figsize=(16.5,6.2)); fig.subplots_adjust(left=.045,right=.99,top=.82,bottom=.13,wspace=.18)
fighead(fig,'Break. Return. Response. Keep them separate.','A retest is only a description of the return; the reaction that follows carries the next piece of evidence.')
anc=[(0,96.8),(.10,98.8),(.2,99.3),(.3,98.9),(.4,99.5),(.52,100.1),(.6,102.6),(.7,103.4),(.78,101.8),(.84,100.2),(.91,101.6),(1,102.9)]
d=make_ohlc(anc,45,seed=309,noise=.34)
limits=[28,33,38,45]
titles=['01 · Before the break','02 · The break','03 · Return to area','04 · Response develops']
subs=['Define the boundary first.','Price closes beyond it.','Does it touch, enter or cross?','Hold, fail—or still unclear?']
for i,(n,t,sub) in enumerate(zip(limits,titles,subs)):
    dd={k:v[:n] for k,v in d.items()}; draw_candles(axs[i],dd,(99.5,101.0),show_x=True); axs[i].set_ylim(96,105.4); axs[i].set_title(t,loc='left',color=INK,fontweight='bold',pad=8)
    axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.2,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG04_break_return_response.png')

# FIG05: three retest outcomes long sequences
fig,axs=plt.subplots(1,3,figsize=(15.4,7)); fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.22)
fighead(fig,'Three returns that share a name—but not a meaning','Compare the response after the return. The original zone stays fixed across each sequence.')
seq=[
 ([(0,95.5),(.14,97.2),(.28,99.4),(.42,100),(.52,102.6),(.62,103.1),(.73,101.0),(.8,100.3),(.88,102.4),(1,104)],'01 · Holds beyond','Return enters the near edge; later bars remain above.'),
 ([(0,95.5),(.14,97.2),(.28,99.4),(.42,100),(.52,102.6),(.62,103.1),(.73,100.3),(.82,98.8),(.9,97.5),(1,96.5)],'02 · Re-enters range','Return crosses through; continuation thesis weakens.'),
 ([(0,95.5),(.14,97.2),(.28,99.4),(.42,100),(.52,102.6),(.62,101.0),(.7,100.2),(.8,101.6),(.9,100.4),(1,100.8)],'03 · Inconclusive','Repeated overlap; do not force a clean verdict.')]
for i,(anc,title,sub) in enumerate(seq):
    d=make_ohlc(anc,45,seed=450+i,noise=.38); draw_candles(axs[i],d,(99.5,101.0),show_x=True); axs[i].set_ylim(94.6,105.4); axs[i].set_title(title,loc='left',color=GREEN if i==0 else RUST if i==1 else INK,fontweight='bold',pad=10); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.2,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG05_three_retest_outcomes.png')

# FIG06: no retest/delayed/shallow/deep return 4 panels
fig,axs=plt.subplots(2,2,figsize=(14.6,9.1)); fig.subplots_adjust(left=.06,right=.985,top=.86,bottom=.09,wspace=.18,hspace=.28)
fighead(fig,'The market does not owe you a retest','No return, a delayed return, a shallow touch and a deeper retest are different paths—not grades of correctness.')
seq=[
 ([(0,96),(.18,98.2),(.34,99.7),(.48,100),(.6,102.0),(.72,103.1),(.84,104.8),(1,106)],'A · No retest','Can continue without returning.'),
 ([(0,96),(.18,98.2),(.34,99.7),(.48,100),(.6,103.0),(.74,105.0),(.82,104.1),(.90,105.3),(1,106)],'B · Delayed return','The return happens after additional distance.'),
 ([(0,96),(.18,98.2),(.34,99.7),(.48,100),(.6,103.0),(.72,102.4),(.8,101.1),(.89,102.8),(1,104.4)],'C · Shallow return','Touches the edge, then moves away.'),
 ([(0,96),(.18,98.2),(.34,99.7),(.48,100),(.6,103.0),(.72,101.1),(.80,99.9),(.88,101.8),(1,103.6)],'D · Deep return, reclaim','Enters the band; later response matters.')]
for i,(anc,title,sub) in enumerate(seq):
    ax=axs.flat[i]; d=make_ohlc(anc,42,seed=600+i,noise=.35); draw_candles(ax,d,(99.5,101.0),show_x=True); ax.set_ylim(95,108); ax.set_title(title,loc='left',color=INK,fontweight='bold',pad=8); ax.text(.02,.035,sub,transform=ax.transAxes,fontsize=7.4,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG06_retest_is_not_owed.png')

# FIG07: after failed breakout, 3 different paths
fig,axs=plt.subplots(1,3,figsize=(15.4,6.9)); fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.22)
fighead(fig,'Failure changes the questions; it does not choose the next path','After a move back inside the range, price may travel, stall, or reclaim the boundary again.')
seq=[
 ([(0,97.0),(.18,99),(.35,100),(.48,102.8),(.58,99.2),(.68,97.9),(.78,96.1),(.9,94.9),(1,94)],'01 · Continues through range','Possible opposite movement; not guaranteed.'),
 ([(0,97.0),(.18,99),(.35,100),(.48,102.8),(.58,99.2),(.68,100.1),(.78,98.8),(.9,99.9),(1,99.0)],'02 · Chops around the area','A failure label may be premature if evidence stays mixed.'),
 ([(0,97.0),(.18,99),(.35,100),(.48,102.8),(.58,99.2),(.68,100.4),(.78,102.0),(.9,103.0),(1,104)],'03 · Reclaims the boundary','The first failure interpretation can itself be challenged.')]
for i,(anc,title,sub) in enumerate(seq):
    d=make_ohlc(anc,45,seed=720+i,noise=.36); draw_candles(axs[i],d,(99.5,101),show_x=True); axs[i].set_ylim(93.5,106); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.1,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG07_failure_is_not_reverse_signal.png')

# FIG08 improved volume matrix (2x2, many candles + volume subcharts)
fig=plt.figure(figsize=(16.4,11.2)); fig.subplots_adjust(left=.06,right=.985,top=.89,bottom=.07,hspace=.3,wspace=.18)
fighead(fig,'Volume can add context; it does not decide the outcome','Compare price behaviour first. Volume is participation recorded by this feed—not a measure of buyer/seller intent.')
gs=fig.add_gridspec(2,2)
vol_cases=[
 ([(0,97),(.14,98.7),(.3,99.3),(.44,99.7),(.55,101.8),(.67,102.4),(.81,102),(.9,103.3),(1,104.7)],'PRICE HOLDS · VOLUME EXPANDS',True,True),
 ([(0,97),(.14,98.7),(.3,99.3),(.44,99.7),(.55,101.8),(.67,102.1),(.79,100.1),(.9,98.8),(1,97.5)],'PRICE FAILS · VOLUME EXPANDS',False,True),
 ([(0,97),(.14,98.7),(.3,99.3),(.44,99.7),(.55,101.8),(.67,102.4),(.81,102),( .9,103.3),(1,104.7)],'PRICE HOLDS · VOLUME MUTED',True,False),
 ([(0,97),(.14,98.7),(.3,99.3),(.44,99.7),(.55,101.8),(.67,102.1),(.79,100.1),(.9,98.8),(1,97.5)],'PRICE FAILS · VOLUME MUTED',False,False)]
for i,(anc,title,holds,expanded) in enumerate(vol_cases):
    cell=gs[i//2,i%2].subgridspec(2,1,height_ratios=[3.2,1.0],hspace=.05)
    ax=fig.add_subplot(cell[0]); vax=fig.add_subplot(cell[1],sharex=ax)
    d=make_ohlc(anc,36,seed=850+i,noise=.33)
    # override volume pattern to clearly test context, while keeping labels explicitly illustrative
    rng=np.random.default_rng(855+i); volume=70+rng.uniform(5,15,36)
    if expanded:
        volume[20:25]=rng.uniform(125,175,5); volume[28:34]=rng.uniform(110,160,6)
    else:
        volume[20:25]=rng.uniform(65,92,5); volume[28:34]=rng.uniform(58,85,6)
    d['Volume']=volume
    draw_candles(ax,d,(99.5,101),show_x=False); ax.set_ylabel('Relative price',fontsize=7,color=MUTED); ax.set_xticklabels([]); ax.set_ylim(95.8,105.4); ax.set_title(title,loc='left',color=GREEN if holds else RUST,fontweight='bold',pad=6)
    colors=[GREEN if d['Close'][k]>=d['Open'][k] else DOWN for k in range(36)]
    vax.bar(np.arange(36),volume,width=.62,color=colors,alpha=.7); vax.set_ylim(0,200); vax.grid(axis='y',color=GRID,lw=.55); vax.set_facecolor(PANEL); vax.set_ylabel('Vol.',fontsize=7,color=MUTED)
    for s in ('top','right'):vax.spines[s].set_visible(False)
    for s in ('left','bottom'):vax.spines[s].set_color('#d8d0c0')
    vax.tick_params(axis='both',colors=MUTED,labelsize=6,length=0); vax.set_xticks([0,18,35]); vax.set_xticklabels(['Earlier','Sequence','Later'])
    vax.text(.995,.08,'Illustrative volume',transform=vax.transAxes,ha='right',va='bottom',fontsize=6.6,color=MUTED)
save(fig,'FIG08_volume_context_not_gate.png')

# FIG09 detailed decision timeline 4 charts and worksheet prompts
fig,axs=plt.subplots(1,4,figsize=(16.5,6.7)); fig.subplots_adjust(left=.045,right=.99,top=.83,bottom=.12,wspace=.18)
fighead(fig,'Preserve the decision before the outcome','The point is not to predict the last panel. It is to audit how each new observation should revise the first interpretation.')
anc=[(0,96),(.12,98.2),(.23,98.7),(.36,99.6),(.48,99.2),(.59,100.1),(.69,102.7),(.78,103.3),(.86,101.0),(.93,99.1),(1,97.7)]
d=make_ohlc(anc,48,seed=950,noise=.35)
for i,(n,title,sub) in enumerate([(28,'01 · Before','What made this boundary relevant?'),(34,'02 · Break','What does the close establish?'),(40,'03 · Contradiction','What changed in the evidence?'),(48,'04 · Review','What do you revise—and retain?')]):
    dd={k:v[:n] for k,v in d.items()}; draw_candles(axs[i],dd,(99.5,101),show_x=True); axs[i].set_ylim(95,105.5); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=8); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.0,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG09_decision_record_timeline.png')

# FIG10 improved failure family 2x3, 35 candles each
fig,axs=plt.subplots(2,3,figsize=(17,10.2)); fig.subplots_adjust(left=.045,right=.99,top=.87,bottom=.09,wspace=.16,hspace=.3)
fighead(fig,'Failed signals are a family of sequences—not one candle pattern','The initial signal differs by structure. The common question is whether later price action supports or contradicts the signal.')
family=[
 ([(0,97),(.16,99),(.32,98.7),(.46,99.6),(.58,102.2),(.67,100),(.78,98.6),(.9,97.4),(1,96.5)],(99.2,100.4),'01 · Range-edge upthrust','Trades above the range, then closes and holds inside.'),
 ([(0,102),(.15,100.8),(.3,101.2),(.44,99.0),(.55,96.8),(.66,99),(.78,101),(.9,102),(1,103)],(99.0,100.1),'02 · Spring / downside failure','Moves below support, then reclaims the prior range.'),
 ([(0,96),(.15,98),(.30,100),(.45,102),(.6,103.5),(.73,102.2),(.82,100.5),(.91,101.8),(1,102.0)],None,'03 · Trendline break reclaimed','A line break alone does not show a lasting structure change.'),
 ([(0,96.5),(.15,98),(.28,99.5),(.42,101),(.53,103),(.64,104),(.75,101.6),(.85,99.6),(1,98.2)],(99.5,101),'04 · First pullback fails','The first pullback holds; a later return breaks the prior area.'),
 ([(0,96.5),(.12,98),(.28,100),(.42,99.3),(.54,101.2),(.66,100.4),(.75,99.6),(.87,97.5),(1,96)],(99.5,101),'05 · Continuation pattern fails','A pause breaks in the opposite direction from the first thesis.'),
 ([(0,96),(.14,98),(.28,99.6),(.43,98.9),(.55,100.1),(.68,102.3),(.79,99.2),(.9,97.7),(1,96.8)],(99.5,101),'06 · Prior swing break fails','A previous pivot is crossed, then quickly surrendered.')]
for i,(anc,zone,title,sub) in enumerate(family):
    ax=axs.flat[i]; d=make_ohlc(anc,39,seed=1000+i,noise=.37); draw_candles(ax,d,zone,show_x=False); ax.set_ylim(94.2,106.2); ax.set_title(title,loc='left',color=INK,fontweight='bold',pad=7); ax.text(.02,.035,sub,transform=ax.transAxes,fontsize=6.8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
    if i==2:
        # add rising trendline
        ax.plot([2,34],[96.7,103.1],ls=(0,(4,3)),color=GOLD,lw=1.1,zorder=1)
save(fig,'FIG10_failed_signal_family.png')

# FIG11 pullbacks: first holds vs later fails (Grimes concept)
fig,axs=plt.subplots(1,2,figsize=(14.7,7.0)); fig.subplots_adjust(left=.06,right=.98,top=.82,bottom=.12,wspace=.2)
fighead(fig,'Not all pullbacks are equal','The first return after a break and a later pullback can supply different evidence. Read the sequence rather than naming every dip “support”.')
seq=[
 ([(0,95),(.13,97),(.24,99.2),(.35,100.4),(.46,103.2),(.56,101.4),(.65,103.5),(.77,105.0),(.9,105.8),(1,107)],(99.5,101),'01 · First pullback holds','The first return stays above the old area; price moves away.'),
 ([(0,95),(.13,97),(.24,99.2),(.35,100.4),(.46,103.2),(.56,101.4),(.65,104),(.74,105.2),(.84,101),(.93,99.4),(1,97.8)],(99.5,101),'02 · Later pullback fails','After initial continuation, price crosses back through the area.')]
for i,(anc,zone,title,sub) in enumerate(seq):
 d=make_ohlc(anc,49,seed=1200+i,noise=.4); draw_candles(axs[i],d,zone,show_x=True); axs[i].set_ylim(93.5,108.5); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.8,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG11_first_pullback_later_failure.png')

# FIG12 failure alternative after range: reach other boundary not guaranteed
fig,axs=plt.subplots(1,3,figsize=(15.5,6.8)); fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.2)
fighead(fig,'A failed upper break can change the range question','After a failed move above the upper edge, price may move through the range, stall, or turn again. The opposite boundary is context—not a promised target.')
seq=[
 ([(0,97.5),(.18,99),(.36,100),(.49,102.3),(.58,99.2),(.7,97.7),(.83,96.2),(1,94.8)],(95,96),'01 · Range travel','Price moves toward the other edge in this example.'),
 ([(0,97.5),(.18,99),(.36,100),(.49,102.3),(.58,99.2),(.7,98.9),(.83,99.6),(1,98.8)],(95,96),'02 · Range interior','The failed break stalls; the lower edge is not reached.'),
 ([(0,97.5),(.18,99),(.36,100),(.49,102.3),(.58,99.2),(.7,100.5),(.83,102),(1,103.5)],(95,96),'03 · Boundary reclaimed','The market returns above the upper area; reassess again.')]
for i,(anc,zone,title,sub) in enumerate(seq):
 d=make_ohlc(anc,43,seed=1300+i,noise=.36); draw_candles(axs[i],d,(99.5,101.0),show_x=True); axs[i].axhspan(95,96,color=ZONE,alpha=.24); axs[i].axhline(95,color=ZEDGE,lw=.8); axs[i].axhline(96,color=ZEDGE,lw=.8); axs[i].set_ylim(93.6,105); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=8); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.2,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG12_after_failure_alternatives.png')

# FIG13 gap / spike failure two columns
fig,axs=plt.subplots(1,2,figsize=(14.8,7.2)); fig.subplots_adjust(left=.06,right=.98,top=.82,bottom=.12,wspace=.2)
fighead(fig,'Gaps and wide-range bars complicate the definition of a break','The next tradable price may jump across the boundary. A single extreme candle also has an entire high-low range, not a single confirmation point.')
seq=[
 ([(0,97),(.16,98.5),(.31,99.4),(.45,100),(.57,103.4),(.68,103.8),(.78,102),(.88,99.6),(1,98.8)],(99.5,101),'01 · Gap beyond, then return','A gap can leap through the band; the return still needs interpretation.',{24:102.4}),
 ([(0,97),(.15,98.5),(.3,99.4),(.45,100),(.58,103.7),(.64,101.3),(.72,99.5),(.84,98.8),(1,98)],(99.5,101),'02 · Wide-range spike, no hold','A wide bar extends beyond the zone; later closes return inside.',None)]
for i,(anc,zone,title,sub,gaps) in enumerate(seq):
 d=make_ohlc(anc,42,seed=1410+i,noise=.34,gap_points=gaps); draw_candles(axs[i],d,zone,show_x=True); axs[i].set_ylim(94.8,106.4); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.5,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG13_gap_and_spike_failures.png')

# FIG14 failure of failure: first failed breakout then reclaim
fig,ax=plt.subplots(figsize=(13.8,6.8)); fig.subplots_adjust(left=.07,right=.98,top=.83,bottom=.12)
fighead(fig,'A failed signal can itself be challenged','A reclaim does not retroactively erase the first failure. It adds a new fact that requires a second update.')
anc=[(0,96),(.10,98),(.23,99.4),(.34,100.1),(.45,102.6),(.55,99),(.64,98.4),(.73,100.4),(.82,102.2),(.92,103),(1,104)]
d=make_ohlc(anc,52,seed=1510,noise=.4); draw_candles(ax,d,(99.5,101),show_x=True); ax.set_ylim(94.5,106.5)
annotate(ax,25,d['Close'][25],'First failure evidence',(RUST),(13,104.8)); annotate(ax,43,d['Close'][43],'Reclaim challenges the\nfailed-break interpretation',GREEN,(32,105.4))
save(fig,'FIG14_failed_failure_reclaim.png')

# FIG15 classification framework with chart ribbon + boxes
fig,ax=plt.subplots(figsize=(14.8,7.3)); fig.subplots_adjust(left=.035,right=.985,top=.82,bottom=.1); ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off');ax.set_facecolor(PAPER)
fighead(fig,'When is a breakout failure a defensible label?','Define the original claim before the outcome. Apply the label only when later evidence challenges that claim.')
steps=[
 (4,58,20,23,'01 · Define signal','Which boundary? Which timeframe?\nWhich convention?'),
 (28,58,20,23,'02 · Observe attempt','Wick, close, distance,\ntime outside, follow-through?'),
 (52,58,20,23,'03 · Find contradiction','Return inside? Reclaim fails?\nFollow-through absent?'),
 (76,58,20,23,'04 · Check response','Persist, chop, or reclaim?\nHow strong is the label?')]
for x,y,w,h,title,body in steps:
 box=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=1,rounding_size=1.8',facecolor=PANEL,edgecolor='#d7cdbb',linewidth=1.2);ax.add_patch(box)
 ax.text(x+1.4,y+h-5.2,title,fontsize=10,fontweight='bold',color=INK,va='top')
 ax.text(x+1.4,y+h-11.5,body,fontsize=8.5,color=MUTED,va='top',linespacing=1.5)
 if x<76:ax.add_patch(FancyArrowPatch((x+w+1,y+h/2),(x+w+3.5,y+h/2),arrowstyle='-|>',mutation_scale=11,color=GOLD,lw=1.2))
box=FancyBboxPatch((14,16),72,23,boxstyle='round,pad=1,rounding_size=1.8',facecolor='#f6f1e6',edgecolor='#cdb47d',linewidth=1.2);ax.add_patch(box)
ax.text(17,33,'The final wording should describe the evidence—not invent a cause.',fontsize=12,fontfamily='DejaVu Serif',color=INK,va='top')
ax.text(17,26,'Good: “Price moved above the range, returned inside, then failed to reclaim it.”',fontsize=9.5,color=GREEN,va='top')
ax.text(17,20,'Avoid: “Institutions trapped breakout traders.” The chart alone cannot prove motive.',fontsize=9.2,color=RUST,va='top')
save(fig,'FIG15_failure_label_checklist.png')

# FIG16 market context/retest map: three possible paths after return, with event tags
fig,axs=plt.subplots(1,3,figsize=(15.4,6.9));fig.subplots_adjust(left=.055,right=.985,top=.82,bottom=.12,wspace=.22)
fighead(fig,'A retest is not one event: classify depth, close and response','The return can stop short, enter the band, close back inside or be followed by a reclaim. Record what actually happened.')
seq=[
 ([(0,96),(.14,98.6),(.29,99.5),(.43,100),(.55,102.4),(.67,103.5),(.78,102.5),(.88,102.3),(1,104.2)],'SHALLOW / STAYS OUTSIDE','Near the upper edge, closes remain above.'),
 ([(0,96),(.14,98.6),(.29,99.5),(.43,100),(.55,102.4),(.67,103.5),(.78,100.4),(.88,101.6),(1,103)],'ENTERS / RECLAIMS','The wick enters the band; close and next bars matter.'),
 ([(0,96),(.14,98.6),(.29,99.5),(.43,100),(.55,102.4),(.67,103.5),(.78,100),(.88,98.7),(1,97.5)],'CLOSES BACK INSIDE','The continuation thesis loses support in this window.')]
for i,(anc,title,sub) in enumerate(seq):
 d=make_ohlc(anc,42,seed=1610+i,noise=.37);draw_candles(axs[i],d,(99.5,101),show_x=True);axs[i].set_ylim(94.5,106);axs[i].set_title(title,loc='left',color=GREEN if i<2 else RUST,fontweight='bold',pad=10);axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.0,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG16_retest_depth_and_closes.png')

# FIG17 range boundary vs trendline failure contrast, more context panels
fig,axs=plt.subplots(1,2,figsize=(14.7,7.1));fig.subplots_adjust(left=.06,right=.98,top=.82,bottom=.12,wspace=.2)
fighead(fig,'The structure defines what a failed break would mean','A range-edge failure and a trendline-break reclaim are different chart events; the labels should identify the structure.')
seq=[
 ([(0,97),(.15,99),(.3,98.4),(.45,99.8),(.59,99.4),(.71,102.3),(.81,99.6),(.9,98.3),(1,97.6)],(99.4,100.7),'Range boundary','Failed move above the range; later price re-enters.'),
 ([(0,95.8),(.16,97),(.32,98.8),(.48,100.6),(.64,102.6),(.78,101.2),(.88,99.8),(1,101)],None,'Rising trendline','Price briefly breaks the line, then reclaims or continues?')]
for i,(anc,zone,title,sub) in enumerate(seq):
 d=make_ohlc(anc,44,seed=1710+i,noise=.39);draw_candles(axs[i],d,zone,show_x=True);axs[i].set_ylim(94.5,105.5);axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10);axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.5,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
if True:
 axs[1].plot([3,40],[96,101.9],ls=(0,(4,3)),color=GOLD,lw=1.15)
save(fig,'FIG17_range_vs_trendline_failure.png')

# FIG18: generated image overview use a clean editorial frame and captions as complementary opener
src=ROOT/'tools'/'source_figures'/'FIG00_generated_overview_source.png'
if src.exists():
    im=Image.open(src).convert('RGB')
    # crop slightly, add header and footer with typography while preserving core artwork
    W=1600; art=im.resize((W, int(im.height*W/im.width)),Image.Resampling.LANCZOS)
    header_h=128; footer_h=118
    out=Image.new('RGB',(W,header_h+art.height+footer_h),PAPER)
    out.paste(art,(0,header_h))
    draw=ImageDraw.Draw(out)
    font_serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';font_sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    try:
        ftitle=ImageFont.truetype(font_serif,44); fsub=ImageFont.truetype(font_sans,19); ffoot=ImageFont.truetype(font_sans,18); fbold=ImageFont.truetype(font_bold,16)
    except: ftitle=ffoot=fbold=fsub=ImageFont.load_default()
    draw.text((48,24),'Four ways a boundary episode can resolve',font=ftitle,fill=INK)
    draw.text((50,84),'Context first · evidence next · label only after the sequence develops',font=fsub,fill=MUTED)
    fy=header_h+art.height+12
    labels=[('FAILED UPSIDE ATTEMPT',48),('BREAK · RETURN · HOLD',432),('FAILURE WITH FOLLOW-THROUGH',838),('MIXED, THEN BREAKS DOWN',1235)]
    for text,xpos in labels: draw.text((xpos,fy),text,font=fbold,fill=INK)
    draw.text((48,fy+43),'Conceptual overview only · panels are schematic illustrations, not market data or a forecast.',font=ffoot,fill=MUTED)
    out.save(FIG/'FIG00_boundary_episode_overview.png',quality=95)

# FIG18: top/bottom formation neckline failure
fig,axs=plt.subplots(1,2,figsize=(14.8,7.1)); fig.subplots_adjust(left=.06,right=.98,top=.82,bottom=.12,wspace=.2)
fighead(fig,'Pattern boundaries can fail too','A neckline break is still a claim about structure. Observe whether price establishes itself beyond it or quickly reclaims the prior formation.')
seq=[
 ([(0,101.5),(.12,102.8),(.24,103.5),(.36,101.2),(.48,103.4),(.60,101.3),(.70,98.8),(.80,99.1),(.89,101.0),(1,102.1)],(99.7,100.3),'01 · Top formation breakdown reclaims','The move below the neckline is reversed; the downside claim weakens.'),
 ([(0,99),(.12,97.8),(.24,96.9),(.36,99.1),(.48,97.0),(.60,99.2),(.70,101.8),(.80,100.8),(.90,99.4),(1,98.1)],(100.0,100.6),'02 · Bottom formation breakout fails','The move above the neckline returns under it; continuation is not sustained.')]
for i,(anc,zone,title,sub) in enumerate(seq):
 d=make_ohlc(anc,46,seed=1810+i,noise=.38); draw_candles(axs[i],d,zone,show_x=True); axs[i].set_ylim(94,106); axs[i].set_title(title,loc='left',color=INK,fontweight='bold',pad=10); axs[i].text(.02,.035,sub,transform=axs[i].transAxes,fontsize=7.5,color=MUTED,bbox={'fc':PANEL,'ec':'#e2dacb','boxstyle':'round,pad=.3'})
save(fig,'FIG18_neckline_formation_failures.png')

# Create visual index
items=[
('FIG00_boundary_episode_overview.png','Opening overview','Four conceptual boundary episodes'),
('FIG01_breakout_evidence_ladder.png','Lesson 12','Wick, close and follow-through'),
('FIG02_filter_tradeoffs.png','Lesson 12','Close, two closes and return-test trade-offs'),
('FIG03_context_changes_the_question.png','Lessons 12–13','Local break versus wider structure'),
('FIG04_break_return_response.png','Lesson 13','Break, return and response timeline'),
('FIG05_three_retest_outcomes.png','Lesson 13','Hold, fail and inconclusive return'),
('FIG06_retest_is_not_owed.png','Lesson 13','No retest, delayed, shallow and deep return'),
('FIG07_failure_is_not_reverse_signal.png','Lesson 14','After failure: travel, chop, reclaim'),
('FIG08_volume_context_not_gate.png','Lessons 12–14','Price outcome crossed with volume context'),
('FIG09_decision_record_timeline.png','All lessons','Preserve the view before the outcome'),
('FIG10_failed_signal_family.png','Lesson 14','Six failure families with developed context'),
('FIG11_first_pullback_later_failure.png','Lesson 14','First pullback holds; later pullback fails'),
('FIG12_after_failure_alternatives.png','Lesson 14','Failure does not set an opposite target'),
('FIG13_gap_and_spike_failures.png','Lesson 14','Gap and wide-range-bar complications'),
('FIG14_failed_failure_reclaim.png','Lesson 14','A reclaim can challenge the failure label'),
('FIG15_failure_label_checklist.png','Lesson 14','A disciplined classification sequence'),
('FIG16_retest_depth_and_closes.png','Lesson 13','Depth, closing location and response'),
('FIG17_range_vs_trendline_failure.png','Lesson 14','Structure-specific false breaks'),
('FIG18_neckline_formation_failures.png','Lesson 14','Top/bottom formation neckline breaks that fail')]
with (ROOT/'FIGURE_INVENTORY.csv').open('w',encoding='utf-8') as f:
    f.write('file,lesson_or_use,description\n')
    for a,b,c in items: f.write(f'"{a}","{b}","{c}"\n')
print('Generated figures:')
for n,_,_ in items:
    p=FIG/n
    print(n, p.exists(), p.stat().st_size if p.exists() else 0)
