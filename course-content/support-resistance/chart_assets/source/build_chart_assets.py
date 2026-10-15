from __future__ import annotations

import csv
import math
import random
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / 'charts'
DATA_DIR = ROOT / 'data'
CHART_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Shared design tokens: restrained, light-background, readable at course/mobile scale.
UP_EDGE = '#34495E'
UP_FILL = '#F7FAFC'
DOWN_FILL = '#52616B'
WICK = '#66737D'
GRID = '#E7EAED'
INK = '#263238'
MUTED = '#66727B'
BAND = '#E7C76D'
BAND_EDGE = '#9D781B'
SELECTED = '#276A75'
OPTIONAL = '#B56A35'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.labelcolor': INK,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
    'text.color': INK,
    'svg.fonttype': 'none',
})

ASSETS: list[dict[str, Any]] = []
DATASETS: dict[str, list[dict[str, float]]] = {}


def bars_from_closes(closes: list[float], seed: int, wick_overrides: dict[int, tuple[float | None, float | None]] | None = None,
                     open_offsets: list[float] | None = None) -> list[dict[str, float]]:
    rng = random.Random(seed)
    bars = []
    for i, close in enumerate(closes):
        if open_offsets and i < len(open_offsets):
            op = close + open_offsets[i]
        else:
            prev = closes[i-1] if i else close - rng.uniform(-0.5, 0.5)
            op = prev + rng.uniform(-0.38, 0.38)
        spread_high = rng.uniform(0.2, 0.7)
        spread_low = rng.uniform(0.2, 0.7)
        high = max(op, close) + spread_high
        low = min(op, close) - spread_low
        if wick_overrides and i in wick_overrides:
            lo, hi = wick_overrides[i]
            if lo is not None:
                low = min(lo, op, close) - 0.02
            if hi is not None:
                high = max(hi, op, close) + 0.02
        bars.append({'open': round(op, 3), 'high': round(high, 3), 'low': round(low, 3), 'close': round(close, 3)})
    return bars


