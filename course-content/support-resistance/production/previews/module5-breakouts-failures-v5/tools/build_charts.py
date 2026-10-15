from pathlib import Path
import csv, hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
CHARTS=ROOT/'charts'
DATA=ROOT/'data'
PAPER='#fbf7ef'; INK='#29382e'; MUTED='#687268'; GREEN='#355a46'; GRID='#e7e0d2'; ZONE='#f0d38a'; ZEDGE='#b58e3c'; UP='#fffdf8'; DOWN='#536575'; WICK='#50616c'

def load_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    out=[]
    for r in rows:
        out.append({k: (datetime.strptime(r['Date'],'%Y-%m-%d') if k=='Date' else float(r[k])) for k in ['Date','Open','High','Low','Close']})
    return out

def get_date(s): return datetime.strptime(s,'%Y-%m-%d')

def draw(name, data, cutoff, zone, title, subtitle, note, reveal_label=None, ylims=None):
    use=[b for b in data if b['Date']<=get_date(cutoff)]
    fig,ax=plt.subplots(figsize=(12.8,7.2),dpi=140)
    fig.patch.set_facecolor(PAPER); ax.set_facecolor('#fffdf8')
    fig.subplots_adjust(left=0.075,right=0.975,top=0.84,bottom=0.16)
    for side in ['top','right']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#ded8ca'); ax.spines['bottom'].set_color('#ded8ca')
    ax.grid(axis='y',color=GRID,linewidth=.8); ax.grid(axis='x',color='#f2ece2',linewidth=.45)
    ax.set_axisbelow(True)
    lo,hi=zone
    ax.axhspan(lo,hi,color=ZONE,alpha=.32,zorder=1)
    ax.axhline(lo,color=ZEDGE,lw=1.05,zorder=2); ax.axhline(hi,color=ZEDGE,lw=1.05,zorder=2)
    n=len(use)
    xs=list(range(n))
    width=.58
    for i,b in enumerate(use):
        up=b['Close']>=b['Open']; fill=UP if up else DOWN
        ax.vlines(i,b['Low'],b['High'],color=WICK,linewidth=1.1,zorder=3)
        bottom=min(b['Open'],b['Close']); height=max(abs(b['Close']-b['Open']),.035)
        ax.add_patch(Rectangle((i-width/2,bottom),width,height,facecolor=fill,edgecolor=INK if up else DOWN,linewidth=.9,zorder=4))
    # zone annotation is neutral until later states; never label an outcome before it is observed.
    label=f'prior area · {lo:,.0f}–{hi:,.0f}'
    ax.text(max(1,n*.5),hi+(hi-lo)*.18,label,fontsize=8.5,color='#725c2a',va='bottom',ha='left',bbox={'boxstyle':'round,pad=.25','facecolor':'#fff9e8','edgecolor':'#e2cd8f','linewidth':.6})
    if reveal_label:
        ax.annotate(reveal_label,xy=(n-2,use[-2]['Close']),xytext=(max(2,n*.62),use[-2]['Close']+(max(b['High'] for b in use)-min(b['Low'] for b in use))*.13),fontsize=8.5,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN,'lw':.9},bbox={'boxstyle':'round,pad=.25','facecolor':'#f2f7ef','edgecolor':'#cbd9c5','linewidth':.6})
    if ylims: ax.set_ylim(*ylims)
    else:
        lows=[b['Low'] for b in use]+[lo]; highs=[b['High'] for b in use]+[hi]
        span=max(highs)-min(lows); ax.set_ylim(min(lows)-span*.1,max(highs)+span*.20)
    positions=[]
    max_ticks=min(6,n)
    for pos in range(max_ticks):
        idx=round(pos*(n-1)/(max_ticks-1)) if max_ticks>1 else 0
        positions.append(idx)
    ax.set_xticks(positions)
    ax.set_xticklabels([use[i]['Date'].strftime('%d %b %Y') for i in positions],fontsize=8,color=MUTED)
    ax.tick_params(axis='y',labelsize=8,colors=MUTED,length=0); ax.tick_params(axis='x',length=0,pad=8)
    ax.set_ylabel('NIFTY 50 index points',fontsize=9,color=MUTED,labelpad=10)
    fig.suptitle(title,x=.075,y=.96,ha='left',fontsize=17,fontfamily='DejaVu Serif',color=INK)
    fig.text(.075,.905,subtitle,ha='left',fontsize=9,color=MUTED)
    fig.text(.075,.055,note,ha='left',fontsize=8,color=MUTED)
    out=CHARTS/name
    fig.savefig(out,facecolor=PAPER,bbox_inches='tight')
    plt.close(fig)
    return {'file':f'charts/{name}','rows':n,'start':use[0]['Date'].strftime('%Y-%m-%d'),'end':use[-1]['Date'].strftime('%Y-%m-%d'),'zone_low':lo,'zone_high':hi}