def save_dataset(dataset_id: str, bars: list[dict[str, float]]) -> None:
    DATASETS[dataset_id] = bars
    with (DATA_DIR / f'{dataset_id}.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['bar', 'open', 'high', 'low', 'close'])
        writer.writeheader()
        for i, b in enumerate(bars, start=1):
            writer.writerow({'bar': i, **b})


def draw_chart(asset_id: str, dataset_id: str, bars: list[dict[str, float]], state: str,
               visible_bars: int | None = None, bands: list[dict[str, Any]] | None = None,
               markers: list[dict[str, Any]] | None = None, extra_text: list[dict[str, Any]] | None = None,
               alt_text: str = '', note: str = '', label: str = '', y_limits: tuple[float, float] | None = None) -> None:
    use = bars[:visible_bars] if visible_bars else bars
    n = len(use)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=140)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.92, bottom=0.15)
    ax.set_facecolor('#FFFFFF')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#D8DDE1')
    ax.spines['bottom'].set_color('#D8DDE1')
    ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)
    ax.grid(axis='x', color='#F2F4F5', linewidth=0.55, zorder=0)
    ax.set_axisbelow(True)

    # Areas sit beneath candles and labels.
    for band in bands or []:
        lo, hi = band['low'], band['high']
        ax.axhspan(lo, hi, color=band.get('color', BAND), alpha=band.get('alpha', 0.27), zorder=1,
                   linewidth=0)
        if band.get('edge', True):
            ax.axhline(lo, color=band.get('edge_color', BAND_EDGE), linewidth=0.95, alpha=0.85, zorder=2)
            ax.axhline(hi, color=band.get('edge_color', BAND_EDGE), linewidth=0.95, alpha=0.85, zorder=2)
        if band.get('label'):
            x = band.get('x', max(1, int(n * 0.58)))
            ax.text(x, hi + (max(b['high'] for b in use) - min(b['low'] for b in use)) * 0.025,
                    band['label'], ha='left', va='bottom', fontsize=9, color=INK,
                    bbox={'boxstyle': 'round,pad=0.3', 'facecolor': '#FFF9E8', 'edgecolor': '#D9C17A', 'linewidth': 0.7},
                    zorder=6)

    # Candles
    width = 0.58
    for i, b in enumerate(use):
        up = b['close'] >= b['open']
        fill = UP_FILL if up else DOWN_FILL
        edge = UP_EDGE
        ax.vlines(i, b['low'], b['high'], color=WICK, linewidth=1.15, zorder=4)
        bottom = min(b['open'], b['close'])
        height = max(abs(b['close'] - b['open']), 0.055)
        rect = Rectangle((i-width/2, bottom), width, height, facecolor=fill, edgecolor=edge,
                         linewidth=1.05, zorder=5)
        ax.add_patch(rect)

    # Marker overlays (candidate points / reference swing points)
    for m in markers or []:
        idx = m['bar'] - 1
        if not (0 <= idx < n):
            continue
        y = m.get('y')
        if y is None:
            b = use[idx]
            y = b['low'] - 0.28 if m.get('kind', 'low') == 'low' else b['high'] + 0.28
        c = m.get('color', SELECTED)
        ax.scatter([idx], [y], s=m.get('size', 36), facecolor=m.get('facecolor', c),
                   edgecolor=m.get('edgecolor', '#FFFFFF'), linewidth=0.9, zorder=8)
        if m.get('label'):
            dy = m.get('label_offset', -0.38 if m.get('kind') == 'low' else 0.38)
            ax.text(idx, y + dy, m['label'], ha='center', va='center', fontsize=8.4,
                    color=m.get('label_color', INK), fontweight='bold', zorder=9,
                    bbox={'boxstyle': 'round,pad=0.16', 'facecolor': '#FFFFFF', 'edgecolor': '#D6DDE1', 'linewidth': 0.55})

    for t in extra_text or []:
        ax.text(t.get('x', max(0.5, n*0.06)), t.get('y', max(b['high'] for b in use)), t['text'],
                fontsize=t.get('fontsize', 9), color=t.get('color', INK), ha=t.get('ha', 'left'),
                va=t.get('va', 'top'), zorder=10,
                bbox=t.get('bbox', {'boxstyle': 'round,pad=0.25', 'facecolor': '#FFFFFF', 'edgecolor': '#D6DDE1', 'linewidth': 0.65}))

    ax.set_xlim(-0.8, n-0.2)
    if y_limits:
        ax.set_ylim(*y_limits)
    else:
        lows = [b['low'] for b in use]
        highs = [b['high'] for b in use]
        # Include reference bands in autoscaling so intentionally distant marks remain visible.
        for band in bands or []:
            lows.append(float(band['low']))
            highs.append(float(band['high']))
        span = max(highs) - min(lows)
        ax.set_ylim(min(lows)-span*0.12, max(highs)+span*0.16)
    # Abstract bar index, not dates or a real instrument scale.
    ax.set_xticks([0, max(1, n//4), max(2, n//2), max(3, (3*n)//4), n-1])
    ax.set_xticklabels(['Earlier', '', 'Sequence', '', 'Later'])
    ax.set_ylabel('Illustrative price')
    ax.tick_params(axis='both', labelsize=8.5, length=0, pad=7)
    ax.set_title(label, loc='left', fontsize=12, fontweight='bold', color=INK, pad=11) if label else None
    fig.text(0.5, 0.035, 'Illustrative chart — not historical market data', ha='center', va='center',
             fontsize=9, color=MUTED)
    if note:
        fig.text(0.97, 0.035, note, ha='right', va='center', fontsize=8, color=MUTED)
    for ext in ('png', 'svg'):
        fig.savefig(CHART_DIR / f'{asset_id}.{ext}', dpi=160 if ext == 'png' else None,
                    facecolor='white', metadata={'Description': alt_text or 'Synthetic illustrative candlestick chart.'})
    plt.close(fig)
    ASSETS.append({
        'asset_id': asset_id, 'dataset_id': dataset_id, 'state': state,
        'visible_bars': visible_bars or len(bars), 'format': 'PNG + SVG', 'source_type': 'synthetic illustrative OHLC',
        'alt_text': alt_text, 'notes': note,
    })

# --- Lesson 1: repeated reaction zones ---
support1_closes = [102.3,101.2,100.4,99.3,98.8,99.5,100.7,101.3,100.5,99.6,98.9,99.4,100.5,101.7,102.2,101.5,100.3,99.4,98.0,96.9,96.1]
support1 = bars_from_closes(support1_closes, 101, {4:(97.95,None), 10:(97.85,None), 18:(97.3,None)})
save_dataset('L01_A_repeated_lower_reaction', support1)
band_support1 = {'low':97.7,'high':99.0,'label':'prior reaction area'}
draw_chart('L01-A-01-clean', 'L01_A_repeated_lower_reaction', support1, 'unlabelled repeated lower reactions', visible_bars=16,
           alt_text='Illustrative candles decline into a broad lower price area, move upward, and later revisit a similar area before a later extension is shown.')
draw_chart('L01-A-02-band', 'L01_A_repeated_lower_reaction', support1, 'band only', visible_bars=16, bands=[{**band_support1,'label':None}],
           alt_text='Same illustrative lower reaction sequence with a neutral band around the area where price reacted more than once.')
draw_chart('L01-A-03-labelled', 'L01_A_repeated_lower_reaction', support1, 'band plus prior-reaction label', visible_bars=16, bands=[band_support1],
           alt_text='Same illustrative sequence with the lower band labelled prior reaction area.')
draw_chart('L01-A-04-support-label', 'L01_A_repeated_lower_reaction', support1, 'support area label', visible_bars=16, bands=[{'low':97.7,'high':99.0,'label':'support area'}],
           alt_text='Same illustrative sequence with the lower area labelled support area.')
draw_chart('L01-A-05-breakdown', 'L01_A_repeated_lower_reaction', support1, 'later candles crossing decisively through band', bands=[{'low':97.7,'high':99.0,'label':'support area'}],
           alt_text='Illustrative support-area sequence extended with later candles moving decisively below the former lower reaction area.')

resist1_closes = [98.9,99.5,100.3,101.4,102.7,103.8,103.1,101.8,100.9,101.8,103.2,104.4,103.7,102.3,101.4,100.7]
resist1 = bars_from_closes(resist1_closes, 102, {5:(None,105.0), 11:(None,105.2)})
save_dataset('L01_B_repeated_upper_reaction', resist1)
resband = {'low':103.7,'high':105.0,'label':'prior reaction area'}
draw_chart('L01-B-01-clean', 'L01_B_repeated_upper_reaction', resist1, 'unlabelled repeated upper reactions', visible_bars=16,
           alt_text='Illustrative price sequence rises into a broad upper area, turns down, returns to that area and turns down again.')
draw_chart('L01-B-02-band', 'L01_B_repeated_upper_reaction', resist1, 'band only', bands=[{**resband,'label':None}],
           alt_text='Same upper reaction sequence with a broad neutral band around related upper reactions.')
draw_chart('L01-B-03-labelled', 'L01_B_repeated_upper_reaction', resist1, 'band plus prior-reaction label', bands=[resband],
           alt_text='Same upper reaction sequence with a band labelled prior reaction area.')
draw_chart('L01-B-04-resistance-label', 'L01_B_repeated_upper_reaction', resist1, 'resistance area label', bands=[{'low':103.7,'high':105.0,'label':'resistance area'}],
           alt_text='Same upper reaction sequence with the band labelled resistance area.')

# Lesson 1 separate simple practice charts
p1a_closes = [102,101,99.5,98.4,99.2,100.4,101.3,100.0,98.7,99.3,100.5,101.2,102.1]
p1a = bars_from_closes(p1a_closes, 103, {3:(97.8,None),8:(97.9,None)})
save_dataset('L01_PRACTICE_A_clearer_reactions', p1a)
draw_chart('L01-PRACTICE-A-01-clean', 'L01_PRACTICE_A_clearer_reactions', p1a, 'practice, no annotation',
           alt_text='Illustrative practice chart with two relatively clear lower reactions and upward movement away from each.')
draw_chart('L01-PRACTICE-A-02-reference', 'L01_PRACTICE_A_clearer_reactions', p1a, 'practice reference overlay',
           bands=[{'low':97.7,'high':99.1,'label':'one defensible lower area'}],
           alt_text='Practice chart with one defensible lower reaction area shown as a band; other boundaries may also be defensible.')
p1b_closes = [101.8,100.5,99.4,98.3,99.4,100.1,99.5,98.9,100.0,99.2,98.1,99.0,100.0]
p1b = bars_from_closes(p1b_closes, 104, {3:(97.7,None),7:(98.4,None),10:(97.5,None)})
save_dataset('L01_PRACTICE_B_ambiguous_reactions', p1b)
draw_chart('L01-PRACTICE-B-01-clean', 'L01_PRACTICE_B_ambiguous_reactions', p1b, 'practice, ambiguous evidence',
           alt_text='Illustrative practice chart with uneven lower reactions; the evidence for one precise repeated area is weaker and uncertainty is reasonable.')
draw_chart('L01-PRACTICE-B-02-reference', 'L01_PRACTICE_B_ambiguous_reactions', p1b, 'practice uncertainty reference',
           bands=[{'low':97.5,'high':98.8,'label':'broad candidate area'}],
           extra_text=[{'x':1,'y':101.5,'text':'Evidence is less clustered; “unclear” is acceptable','fontsize':8.5}],
           alt_text='Same ambiguous practice chart with a broad candidate area and a note that uncertainty is acceptable.')

# --- Lesson 2: broad structure ---
l02a = bars_from_closes([100,101.2,100.5,102.1,101.2,103.0,102.2,104.2,103.3,105.4,104.6,106.0,105.1,107.0,106.2,108.1], 201)
save_dataset('L02_A_rising_structure', l02a)
markers_up = [{'bar':3,'kind':'low','label':'Swing low','color':SELECTED},{'bar':4,'kind':'high','label':'Swing high','color':SELECTED},
              {'bar':7,'kind':'low','label':'Higher low','color':SELECTED},{'bar':8,'kind':'high','label':'Higher high','color':SELECTED},
              {'bar':11,'kind':'low','label':'Higher low','color':SELECTED},{'bar':12,'kind':'high','label':'Higher high','color':SELECTED},
              {'bar':13,'kind':'low','label':'Higher low','color':SELECTED},{'bar':14,'kind':'high','label':'Higher high','color':SELECTED}]
draw_chart('L02-A-01-clean', 'L02_A_rising_structure', l02a, 'clean rising sequence',
           alt_text='Illustrative rising candlestick sequence with several pullbacks and generally higher turning points.')
draw_chart('L02-A-02-turns', 'L02_A_rising_structure', l02a, 'major turn points marked',
           markers=[{'bar':3,'kind':'low','label':'L1'},{'bar':4,'kind':'high','label':'H1'}, {'bar':5,'kind':'low','label':'L2'}, {'bar':6,'kind':'high','label':'H2'},
                    {'bar':7,'kind':'low','label':'L3'}, {'bar':8,'kind':'high','label':'H3'}],
           alt_text='Same rising chart with a few relative turning points marked for instruction; labels are illustrative examples rather than trade signals.')
draw_chart('L02-A-03-structure-reference', 'L02_A_rising_structure', l02a, 'relative highs and lows reference',
           markers=markers_up,
           alt_text='Same rising chart with a restrained reference set identifying generally higher highs and higher lows.')

l02b_closes = [108.2,107.1,107.8,105.8,106.4,104.2,104.9,103.0,103.7,101.6,102.4,100.3,100.9,99.0,99.7,97.8]
l02b = bars_from_closes(l02b_closes, 202)
save_dataset('L02_B_falling_structure', l02b)
draw_chart('L02-B-01-clean', 'L02_B_falling_structure', l02b, 'clean falling sequence',
           alt_text='Illustrative falling sequence with upward retracements and generally lower turning points.')
draw_chart('L02-B-02-structure-reference', 'L02_B_falling_structure', l02b, 'relative highs and lows reference',
           markers=[{'bar':3,'kind':'high','label':'Lower high'},{'bar':4,'kind':'low','label':'Lower low'},
                    {'bar':7,'kind':'high','label':'Lower high'},{'bar':8,'kind':'low','label':'Lower low'},
                    {'bar':11,'kind':'high','label':'Lower high'},{'bar':12,'kind':'low','label':'Lower low'}],
           alt_text='Same falling chart with a reference selection of generally lower highs and lower lows.')

l02c_closes = [100,101.2,102.0,101.3,100.2,99.0,98.8,99.7,101.0,102.4,101.5,100.1,99.0,98.5,99.6,101.2,102.0,101.0,99.9,98.9,99.5,100.8]
l02c = bars_from_closes(l02c_closes, 203)
save_dataset('L02_C_trading_range', l02c)
draw_chart('L02-C-01-clean', 'L02_C_trading_range', l02c, 'range sequence, no boundaries',
           alt_text='Illustrative chart moving back and forth inside a broad region, with uneven highs and lows rather than perfectly flat boundaries.')
draw_chart('L02-C-02-major-turns', 'L02_C_trading_range', l02c, 'major turns revealed',
           markers=[{'bar':3,'kind':'high','label':'High'},{'bar':7,'kind':'low','label':'Low'},{'bar':10,'kind':'high','label':'High'},
                    {'bar':14,'kind':'low','label':'Low'},{'bar':17,'kind':'high','label':'High'},{'bar':20,'kind':'low','label':'Low'}],
           alt_text='Same range chart with major turning points revealed before any range bracket is added.')
draw_chart('L02-C-03-range-reference', 'L02_C_trading_range', l02c, 'broad range bracket',
           bands=[{'low':98.4,'high':102.6,'label':'Trading range'}],
           alt_text='Same range chart with a broad bracket showing the approximate trading region, not a support/resistance teaching overlay.')

l02d_closes = [99,100.2,99.7,101.1,100.5,102.0,101.4,103.1,102.6,104.2,103.3,105.0,104.4,104.8,103.9,104.7,103.8,104.4,103.6,104.3,103.7,104.2,103.5,104.0,103.4,104.1]
l02d = bars_from_closes(l02d_closes, 204)
save_dataset('L02_D_trend_to_range', l02d)
draw_chart('L02-D-01-early-state', 'L02_D_trend_to_range', l02d, 'early state; future candles hidden', visible_bars=13,
           extra_text=[{'x':0.4,'y':106.0,'text':'Earlier: rising structure','fontsize':9}],
           alt_text='First segment of an illustrative rise with the later candles hidden; early structure is directional but the transition is not yet established.')
draw_chart('L02-D-02-later-state', 'L02_D_trend_to_range', l02d, 'later state; overlap revealed', visible_bars=26,
           extra_text=[{'x':0.4,'y':106.0,'text':'Earlier: rising structure','fontsize':9}, {'x':16.0,'y':105.7,'text':'Later: less directional / possible range','fontsize':9}],
           alt_text='Full illustrative sequence shows the earlier rise giving way to more overlapping, less directional movement and a possible range.')

l02e_closes = [108.5,107.0,107.7,105.6,106.5,104.4,105.1,102.8,103.6,101.8,102.4,101.6,102.1,101.3,102.0,101.4,102.2,101.7,102.4,101.9,102.6,102.0]
l02e = bars_from_closes(l02e_closes, 205)
save_dataset('L02_E_independent_practice', l02e)
draw_chart('L02-E-01-practice', 'L02_E_independent_practice', l02e, 'independent practice, answer hidden',
           alt_text='Illustrative independent practice chart showing a decline that becomes less directional and develops into overlapping movement.')
draw_chart('L02-E-02-reference', 'L02_E_independent_practice', l02e, 'reference interpretation after attempt',
           extra_text=[{'x':0.7,'y':109.5,'text':'Reference read: earlier decline → later overlap / possible range','fontsize':9}],
           markers=[{'bar':4,'kind':'high','label':'Lower high'},{'bar':6,'kind':'low','label':'Lower low'}, {'bar':8,'kind':'high','label':'Lower high'},
                    {'bar':10,'kind':'low','label':'Lower low'}, {'bar':14,'kind':'low','label':'Range low?','color':OPTIONAL}, {'bar':19,'kind':'high','label':'Range high?','color':OPTIONAL}],
           alt_text='Reference view of the practice chart: earlier decline followed by later overlap; exact transition point remains interpretive.')

# --- Lesson 3: selecting major swings from clutter ---
l03a_closes = [100,102.0,99.6,101.0,98.4,100.0,97.3,99.2,96.1,98.4,94.9,97.1,94.0,96.7,94.7,97.5,95.2,98.3,96.0,99.2,97.3,100.3,98.8,101.2,99.3,100.8,99.7]
l03a = bars_from_closes(l03a_closes, 301)
save_dataset('L03_A_overmarked_teaching', l03a)
draw_chart('L03-A-01-clean', 'L03_A_overmarked_teaching', l03a, 'over-marked chart; initial view',
           alt_text='Illustrative chart with many local turns along a broad down-then-up path; no candidate points are initially marked.')
candidates_a = [{'bar':2,'kind':'high','label':'C1','color':MUTED},{'bar':3,'kind':'low','label':'C2','color':MUTED},
                {'bar':4,'kind':'high','label':'C3','color':MUTED},{'bar':5,'kind':'low','label':'C4','color':MUTED},
                {'bar':6,'kind':'high','label':'C5','color':MUTED},{'bar':7,'kind':'low','label':'C6','color':MUTED},
                {'bar':10,'kind':'high','label':'C7','color':MUTED},{'bar':13,'kind':'low','label':'C8','color':MUTED},
                {'bar':14,'kind':'high','label':'C9','color':MUTED},{'bar':17,'kind':'low','label':'C10','color':MUTED},
                {'bar':20,'kind':'high','label':'C11','color':MUTED}]
draw_chart('L03-A-02-candidate-turns', 'L03_A_overmarked_teaching', l03a, 'candidate points available', markers=candidates_a,
           alt_text='Same chart with candidate turning points identified by neutral IDs, including major swings and minor fluctuations.')
ref_a = [{'bar':2,'kind':'high','label':'Major high'},{'bar':13,'kind':'low','label':'Major low'},
         {'bar':20,'kind':'high','label':'Recovery high'},{'bar':23,'kind':'low','label':'Pullback low'}, {'bar':24,'kind':'high','label':'Later high'}]
draw_chart('L03-A-03-reference-points', 'L03_A_overmarked_teaching', l03a, 'reference set with rationale markers', markers=ref_a,
           alt_text='Reference selection highlights a smaller set of structural turns that explain the broader path, leaving minor fluctuations unmarked.')
draw_chart('L03-A-04-simplified', 'L03_A_overmarked_teaching', l03a, 'simplified view after removing minor marks', markers=ref_a,
           extra_text=[{'x':0.5,'y':103.2,'text':'Keep the turns that explain the path; alternatives may be defensible','fontsize':9}],
           alt_text='Simplified chart that retains only the reference structural turns; this is one reasoned selection, not a uniquely correct set.')

l03b_closes = [99,100.5,98.7,101.0,99.6,102.4,100.9,103.0,101.8,102.8,101.4,103.4,102.0,104.0,102.6,103.5,101.9,103.0,101.7,102.7,101.4,102.8,101.6,103.2]
l03b = bars_from_closes(l03b_closes, 302)
save_dataset('L03_B_independent_practice', l03b)
draw_chart('L03-B-01-practice', 'L03_B_independent_practice', l03b, 'independent practice; answer hidden',
           alt_text='Illustrative practice chart with a rising but uneven path and several minor turns competing for attention.')
ref_b = [{'bar':3,'kind':'low','label':'Swing low'},{'bar':6,'kind':'high','label':'Swing high'},
         {'bar':7,'kind':'low','label':'Higher low'},{'bar':14,'kind':'high','label':'Higher high'},
         {'bar':19,'kind':'low','label':'Borderline low','color':OPTIONAL},{'bar':21,'kind':'low','label':'Later low'}]
draw_chart('L03-B-02-reference', 'L03_B_independent_practice', l03b, 'reference selection and borderline candidate', markers=ref_b,
           extra_text=[{'x':0.5,'y':105.0,'text':'Borderline point: explain whether it helps your reading','fontsize':8.5}],
           alt_text='Reference view shows a selected set of structural points and one borderline candidate that can reasonably be discussed either way.')

# --- Lesson 4: zones instead of exact lines ---
l04a_closes = [101.0,100.4,99.5,98.8,99.6,100.8,101.2,100.3,99.1,98.9,99.8,100.6,101.3,100.7,99.4,99.1,99.8,100.8,101.4,100.9,102.0,101.5]
wick04a = {3:(97.95,None),8:(98.1,None),14:(98.35,None)}
l04a = bars_from_closes(l04a_closes, 401, wick04a)
# Keep the reaction bodies/closes around/above the lower extremes to make the area visibly broader than one exact low.
save_dataset('L04_A_lower_reactions_wick_body_variation', l04a)
draw_chart('L04-A-01-clean', 'L04_A_lower_reactions_wick_body_variation', l04a, 'lower reactions without boundaries',
           alt_text='Illustrative candles show three lower reactions with modestly different wick lows and bodies/closes positioned somewhat above the lowest extremes.')
draw_chart('L04-A-02-broad-bracket', 'L04_A_lower_reactions_wick_body_variation', l04a, 'broad neutral bracket',
           bands=[{'low':97.9,'high':99.5,'label':'related reaction area'}],
           alt_text='Same lower reaction chart with a broad neutral bracket around the related reaction area.')
draw_chart('L04-A-03-too-narrow', 'L04_A_lower_reactions_wick_body_variation', l04a, 'too-narrow boundary comparison',
           bands=[{'low':97.95,'high':98.12,'label':'too narrow to explain the cluster','alpha':0.42}],
           alt_text='Same chart with an extremely narrow band around only the lowest wick points, illustrating a boundary that omits much of the related response area.')
draw_chart('L04-A-04-defensible-zone', 'L04_A_lower_reactions_wick_body_variation', l04a, 'one defensible reference zone',
           bands=[{'low':97.9,'high':99.15,'label':'one defensible support area'}],
           alt_text='Same chart with one defensible support zone around the clustered lower reactions; another consistently justified boundary may also be acceptable.')
draw_chart('L04-A-05-too-broad', 'L04_A_lower_reactions_wick_body_variation', l04a, 'too-broad boundary comparison',
           bands=[{'low':97.2,'high':101.0,'label':'too broad to isolate the reactions','alpha':0.2}],
           alt_text='Same chart with a band so broad that it covers a large amount of unrelated price movement and does not isolate the lower reactions well.')
# Comparison chart with all candidate bands; labels placed in a side legend instead of overlapping the candles.
draw_chart('L04-A-06-compare', 'L04_A_lower_reactions_wick_body_variation', l04a, 'compare boundary choices',
           bands=[{'low':97.95,'high':98.12,'label':None,'color':'#DCA06A','alpha':0.42,'edge_color':'#A85B1B'},
                  {'low':97.9,'high':99.15,'label':None,'color':BAND,'alpha':0.22,'edge_color':BAND_EDGE},
                  {'low':97.2,'high':101.0,'label':None,'color':'#9BAEC2','alpha':0.12,'edge_color':'#7B8B99'}],
           extra_text=[{'x':0.5,'y':102.8,'text':'Narrow = misses reactions   |   Middle = defensible example   |   Broad = loses focus','fontsize':8.7}],
           alt_text='Same chart compares narrow, moderate and overly broad bands so learners can assess what each includes and excludes.')

l04b_closes = [100.0,101.2,102.1,103.3,104.0,103.4,102.5,101.9,102.6,103.8,104.7,104.1,103.0,102.1,103.0,104.2,104.6,103.5,102.4,101.8]
l04b = bars_from_closes(l04b_closes, 402, {4:(None,105.15),10:(None,105.3),16:(None,105.05)})
save_dataset('L04_B_upper_reactions', l04b)
draw_chart('L04-B-01-clean', 'L04_B_upper_reactions', l04b, 'upper reactions without boundaries',
           alt_text='Illustrative candles rise into a broad upper region and turn downward on several occasions with slightly different wick highs.')
draw_chart('L04-B-02-zone', 'L04_B_upper_reactions', l04b, 'defensible upper zone',
           bands=[{'low':103.5,'high':105.35,'label':'one defensible upper area'}],
           alt_text='Same upper reaction sequence with a broad band around the group of upper reactions.')
draw_chart('L04-B-03-resistance', 'L04_B_upper_reactions', l04b, 'upper area labelled resistance',
           bands=[{'low':103.5,'high':105.35,'label':'resistance area'}],
           alt_text='Same chart with the reference upper area labelled resistance area after the boundary is discussed.')

l04c_closes = [102.0,100.9,99.7,98.5,99.4,100.5,101.1,100.0,98.9,99.7,100.8,101.5,100.7,99.5,98.7,99.6,100.6,101.4]
l04c = bars_from_closes(l04c_closes, 403, {3:(97.2,None),8:(97.55,None),14:(97.4,None)})
save_dataset('L04_C_independent_practice', l04c)
draw_chart('L04-C-01-practice', 'L04_C_independent_practice', l04c, 'independent zone practice; answer hidden',
           alt_text='Illustrative practice chart with related lower reactions whose wick lows vary modestly; students must draw and justify a useful band.')
draw_chart('L04-C-02-reference', 'L04_C_independent_practice', l04c, 'one acceptable reference zone',
           bands=[{'low':97.2,'high':98.9,'label':'one defensible zone'}],
           extra_text=[{'x':0.5,'y':103.2,'text':'Alternative boundaries may be reasonable if explained consistently','fontsize':8.6}],
           alt_text='Reference view of the practice chart shows one defensible lower zone and notes that alternative boundaries may be reasonable.')

# --- Lesson 5: selection and clutter reduction ---
l05_closes = [100.2,101.0,102.8,101.9,104.1,103.0,101.4,100.1,99.0,99.8,101.2,102.0,101.2,100.0,99.2,100.5,102.2,103.8,102.6,101.4,100.5,101.6,102.5,101.8]
l05 = bars_from_closes(l05_closes, 501, {8:(98.65,None),14:(98.7,None),4:(None,104.8),17:(None,104.7)})
save_dataset('L05_A_overmarked_selection', l05)
l05_all_bands = [
    {'low':98.7,'high':99.35,'label':None,'alpha':0.13},
    {'low':99.2,'high':99.65,'label':None,'alpha':0.12,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':101.35,'high':101.75,'label':None,'alpha':0.12,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':101.65,'high':102.15,'label':None,'alpha':0.12},
    {'low':103.4,'high':104.7,'label':None,'alpha':0.13},
    {'low':100.25,'high':100.65,'label':None,'alpha':0.12,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':96.0,'high':96.45,'label':None,'alpha':0.12,'color':'#9BAEC2','edge_color':'#7B8B99'},
]
draw_chart('L05-A-01-overmarked', 'L05_A_overmarked_selection', l05, 'cluttered candidate marks', bands=l05_all_bands,
           alt_text='Illustrative chart with seven subdued candidate horizontal bands: some overlap, some mark minor movement, one is far from current price, and key structure is mixed with clutter.')
draw_chart('L05-A-02-candidate-ids', 'L05_A_overmarked_selection', l05, 'candidate bands available for selection', bands=l05_all_bands,
           extra_text=[{'x':0.3,'y':104.95,'text':'A','fontsize':8.5},{'x':0.3,'y':102.2,'text':'B','fontsize':8.5},
                       {'x':0.3,'y':101.83,'text':'C','fontsize':8.5},{'x':0.3,'y':100.78,'text':'D','fontsize':8.5},
                       {'x':0.3,'y':99.78,'text':'E','fontsize':8.5},{'x':0.3,'y':99.08,'text':'F','fontsize':8.5},
                       {'x':0.3,'y':96.55,'text':'G','fontsize':8.5}],
           alt_text='Same cluttered chart with candidate IDs added at the left so each band can be selected without pre-classifying it.')
draw_chart('L05-A-03-reduced-reference', 'L05_A_overmarked_selection', l05, 'reference edit: retain key areas and remove clutter',
           bands=[{'low':98.65,'high':99.55,'label':'lower reaction / range area'}, {'low':103.4,'high':104.7,'label':'upper reaction area'}],
           extra_text=[{'x':0.5,'y':103.0,'text':'Nearby marks combined; minor/distant marks omitted for this chart question','fontsize':8.7}],
           alt_text='Reference edit retains a defensible lower reaction area and upper reaction area while omitting redundant nearby marks, a minor fluctuation and a distant level.')

# ChartLab 1: Clear W — reference views to accompany the interaction, not a substitute for it.
cl01_closes = [105.0,103.2,101.2,99.4,98.1,99.3,101.3,103.2,102.1,100.5,98.45,99.5,101.0,102.4,102.1,101.4]
cl01 = bars_from_closes(cl01_closes, 502, {4:(97.75,None),10:(98.05,None),7:(None,103.8)})
save_dataset('CL01_clear_W', cl01)
draw_chart('CL01-01-clean', 'CL01_clear_W', cl01, 'Clear W; no reference overlays',
           alt_text='Illustrative W-like price sequence with two related lower reactions and an upper reaction between them; no zones are drawn.')
draw_chart('CL01-02-support-reference', 'CL01_clear_W', cl01, 'Clear W support reference only',
           bands=[{'low':97.75,'high':99.15,'label':'one defensible support area'}],
           alt_text='Clear W illustrative sequence with the two lower reactions grouped by a defensible support band; resistance remains unmarked.')
draw_chart('CL01-03-resistance-reference', 'CL01_clear_W', cl01, 'Clear W resistance reference only',
           bands=[{'low':102.5,'high':103.85,'label':'one defensible upper area'}],
           alt_text='Clear W illustrative sequence with the intervening upper reaction marked as one defensible resistance area; support remains unmarked.')
draw_chart('CL01-04-combined-reference', 'CL01_clear_W', cl01, 'Clear W combined reference',
           bands=[{'low':97.75,'high':99.15,'label':'support area','x':1}, {'low':102.5,'high':103.85,'label':'resistance area','x':10}],
           alt_text='Clear W illustrative sequence with both support and resistance reference bands shown after the learner has submitted both drawings.')

# --- Lesson 6: defend the boundaries with a different chart set ---
l06a_closes = [103.0,101.8,100.2,98.9,100.1,101.4,100.0,98.5,99.6,101.2,102.0,100.8,99.5,98.7,99.8,101.4,102.1]
l06a = bars_from_closes(l06a_closes, 601, {3:(97.85,None),7:(98.1,None),13:(98.0,None)})
save_dataset('L06_A_lower_boundary_practice', l06a)
draw_chart('L06-A-01-clean', 'L06_A_lower_boundary_practice', l06a, 'lower reactions; boundaries hidden',
           alt_text='Illustrative support-boundary practice chart with three lower reactions, modestly varied wick extremes and bodies/closes around the same broad region.')
draw_chart('L06-A-02-reaction-points', 'L06_A_lower_boundary_practice', l06a, 'relevant low reactions identified',
           markers=[{'bar':4,'kind':'low','label':'Reaction 1'},{'bar':8,'kind':'low','label':'Reaction 2'},{'bar':14,'kind':'low','label':'Reaction 3'}],
           alt_text='Same lower reaction chart with the three teaching-relevant low points marked before boundary options are shown.')
draw_chart('L06-A-03-wick-body-guides', 'L06_A_lower_boundary_practice', l06a, 'wick/body guide state',
           bands=[{'low':98.0,'high':98.45,'label':'wick extremes','alpha':0.18,'color':'#9BAEC2','edge_color':'#7B8B99'},
                  {'low':98.7,'high':99.65,'label':'body / close region','alpha':0.14}],
           alt_text='Same chart with separate guide bands highlighting variation between wick extremes and nearby body/close behaviour.')
draw_chart('L06-A-04-too-narrow', 'L06_A_lower_boundary_practice', l06a, 'too-narrow zone',
           bands=[{'low':97.9,'high':98.18,'label':'too narrow for the full reaction area'}],
           alt_text='Same chart with a very narrow band near only the lowest wick tips, illustrating how the choice can omit related body and response behaviour.')
draw_chart('L06-A-05-defensible', 'L06_A_lower_boundary_practice', l06a, 'one defensible zone',
           bands=[{'low':97.85,'high':99.35,'label':'one defensible support zone'}],
           alt_text='Same chart with one defensible support zone that groups the relevant lower reactions while keeping the area distinct from unrelated candles.')
draw_chart('L06-A-06-too-broad', 'L06_A_lower_boundary_practice', l06a, 'overly broad zone',
           bands=[{'low':97.2,'high':101.0,'label':'too broad; loses focus','alpha':0.19}],
           alt_text='Same chart with an overly broad area that captures unrelated price movement and weakens the explanation of the actual reaction cluster.')

l06b_closes = [98.8,100.0,101.3,103.0,104.1,103.4,102.3,101.5,102.4,103.8,104.4,103.6,102.2,101.2,102.1,103.5,104.0,102.8,101.9]
l06b = bars_from_closes(l06b_closes, 602, {4:(None,105.1),10:(None,105.35),16:(None,105.0)})
save_dataset('L06_B_upper_boundary_practice', l06b)
draw_chart('L06-B-01-clean', 'L06_B_upper_boundary_practice', l06b, 'upper reactions; boundaries hidden',
           alt_text='Illustrative resistance-boundary practice chart showing several upper reactions with slightly different wick highs and nearby bodies/closes.')
draw_chart('L06-B-02-defensible', 'L06_B_upper_boundary_practice', l06b, 'one defensible resistance zone',
           bands=[{'low':103.2,'high':105.35,'label':'one defensible resistance zone'}],
           alt_text='Same upper reaction chart with one defensible resistance band that captures the related upper reactions.')

l06c_closes = [103,101.5,99.8,98.5,99.8,101.2,100.4,99.0,99.7,101.3,102.0,100.6,98.9,99.9,101.5,102.5]
l06c = bars_from_closes(l06c_closes, 603, {3:(97.5,None),7:(97.9,None),12:(97.7,None)})
save_dataset('L06_C_independent_boundary_practice', l06c)
draw_chart('L06-C-01-practice', 'L06_C_independent_boundary_practice', l06c, 'independent boundary practice; answer hidden',
           alt_text='Unlabelled illustrative practice chart with clustered lower reactions, modestly varying wick lows and a distinct sequence away from the region.')
draw_chart('L06-C-02-reference', 'L06_C_independent_boundary_practice', l06c, 'reference zone and rationale',
           bands=[{'low':97.5,'high':99.25,'label':'one defensible support zone'}],
           extra_text=[{'x':0.5,'y':104.2,'text':'Explain both edges and name one nearby move you chose not to include','fontsize':8.7}],
           alt_text='Reference view of the independent chart showing one defensible zone and a prompt to explain included and excluded price action.')

# --- Lesson 7: chart editing with contextual reasons ---
l07a_closes = [99.5,100.3,101.5,102.4,101.3,100.1,99.0,99.8,101.2,102.2,101.5,100.3,99.2,100.0,101.0,102.5,104.0,103.0,101.8,100.7,101.5,102.4]
l07a = bars_from_closes(l07a_closes, 701, {6:(98.65,None),12:(98.75,None),16:(None,104.8)})
save_dataset('L07_A_overmarked_editing_demo', l07a)
l07_bands = [
    {'low':98.7,'high':99.35,'label':None,'alpha':0.14},
    {'low':99.25,'high':99.75,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':100.3,'high':100.7,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':101.5,'high':102.05,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':102.0,'high':102.65,'label':None,'alpha':0.11},
    {'low':103.4,'high':104.8,'label':None,'alpha':0.14},
    {'low':96.4,'high':96.85,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
]
draw_chart('L07-A-01-overmarked', 'L07_A_overmarked_editing_demo', l07a, 'overmarked demonstration', bands=l07_bands,
           alt_text='Illustrative chart with seven candidate zones, including two nearby overlapping areas, a minor fluctuation, a distant mark and the key lower/upper structure.')
draw_chart('L07-A-02-merge-redundant', 'L07_A_overmarked_editing_demo', l07a, 'first edit: merge redundant lower areas',
           bands=[{'low':98.55,'high':99.8,'label':'merged lower area'}, *l07_bands[2:]],
           alt_text='Same chart after two nearby lower bands have been merged into one broader area because they describe the same general reaction region.')
draw_chart('L07-A-03-contextual-omissions', 'L07_A_overmarked_editing_demo', l07a, 'second edit: omit minor and distant marks',
           bands=[{'low':98.55,'high':99.8,'label':'retained lower area'}, {'low':103.4,'high':104.8,'label':'retained upper area'}],
           extra_text=[{'x':0.4,'y':103.0,'text':'The omitted marks are less useful for this question; they are not declared irrelevant forever','fontsize':8.5}],
           alt_text='Edited chart retains the major lower and upper areas and omits low-relevance marks for this specific chart-reading question.')
draw_chart('L07-A-04-clean-final', 'L07_A_overmarked_editing_demo', l07a, 'final clean view',
           bands=[{'low':98.55,'high':99.8,'label':'lower reaction area'}, {'low':103.4,'high':104.8,'label':'upper reaction area'}],
           alt_text='Final edited chart with only the two areas needed to explain the current structure; it is not claimed to be the only possible clean chart.')

l07b_closes = [105,103,101,100,101,102.5,101.6,100.2,99.3,100.1,101.7,102.6,101.5,100.4,99.1,99.8,101.1,102.2,103.4]
l07b = bars_from_closes(l07b_closes, 702, {8:(98.75,None),14:(98.55,None),18:(None,104.1)})
save_dataset('L07_B_independent_editing', l07b)
l07b_bands = [
    {'low':98.7,'high':99.4,'label':None,'alpha':0.13},
    {'low':99.25,'high':99.75,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':100.25,'high':100.75,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':102.1,'high':102.7,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
    {'low':103.1,'high':104.25,'label':None,'alpha':0.13},
    {'low':96.8,'high':97.3,'label':None,'alpha':0.11,'color':'#9BAEC2','edge_color':'#7B8B99'},
]
draw_chart('L07-B-01-practice', 'L07_B_independent_editing', l07b, 'independent chart editing practice', bands=l07b_bands,
           alt_text='Independent illustrative practice chart with six candidate bands, including a redundant lower pair, a minor area, relevant upper structure and a distant band.')
draw_chart('L07-B-02-reference', 'L07_B_independent_editing', l07b, 'one reference edited view',
           bands=[{'low':98.6,'high':99.75,'label':'retained lower area'}, {'low':103.1,'high':104.25,'label':'retained upper area'}],
           extra_text=[{'x':0.4,'y':102.7,'text':'An additional area can be retained if its distinct role is explained','fontsize':8.5}],
           alt_text='One reference edit removes redundant and less relevant marks while retaining the main lower and upper areas; another defensible edit may preserve a distinct middle area.')

# --- Lesson 8: evaluate qualitatively, not by touch count ---
l08a_closes = [100,101,100.3,101.2,100.4,101.3,100.2,101.4,100.4,101.2,100.0,101.3,100.4,101.4,100.6,101.2,100.3,101.4,100.4,101.3]
l08a = bars_from_closes(l08a_closes, 801, {3:(99.1,None),5:(99.15,None),7:(99.05,None),9:(99.2,None),11:(99.0,None),13:(99.1,None),15:(99.05,None),17:(99.2,None)})
save_dataset('L08_A_many_crossings_incoherent', l08a)
draw_chart('L08-A-01-many-crossings', 'L08_A_many_crossings_incoherent', l08a, 'Area A: many contacts, mixed behaviour',
           bands=[{'low':100.0,'high':101.15,'label':'Area A','alpha':0.18}],
           alt_text='Illustrative chart in which price crosses and revisits a band many times with overlapping, less coherent behaviour; contact count alone is not a quality verdict.')
l08b_closes = [104,102.5,100.9,99.5,100.5,102.2,103.0,101.2,99.7,100.6,102.3,103.4,104.0,102.6,101.5]
l08b = bars_from_closes(l08b_closes, 802, {3:(98.9,None),8:(99.05,None)})
save_dataset('L08_A_fewer_interpretable_reactions', l08b)
draw_chart('L08-A-02-fewer-interpretable', 'L08_A_fewer_interpretable_reactions', l08b, 'Area B: fewer, clearer contextual reactions',
           bands=[{'low':98.95,'high':100.0,'label':'Area B','alpha':0.18}],
           alt_text='Illustrative chart with fewer visits to an area but more interpretable reactions within a clearer structural sequence; this does not establish guaranteed predictive strength.')
draw_chart('L08-A-03-comparison-A', 'L08_A_many_crossings_incoherent', l08a, 'Compare Area A: evidence and uncertainty',
           bands=[{'low':100.0,'high':101.15,'label':'Area A','alpha':0.18}],
           extra_text=[{'x':0.3,'y':102.4,'text':'Ask: what does the structure explain, beyond the number of contacts?','fontsize':8.6}],
           alt_text='Area A comparison state emphasises repeated crossings and asks learners to examine the structure and current behaviour rather than count contacts.')
draw_chart('L08-A-04-comparison-B', 'L08_A_fewer_interpretable_reactions', l08b, 'Compare Area B: evidence and uncertainty',
           bands=[{'low':98.95,'high':100.0,'label':'Area B','alpha':0.18}],
           extra_text=[{'x':0.3,'y':105.2,'text':'Ask: why might fewer reactions still be more interpretable here?','fontsize':8.6}],
           alt_text='Area B comparison state asks why fewer reactions can be more interpretable in context, without asserting that it must hold or has a known probability.')

# ChartLab 2: Uneven Lows — reference views for the activity companion.
cl02_closes = [104.0,102.5,100.8,98.8,100.0,101.4,103.2,102.3,100.8,98.0,99.4,101.2,102.6,101.5,100.2,98.35,99.6,101.4,103.1,104.0]
cl02 = bars_from_closes(cl02_closes, 803, {3:(97.95,None),9:(97.25,None),15:(97.8,None),6:(None,103.8),18:(None,103.6)})
save_dataset('CL02_uneven_lows', cl02)
draw_chart('CL02-01-clean', 'CL02_uneven_lows', cl02, 'Uneven Lows; no reference overlays',
           alt_text='Illustrative sequence with two lower reactions at slightly different lows and a separate upper reaction area; all zones are initially hidden.')
draw_chart('CL02-02-support-reference', 'CL02_uneven_lows', cl02, 'Uneven Lows support reference',
           bands=[{'low':97.25,'high':99.0,'label':'one defensible support zone'}],
           alt_text='Uneven Lows chart with a support band that captures two lower reactions whose wick lows are not perfectly aligned.')
draw_chart('CL02-03-resistance-reference', 'CL02_uneven_lows', cl02, 'Uneven Lows resistance reference',
           bands=[{'low':102.5,'high':104.0,'label':'one defensible upper area'}],
           alt_text='Uneven Lows chart with the distinct upper reaction area shown as a separate resistance reference.')
draw_chart('CL02-04-combined-reference', 'CL02_uneven_lows', cl02, 'Uneven Lows combined reference',
           bands=[{'low':97.25,'high':99.0,'label':'support area','x':1}, {'low':102.5,'high':104.0,'label':'resistance area','x':10}],
           alt_text='Uneven Lows chart with both support and resistance reference zones visible after the learner submits both drawings.')

# --- Lesson 9: examine the approach before the interaction ---
l09a_closes = [96.5,97.3,98.4,97.9,99.0,98.7,100.0,99.6,101.0,100.5,102.0,101.8,103.0]
l09a = bars_from_closes(l09a_closes, 901)
save_dataset('L09_A_directional_approach', l09a)
draw_chart('L09-A-01-directional-approach', 'L09_A_directional_approach', l09a, 'controlled approach A; later interaction hidden',
           bands=[{'low':104.0,'high':105.2,'label':'previously identified area'}],
           alt_text='Illustrative price sequence advancing toward a previously identified upper area with relatively directional steps; the interaction with the area is not shown.')
l09b_closes = [97.0,98.0,98.7,98.3,99.4,99.0,100.0,99.5,100.6,100.1,101.2,100.5,101.4,101.0,102.0]
l09b = bars_from_closes(l09b_closes, 902)
save_dataset('L09_B_overlapping_approach', l09b)
draw_chart('L09-B-01-overlapping-approach', 'L09_B_overlapping_approach', l09b, 'controlled approach B; later interaction hidden',
           bands=[{'low':103.0,'high':104.1,'label':'previously identified area'}],
           alt_text='Illustrative price sequence approaching a previously identified upper area with overlapping candles, pauses and less direct progress.')
l09p_closes = [104.0,103.0,102.2,102.7,101.5,101.9,100.7,100.9,99.8,100.1]
l09p = bars_from_closes(l09p_closes, 903, {8:(99.1,None)})
save_dataset('L09_C_independent_approach_practice', l09p)
draw_chart('L09-PRACTICE-01-clean', 'L09_C_independent_approach_practice', l09p, 'independent approach practice',
           bands=[{'low':98.8,'high':99.8,'label':'previously identified area'}],
           alt_text='Illustrative practice chart approaching a lower area with a mix of directional movement and pauses; learner describes visible approach behaviour.')
draw_chart('L09-PRACTICE-02-reference', 'L09_C_independent_approach_practice', l09p, 'approach observations reference',
           bands=[{'low':98.8,'high':99.8,'label':'previously identified area'}],
           extra_text=[{'x':0.5,'y':104.9,'text':'Describe pace, overlap, swing sequence and remaining distance; do not infer the outcome','fontsize':8.5}],
           alt_text='Reference view of the approach practice chart prompts observations about pace, overlap, swing sequence and distance without revealing an outcome.')

# --- Lesson 10: rejection, acceptance, or inconclusive evidence ---
l10a_closes = [103,102,101.2,100.7,99.6,100.5,101.4,102.0,102.8,103.2,103.8]
l10a = bars_from_closes(l10a_closes, 1001, {4:(98.65,None)})
save_dataset('L10_A_reaction_then_move_away', l10a)
for suffix, cut, state in [('01-first-interaction',5,'first zone interaction only'),('02-close-away',7,'close back above zone and initial move away'),('03-follow-through',11,'subsequent movement away revealed')]:
    draw_chart(f'L10-A-{suffix}', 'L10_A_reaction_then_move_away', l10a, state, visible_bars=cut,
               bands=[{'low':99.1,'high':100.3,'label':'prior zone'}],
               alt_text=f'Progressive reveal of an illustrative sequence at a prior zone: {state}; later candles stay hidden until the next stage.')

l10b_closes = [97.8,98.7,99.5,100.4,99.9,100.7,102.2,103.5,104.2,104.8,105.6]
l10b = bars_from_closes(l10b_closes, 1002)
save_dataset('L10_B_close_beyond_follow_through', l10b)
draw_chart('L10-B-01-crossing', 'L10_B_close_beyond_follow_through', l10b, 'first close beyond zone', visible_bars=7,
           bands=[{'low':100.0,'high':101.1,'label':'prior zone'}],
           alt_text='Illustrative sequence with an initial close beyond an upper zone; subsequent holding behaviour is hidden.')
draw_chart('L10-B-02-follow-through', 'L10_B_close_beyond_follow_through', l10b, 'continued action beyond zone',
           bands=[{'low':100.0,'high':101.1,'label':'prior zone'}],
           extra_text=[{'x':0.5,'y':106.5,'text':'Several later candles continue to operate beyond the zone','fontsize':8.8}],
           alt_text='Same sequence with later candles continuing to operate above the old zone, supporting an acceptance interpretation without guaranteeing continuation.')
l10c_closes = [102.5,101.2,100.4,99.8,100.7,99.6,100.9,99.7,100.3,99.9,100.5,100.1]
l10c = bars_from_closes(l10c_closes, 1003)
save_dataset('L10_C_mixed_evidence', l10c)
draw_chart('L10-C-01-mixed', 'L10_C_mixed_evidence', l10c, 'conflicting evidence near the zone',
           bands=[{'low':99.7,'high':100.7,'label':'prior zone'}],
           alt_text='Illustrative sequence repeatedly crosses and returns around a zone; the evidence remains mixed rather than resolving clearly.')

practice10 = [
 ('PRACTICE-A','wick-through-close-back', [103,102,100.5,99.7,100.2,101.0,101.8], {3:(98.9,None)}, 'The wick passes through the band, but the close returns into the area and later candles move away.'),
 ('PRACTICE-B','close-beyond-follow-through', [98,99,100.2,101.4,102.4,103.2,104.0], {}, 'The close beyond the upper area is followed by continued action beyond it.'),
 ('PRACTICE-C','mixed-crossings', [102,100.5,99.8,100.7,99.6,100.8,99.9], {}, 'Price crosses the area repeatedly without a clean sustained resolution.'),
 ('PRACTICE-D','quick-push-no-follow-through', [98.5,99.3,100.4,101.3,100.6,100.0,99.8], {}, 'A move beyond the upper band is quickly challenged; current classification should remain conditional.'),
]
for i,(aid,did,closes,overrides,desc) in enumerate(practice10, start=1):
    bars=bars_from_closes(closes,1010+i,overrides); save_dataset(f'L10_{did}',bars)
    band = {'low':100.0,'high':100.8,'label':'prior zone'}
    draw_chart(f'L10-{aid}-01-clean',f'L10_{did}',bars,'practice; answer hidden',bands=[band],
               alt_text=f'Illustrative practice sequence around a prior zone. {desc} No classification is preselected.')
    label = 'inconclusive / mixed' if aid in ('PRACTICE-C','PRACTICE-D') else ('rejection evidence' if aid=='PRACTICE-A' else 'acceptance evidence')
    draw_chart(f'L10-{aid}-02-reference',f'L10_{did}',bars,'practice reference after submission',bands=[{**band,'label':label}],
               extra_text=[{'x':0.4,'y':max(b['high'] for b in bars)+0.7,'text':'Classification describes this visible sequence; it is not a forecast','fontsize':8.2}],
               alt_text=f'Reference view for the practice sequence labels the intended evidence category as {label}, while stating that it is not a forecast.')

# --- Lesson 11: update the usefulness of a zone across time ---
l11_closes = [103,101,99.5,98.8,99.7,101.2,100.5,99.2,98.9,100.0,101.4,102.2,100.8,99.4,98.7,99.7,100.6,99.2,97.8,98.9,100.2,99.1,97.5,96.7]
l11 = bars_from_closes(l11_closes, 1101, {3:(98.0,None),8:(98.05,None),14:(97.85,None),18:(97.4,None),22:(97.1,None)})
save_dataset('L11_zone_significance_timeline', l11)
for suffix,cut,title,desc in [
    ('01-first-reaction',8,'timeline stage 1: initial reaction','Initial lower reaction and movement away are visible; later visits are hidden.'),
    ('02-second-visit',14,'timeline stage 2: revisit and response','A later revisit and move away are visible, adding evidence but not creating a numerical strength score.'),
    ('03-deeper-test',20,'timeline stage 3: deeper test','The area is tested more deeply; earlier reactions still matter historically, but current interpretation should be reassessed.'),
    ('04-move-through',24,'timeline stage 4: move through','Later candles move through the area, challenging its current support interpretation.')]:
    draw_chart(f'L11-{suffix}','L11_zone_significance_timeline',l11,title,visible_bars=cut,
               bands=[{'low':97.9,'high':99.1,'label':'area under review'}],
               alt_text=f'Progressive timeline reveal: {desc}')

# --- Lesson 12: breakout versus temporary penetration ---
l12a_closes = [98.5,99.0,99.5,100.3,101.1,100.4,99.6,99.1,98.8]
l12a = bars_from_closes(l12a_closes,1201,{4:(None,101.7)})
save_dataset('L12_A_temporary_penetration',l12a)
draw_chart('L12-A-01-first-crossing','L12_A_temporary_penetration',l12a,'initial crossing; return hidden',visible_bars=5,
           bands=[{'low':99.8,'high':100.7,'label':'prior zone'}],
           alt_text='Initial stage of an illustrative upward crossing of a zone; later candles that return price toward the old range remain hidden.')
draw_chart('L12-A-02-return-inside','L12_A_temporary_penetration',l12a,'later candles return inside the prior range',
           bands=[{'low':99.8,'high':100.7,'label':'prior zone'}],
           alt_text='Full illustrative sequence shows a brief move above the zone followed by price returning inside the earlier range; the initial move alone was not sustained.')
l12b_closes = [97.5,98.1,99.0,99.7,100.5,101.3,102.3,103.2,104.1,104.7,105.3]
l12b = bars_from_closes(l12b_closes,1202)
save_dataset('L12_B_crossing_with_follow_through',l12b)
draw_chart('L12-B-01-first-crossing','L12_B_crossing_with_follow_through',l12b,'first close above the zone',visible_bars=7,
           bands=[{'low':100.0,'high':101.0,'label':'prior zone'}],
           alt_text='Initial stage of a crossing above the prior zone; follow-through is held back for the next reveal.')
draw_chart('L12-B-02-follow-through','L12_B_crossing_with_follow_through',l12b,'continued movement beyond the zone',
           bands=[{'low':100.0,'high':101.0,'label':'prior zone'}],
           alt_text='Later candles continue to operate above the prior zone, providing more evidence of a sustained move but no guarantee of future continuation.')
l12c_closes = [98.5,99.4,100.6,101.2,100.2,99.7,100.8,101.5,100.4,99.8,100.5]
l12c = bars_from_closes(l12c_closes,1203)
save_dataset('L12_C_mixed_crossings',l12c)
draw_chart('L12-C-01-mixed','L12_C_mixed_crossings',l12c,'mixed crossing evidence',
           bands=[{'low':99.8,'high':100.9,'label':'prior zone'}],
           alt_text='Illustrative chart crosses and returns around a prior zone more than once, leaving the breakout interpretation inconclusive.')

# --- Lesson 13: retest and role reversal are possible, not required ---
l13_closes = [98.5,99.1,100.0,101.2,102.3,103.4,104.2,103.8,104.6,105.1,104.7,103.2,102.3]
l13 = bars_from_closes(l13_closes,1301)
save_dataset('L13_break_then_return',l13)
draw_chart('L13-A-01-break-beyond','L13_break_then_return',l13,'price beyond the former resistance zone',visible_bars=10,
           bands=[{'low':101.0,'high':102.0,'label':'former resistance'}],
           alt_text='Illustrative chart moves above a former resistance band; no return to the zone is visible yet.')
draw_chart('L13-B-01-return-to-area','L13_break_then_return',l13,'return to the prior area revealed',
           bands=[{'low':101.0,'high':102.0,'label':'former resistance'}],
           alt_text='Later candles show price returning toward the former resistance area; its possible new role remains a hypothesis, not a conclusion.')

l13hold_closes = [98,99,100,101,102.5,103.5,104.0,103.0,102.2,102.8,103.7,104.5]
l13hold = bars_from_closes(l13hold_closes,1302)
save_dataset('L13_role_reversal_holds',l13hold)
draw_chart('L13-C1-hold','L13_role_reversal_holds',l13hold,'comparison outcome: return holds beyond the old zone',
           bands=[{'low':100.5,'high':101.6,'label':'former resistance'}],
           extra_text=[{'x':0.4,'y':106.0,'text':'Possible role reversal: evidence supports the idea, but it is not guaranteed','fontsize':8.4}],
           alt_text='One illustrative return-to-area sequence holds beyond former resistance and moves away again; it supports but does not prove a role-reversal interpretation.')
l13fail_closes = [98,99,100,101.2,102.3,103.4,104.0,102.6,101.1,100.2,99.4,98.8]
l13fail = bars_from_closes(l13fail_closes,1303)
save_dataset('L13_role_reversal_fails',l13fail)
draw_chart('L13-C2-fail','L13_role_reversal_fails',l13fail,'comparison outcome: price moves back through the old zone',
           bands=[{'low':100.5,'high':101.6,'label':'former resistance'}],
           extra_text=[{'x':0.4,'y':105.0,'text':'A retest is not a guarantee that the old zone changes role','fontsize':8.5}],
           alt_text='Alternative illustrative return-to-area sequence moves back through former resistance and into the old range, showing that role reversal can fail.')

# --- Lesson 14: failed breakouts and alternate outcomes ---
l14a_closes = [97.8,98.4,99.2,99.7,100.5,101.0,100.6,100.1,100.4,101.2,102.2,102.8,101.9,100.7,99.8,99.3]
l14a = bars_from_closes(l14a_closes,1401)
save_dataset('L14_failed_breakout_sequence',l14a)
draw_chart('L14-A-01-area-before-break','L14_failed_breakout_sequence',l14a,'area before attempted break; later candles hidden',visible_bars=9,
           bands=[{'low':100.0,'high':101.0,'label':'prior zone'}],
           alt_text='Illustrative sequence approaches a prior zone from below; candles showing any attempted breakout and its outcome are hidden.')
draw_chart('L14-B-01-first-move-beyond','L14_failed_breakout_sequence',l14a,'first move beyond the zone',visible_bars=12,
           bands=[{'low':100.0,'high':101.0,'label':'prior zone'}],
           alt_text='The next stage shows an initial move beyond the prior zone; later evidence has not yet been revealed.')
draw_chart('L14-C-01-return-through','L14_failed_breakout_sequence',l14a,'evidence challenges the breakout thesis',
           bands=[{'low':100.0,'high':101.0,'label':'original zone'}],
           extra_text=[{'x':0.5,'y':104.0,'text':'The move beyond was not sustained in this sequence','fontsize':8.7}],
           alt_text='Later candles return through the original zone, weakening the initial breakout interpretation without making the next move certain.')
l14d_closes = [97.8,98.5,99.3,100.0,100.8,101.5,102.6,103.5,104.0,103.0,102.0,101.4,102.2,103.1,104.1]
l14d = bars_from_closes(l14d_closes,1402)
save_dataset('L14_pullback_holds',l14d)
draw_chart('L14-D-01-pullback-holds','L14_pullback_holds',l14d,'contrast: pullback remains beyond the zone',
           bands=[{'low':100.0,'high':101.0,'label':'old zone'}],
           alt_text='Contrast sequence moves beyond a zone, pulls back toward it, remains beyond it and later moves away; a pullback is not automatically a failed breakout.')

# ChartLab 3: Wider Neckline — reference views only; interaction code is out of scope here.
cl03_closes = [106,104,101.8,99.5,98.4,99.7,102.0,104.0,102.1,100.2,98.8,100.0,102.5,104.3,103.0,101.7,102.4,104.8]
cl03 = bars_from_closes(cl03_closes,1403,{4:(97.8,None),10:(98.2,None),7:(None,104.6),13:(None,104.8)})
save_dataset('CL03_wider_neckline',cl03)
draw_chart('CL03-01-clean','CL03_wider_neckline',cl03,'Wider Neckline; no reference overlays',
           alt_text='Illustrative W-like structure with two lower reactions, a broader intervening upper reaction area, and later candles approaching and moving beyond that area.')
draw_chart('CL03-02-support-reference','CL03_wider_neckline',cl03,'Wider Neckline support reference',
           bands=[{'low':97.8,'high':99.4,'label':'support area'}],
           alt_text='Wider Neckline chart with one defensible support area around the two lower reactions.')
draw_chart('CL03-03-neckline-reference','CL03_wider_neckline',cl03,'Wider Neckline upper-area reference',
           bands=[{'low':101.8,'high':104.1,'label':'wider neckline area'}],
           alt_text='Wider Neckline chart with a broad upper reaction region marked as a zone rather than a thin line.')
draw_chart('CL03-04-combined-reference','CL03_wider_neckline',cl03,'Wider Neckline combined reference',
           bands=[{'low':97.8,'high':99.4,'label':'support area','x':1},{'low':101.8,'high':104.1,'label':'neckline / upper area','x':9}],
           alt_text='Wider Neckline chart with both support and the broader neckline area visible after the two zone submissions.')

# --- Lesson 15: conditional scenarios around zones ---
l15a_closes = [98.7,99.5,100.8,100.2,101.5,102.3,101.2,100.6,101.8,102.4,101.6,100.9]
l15a = bars_from_closes(l15a_closes,1501)
save_dataset('L15_A_between_two_areas',l15a)
draw_chart('L15-A-01-clean','L15_A_between_two_areas',l15a,'two-area context; answer hidden',
           alt_text='Illustrative chart with price between a lower reaction area and an upper reaction area; no trade entry or outcome is marked.')
draw_chart('L15-A-02-zones','L15_A_between_two_areas',l15a,'two-area context with zones revealed',
           bands=[{'low':98.0,'high':99.3,'label':'lower area'},{'low':102.4,'high':103.7,'label':'upper area'}],
           alt_text='Same chart with lower and upper contextual zones displayed; current price lies between them and the next decision remains conditional.')
draw_chart('L15-A-03-scenario-prompt','L15_A_between_two_areas',l15a,'conditional thinking prompt',
           bands=[{'low':98.0,'high':99.3,'label':'lower area'},{'low':102.4,'high':103.7,'label':'upper area'}],
           extra_text=[{'x':0.5,'y':105.0,'text':'What evidence would support either scenario? What would weaken it?','fontsize':8.5}],
           alt_text='Scenario prompt asks the learner to consider evidence for either path and to define what would weaken their interpretation; no entry is prescribed.')
l15b_closes = [104,102.8,101.5,100.3,99.4,100.2,101.1,100.6,99.8,100.9,101.8]
l15b = bars_from_closes(l15b_closes,1502,{4:(98.9,None)})
save_dataset('L15_B_independent_scenario_practice',l15b)
draw_chart('L15-B-01-practice','L15_B_independent_scenario_practice',l15b,'independent scenario practice; zones hidden',
           alt_text='Illustrative independent practice chart for writing conditional scenarios; students identify context and zones before seeing the reference.')
draw_chart('L15-B-02-reference','L15_B_independent_scenario_practice',l15b,'reference context after submission',
           bands=[{'low':98.9,'high':100.0,'label':'lower candidate area'},{'low':102.0,'high':103.2,'label':'upper candidate area'}],
           extra_text=[{'x':0.5,'y':105.5,'text':'State an alternative or justify waiting; zone location alone is not an entry trigger','fontsize':8.3}],
           alt_text='Reference context shows candidate lower and upper areas and reminds the learner to state an alternative or a justified waiting decision.')

# --- Lesson 18: unseen final assessment and a separate parallel retry chart ---
l18a_closes = [101,102.3,100.9,103.1,101.8,100.5,102.0,104.2,103.0,101.4,99.7,101.1,102.4,100.8,99.4,100.6,102.0,101.2,99.8,98.7,100.1,101.4,100.5,99.2,100.4,102.1,101.0,102.8,101.6,100.7]
l18a = bars_from_closes(l18a_closes,1801,{10:(98.9,None),14:(98.7,None),19:(98.1,None),23:(98.65,None),7:(None,104.8),25:(None,102.8)})
save_dataset('L18_A_final_unseen_assessment',l18a)
draw_chart('L18-A-01-unseen','L18_A_final_unseen_assessment',l18a,'final assessment initial chart; no annotations',
           alt_text='Unannotated illustrative assessment chart with meaningful turns, secondary fluctuations, and a mixed current sequence; no future outcome or reference zones are shown.')
draw_chart('L18-A-02-reference-internal','L18_A_final_unseen_assessment',l18a,'INTERNAL reference analysis; do not show before submission',
           bands=[{'low':98.5,'high':99.8,'label':'lower area'},{'low':102.5,'high':104.0,'label':'upper area'}],
           markers=[{'bar':8,'kind':'high','label':'candidate major high'},{'bar':20,'kind':'low','label':'candidate major low'},{'bar':26,'kind':'high','label':'later swing'}],
           extra_text=[{'x':12.2,'y':105.5,'text':'One defensible reading; transition/unclear is also acceptable with evidence','fontsize':8.4}],
           alt_text='Internal reference for the final assessment shows one defensible pair of zones and major turns, while explicitly allowing an evidenced transition or unclear interpretation.')
l18b_closes = [106,104.7,103.1,102.0,103.0,101.6,100.4,101.5,99.8,98.9,100.1,101.2,99.6,98.8,99.9,101.4,102.7,101.8,100.5,102.0,103.4,102.5,101.4,102.3,103.6]
l18b = bars_from_closes(l18b_closes,1802,{8:(98.3,None),13:(98.25,None),9:(None,100.5),20:(None,104.0)})
save_dataset('L18_B_parallel_retry',l18b)
draw_chart('L18-B-01-retry-unseen','L18_B_parallel_retry',l18b,'parallel retry chart; no annotations',
           alt_text='Different unannotated illustrative assessment chart with an earlier decline, a developing lower region and later recovery; it is distinct from the initial final-assessment chart.')
draw_chart('L18-B-02-retry-reference-internal','L18_B_parallel_retry',l18b,'INTERNAL parallel retry reference; do not show before retry',
           bands=[{'low':98.2,'high':99.5,'label':'lower area'},{'low':102.6,'high':104.0,'label':'upper area'}],
           markers=[{'bar':2,'kind':'high','label':'earlier high'},{'bar':10,'kind':'low','label':'candidate low'},{'bar':21,'kind':'high','label':'later high'}],
           extra_text=[{'x':12.2,'y':106.9,'text':'Parallel task: same rubric, fresh chart, no copied reference drawing','fontsize':8.4}],
           alt_text='Internal parallel retry reference with one defensible zone interpretation and a distinct swing selection; must remain hidden until retry submission.')

# Save registers.
with (ROOT / 'asset_manifest.csv').open('w', newline='', encoding='utf-8') as f:
    fields = ['asset_id','dataset_id','state','visible_bars','format','source_type','alt_text','notes']
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader(); writer.writerows(ASSETS)

with (ROOT / 'dataset_manifest.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['dataset_id','bars','csv_file','source_type','price_context'])
    writer.writeheader()
    for dataset_id, bars in DATASETS.items():
        writer.writerow({'dataset_id':dataset_id,'bars':len(bars),'csv_file':f'data/{dataset_id}.csv','source_type':'synthetic illustrative OHLC','price_context':'fictional numerical values; not historical prices'})

print(f'Generated {len(ASSETS)} chart states across {len(DATASETS)} synthetic OHLC datasets.')