# Load daily data from existing extraction (same source, no candle reconstruction).
data12=load_csv(DATA/'NIFTY50-2016-breakout-failure.csv')
data13=load_csv(DATA/'NIFTY50-2014-retest-hold.csv')
data14=load_csv(DATA/'NIFTY50-2018-failed-breakout.csv')
assets=[]
# Lesson 12: an apparent breakout that passes multiple close filters and then fails.
z12=(8810,8850)
assets.append(draw('L12-01-before-break.png',data12,'2016-09-02',z12,'L12 · Before the break','NIFTY 50 · daily OHLC · stage 1 — all candles after 2 Sep hidden','Internal teaching case · historical daily OHLC · no prediction implied',None,(8400,9050)))
assets.append(draw('L12-02-outside-zone.png',data12,'2016-09-08',z12,'L12 · Price closes beyond the area','NIFTY 50 · daily OHLC · stage 2 — reveal through 8 Sep 2016','Question: what does the sequence establish, and what remains unresolved?',None,(8400,9050)))
assets.append(draw('L12-03-later-failure.png',data12,'2016-09-16',z12,'L12 · Later evidence changes the read','NIFTY 50 · daily OHLC · stage 3 — later sessions now visible','Price later closes back below the zone; this does not mean the failure was knowable at stage 1.','return below zone',(8400,9050)))
# Lesson 13: candidate prior resistance, break and pullback that remains above area in selected window.
z13=(7795,7865)
assets.append(draw('L13-01-before-break.png',data13,'2014-08-15',z13,'L13 · The old upper area','NIFTY 50 · daily OHLC · stage 1 — future candles hidden','Decide first whether the selected band reasonably describes prior upper reactions.',None,(7350,8235)))
assets.append(draw('L13-02-return-toward-area.png',data13,'2014-08-22',z13,'L13 · The return approaches the band','NIFTY 50 · daily OHLC · stage 2 — through 22 Aug 2014','Record whether price touched, entered or just approached the zone; keep the original band fixed.',None,(7350,8235)))
assets.append(draw('L13-03-later-evidence.png',data13,'2014-09-18',z13,'L13 · Later evidence stays above the area','NIFTY 50 · daily OHLC · stage 3 — selected later window','Consistent with a role-reversal hypothesis in this window; not proof of causation or a guarantee.','later price remains above area',(7350,8235)))
# Lesson 14: breakout, first apparent return above, then failed follow-through.
z14=(10875,10920)
assets.append(draw('L14-01-before-break.png',data14,'2018-01-19',z14,'L14 · Before the breakout attempt','NIFTY 50 · daily OHLC · stage 1 — later sessions hidden','Record the prior area and what would weaken a continuation thesis.',None,(9950,11220)))
assets.append(draw('L14-02-initial-return.png',data14,'2018-02-01',z14,'L14 · The return initially looks acceptable','NIFTY 50 · daily OHLC · stage 2 — through 1 Feb 2018','Pause here: the failure is not yet shown. Write what you think and what would invalidate it.',None,(9950,11220)))
assets.append(draw('L14-03-failed-follow-through.png',data14,'2018-02-20',z14,'L14 · The continuation thesis weakens','NIFTY 50 · daily OHLC · stage 3 — later sessions now visible','The 2 Feb close falls below the zone; the subsequent path adds further evidence.', 'close back below zone',(9950,11220)))

with (ROOT/'CHART_INVENTORY.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['file','rows_visible','first_visible_date','last_visible_date','zone_low','zone_high','lesson','stage'])
    w.writeheader()
    for a in assets:
        file=a['file']; lesson=file.split('/')[-1][:3]; stage=file.split('/')[-1][4:6]
        w.writerow({'file':file,'rows_visible':a['rows'],'first_visible_date':a['start'],'last_visible_date':a['end'],'zone_low':a['zone_low'],'zone_high':a['zone_high'],'lesson':lesson,'stage':stage})

with (ROOT/'SHA256SUMS.txt').open('w',encoding='utf-8') as f:
    for path in sorted([p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and p.name!='package_manifest.json']):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        f.write(f'{digest}  {path.relative_to(ROOT).as_posix()}\n')
print(json.dumps(assets,indent=2))
