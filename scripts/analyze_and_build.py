#!/usr/bin/env python3
"""Analyze ranking snapshots and produce change reports + site HTML."""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data"))

RANKING_WEIGHTS = {"yuepiao": 1.0, "hotsales": 1.0, "recom": 0.8, "collect": 0.8}

THEMES = {
    "仙侠": {
        "label": "仙侠", "bg": "#07111E", "bg2": "#0E1C31", "panel": "rgba(248,250,252,0.10)",
        "text": "#F8FAFC", "muted": "#B8C7DA", "accent": "#8FB8F2", "gold": "#D9E7FF",
        "description": "冷月灵脉 · 深邃星空蓝底，云海远山，仙门双峰对峙",
    },
    "玄幻": {
        "label": "玄幻", "bg": "#101019", "bg2": "#1B1428", "panel": "rgba(248,250,252,0.08)",
        "text": "#F8FAFC", "muted": "#D8D2CA", "accent": "#D6B07A", "gold": "#F0D8A7",
        "description": "裂天遗迹 · 断崖幽冥，位面压迫，黑暗旷野",
    },
}

RANKINGS = ["yuepiao", "hotsales", "recom", "collect"]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))


def compare_snapshots(current: dict, previous: dict | None) -> tuple[dict, list[str]]:
    curr_entries = current.get("entries", [])
    prev_entries = previous.get("entries", []) if previous else []
    curr_idx = {e["title"]: e for e in curr_entries}
    prev_idx = {e["title"]: e for e in prev_entries}

    new_entries, dropped, moved_up, moved_down = [], [], [], []
    for title, entry in curr_idx.items():
        if title not in prev_idx:
            new_entries.append({"title": title, "rank": entry["rank"]})
        else:
            delta = prev_idx[title]["rank"] - entry["rank"]
            if delta > 0: moved_up.append({"title": title, "old_rank": prev_idx[title]["rank"], "new_rank": entry["rank"], "delta": delta})
            elif delta < 0: moved_down.append({"title": title, "old_rank": prev_idx[title]["rank"], "new_rank": entry["rank"], "delta": delta})

    for title, entry in prev_idx.items():
        if title not in curr_idx:
            dropped.append({"title": title, "rank": entry["rank"]})

    moved_up.sort(key=lambda x: -x["delta"])
    moved_down.sort(key=lambda x: x["delta"])
    new_entries.sort(key=lambda x: x["rank"])
    dropped.sort(key=lambda x: x["rank"])

    summary = {"top_1": curr_entries[0]["title"] if curr_entries else None, "entry_count": len(curr_entries),
               "new_entries": new_entries, "dropped_entries": dropped, "moved_up": moved_up, "moved_down": moved_down}

    analysis: list[str] = []
    if not previous:
        analysis.append("首份快照，暂无历史数据比对。")
        return summary, analysis

    if curr_entries and prev_entries and curr_entries[0]["title"] != prev_entries[0]["title"]:
        analysis.append(f"榜首变化：{prev_entries[0]['title']} → {curr_entries[0]['title']}。")
    else:
        analysis.append(f"榜首保持：{summary['top_1']}。")

    if new_entries:
        names = "，".join(f"{e['title']}(#{e['rank']})" for e in new_entries[:5])
        analysis.append(f"新进榜：{names}。")
    else:
        analysis.append("本轮无新进榜作品。")

    if dropped:
        names = "，".join(f"{e['title']}(原#{e['rank']})" for e in dropped[:5])
        analysis.append(f"掉榜：{names}。")
    else:
        analysis.append("本轮无掉榜作品。")

    if moved_up:
        b = moved_up[0]
        analysis.append(f"涨幅最大：{b['title']} {b['old_rank']}→{b['new_rank']}（+{b['delta']}名）。")
    else:
        analysis.append("本轮无明显上升作品。")

    if moved_down:
        w = moved_down[0]
        analysis.append(f"跌幅最大：{w['title']} {w['old_rank']}→{w['new_rank']}（-{abs(w['delta'])}名）。")
    else:
        analysis.append("本轮无明显下降作品。")

    return summary, analysis


def compute_theme(data_dir: Path) -> tuple[str, dict, dict]:
    scores: dict[str, float] = defaultdict(float)
    for key in RANKINGS:
        latest = _load_json(data_dir / "latest" / f"{key}.json")
        for entry in latest.get("entries", [])[:20]:
            cat = entry.get("category") or "玄幻"
            rank = entry.get("rank", 20)
            scores[cat] += RANKING_WEIGHTS.get(key, 1.0) * max(1, 21 - rank)
    dominant = max(scores.items(), key=lambda x: x[1])[0] if scores else "玄幻"
    override_path = data_dir / "theme-override.txt"
    if override_path.exists():
        ov = override_path.read_text(encoding="utf-8").strip()
        if ov in THEMES: dominant = ov
    return dominant, THEMES.get(dominant, THEMES["玄幻"]), dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def _glass(title: str, sub: str, content: str, cls: str = "") -> str:
    return f"<div class='glass {cls}'><div class='panel-head'><div class='sword-line'></div><div><h3>{escape(title)}</h3><p>{escape(sub)}</p></div></div>{content}</div>"


def table_rows(entries: list[dict]) -> str:
    parts = []
    for e in entries[:8]:
        parts.append(f"<div class='row'><div class='rank glow-num'>{e.get('rank',0):02d}</div>"
                     f"<div class='book'><div class='title'>{escape(e.get('title',''))}</div>"
                     f"<div class='meta'>{escape(e.get('author',''))} · {escape(e.get('category',''))} · {escape(e.get('status',''))}</div></div>"
                     f"<div class='metric'>{escape(e.get('metric',''))}</div></div>")
    return "".join(parts) if parts else "<div class='empty'>暂无数据</div>"


def build_html(data_dir: Path) -> Path:
    dominant_key, theme, scores = compute_theme(data_dir)
    rank_data = {k: _load_json(data_dir / "latest" / f"{k}.json") for k in RANKINGS}
    analysis_data = {}
    for k in RANKINGS:
        p = data_dir / "analysis" / k / "latest.json"
        analysis_data[k] = _load_json(p)

    scores_tags = "".join(f"<span>{k} {v:.1f}</span>" for k, v in list(scores.items())[:5])
    bg, bg2, panel, text, muted, accent, gold = theme["bg"], theme["bg2"], theme["panel"], theme["text"], theme["muted"], theme["accent"], theme["gold"]

    total_entries = sum(len(rank_data[k].get("entries", [])) for k in RANKINGS)
    progress = min(100, 28 + total_entries)
    latest_top = [rank_data[k].get("entries", [{}])[0].get("title", "-") for k in RANKINGS]
    core_index = int(sum(v for _, v in list(scores.items())[:3])) if scores else 0
    update_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def al(bullets: list[str]) -> str:
        return "".join(f"<li>{escape(b)}</li>" for b in (bullets if bullets else ["暂无分析"]))

    left = (
        _glass("本周题材", theme["description"],
            f"<div class='theme-pill'><i></i><span>{escape(theme['label'])}</span></div>"
            f"<div class='tags'>{scores_tags}</div>"
            f"<ul class='analysis-list'>{al(analysis_data['yuepiao'].get('analysis', []))}</ul>",
            "theme-panel")
        + _glass("月票榜", "主榜热度与硬强度", table_rows(rank_data["yuepiao"].get("entries", [])), "tall-panel")
        + _glass("推荐榜", "扩散速度与读者投票", table_rows(rank_data["recom"].get("entries", [])), "")
    )
    right = (
        _glass("剑匣储能", "灵力规模模拟",
            f"<div class='progress-wrap'><div class='plabel'><span>储能</span><strong class='glow-num'>{progress}%</strong></div>"
            f"<div class='progress'><div class='bar' style='width:{progress}%'></div></div>"
            f"<div class='pmeta'>抓取 {total_entries} 条 · {escape(update_time)}</div></div>",
            "progress-panel")
        + _glass("畅销榜", "付费意愿与消费热度", table_rows(rank_data["hotsales"].get("entries", [])), "tall-panel")
        + _glass("收藏榜", "长期积累与经典沉淀", table_rows(rank_data["collect"].get("entries", [])), "")
    )
    center = f"""
    <section class='center-stage'>
      <div class='hero-copy'>
        <div class='overline'>起点榜单追踪</div>
        <h1>{' '.join(theme['label'])} 主 题 演 绎</h1>
        <p>同一页按题材气质自动换肤。当前为<span class='accent'>{escape(theme['label'])}</span>版：{escape(theme['description'])}</p>
      </div>
      <div class='core-metrics'>
        <div class='stone'><span>周权重</span><strong class='glow-num'>{core_index}</strong></div>
        <div class='stone'><span>核心指数</span><strong class='glow-num'>{len(set(t for t in latest_top if t != '-'))}</strong></div>
      </div>
    </section>"""

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <meta name='description' content='起点中文网榜单追踪 - 四榜实时数据，题材权重动态换肤' />
  <title>起点榜单追踪 · {escape(theme['label'])}</title>
  <style>
    :root {{ --bg:{bg}; --bg2:{bg2}; --panel:{panel}; --text:{text}; --muted:{muted}; --accent:{accent}; --gold:{gold}; }}
    *,*::before,*::after {{ box-sizing:border-box; }}
    html,body {{ margin:0; min-height:100vh; }}
    body {{ color:var(--text); font-family:"PingFang SC","Noto Serif SC","STSong",serif; background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%); overflow-x:hidden; }}
    /* ── Layer 1: Deep nebula base ── */
    .scene-bg {{ position:fixed; inset:0; z-index:0; overflow:hidden; }}
    .scene-bg::before {{ content:''; position:absolute; inset:-20%; background:
      radial-gradient(ellipse 90% 70% at 20% 15%, rgba(60,30,100,.55) 0%, transparent 65%),
      radial-gradient(ellipse 80% 60% at 78% 82%, rgba(15,45,90,.60) 0%, transparent 60%),
      radial-gradient(ellipse 60% 80% at 55% 35%, rgba(35,15,70,.35) 0%, transparent 70%),
      radial-gradient(ellipse 50% 40% at 88% 12%, rgba(80,40,120,.30) 0%, transparent 55%),
      radial-gradient(ellipse 70% 50% at 12% 72%, rgba(10,30,80,.45) 0%, transparent 60%),
      radial-gradient(ellipse 40% 60% at 40% 90%, rgba(50,20,90,.25) 0%, transparent 55%),
      linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%); }}
    /* ── Layer 2: Flowing mist / ink-wash noise (animated) ── */
    .scene-mist {{ position:fixed; inset:0; z-index:1;
      opacity:.07; animation:mist-drift 28s ease-in-out infinite alternate; pointer-events:none;
      background:transparent; }}
    @keyframes mist-drift {{
      0%   {{ transform:translate(-4%,-3%) rotate(.5deg) scale(1.05); }}
      33%  {{ transform:translate(3%,-5%) rotate(-.3deg) scale(1.08); }}
      66%  {{ transform:translate(-2%,4%) rotate(.8deg) scale(1.06); }}
      100% {{ transform:translate(4%,2%) rotate(-.5deg) scale(1.09); }}
    }}
    /* ── Layer 3: Vignette ── */
    .scene-vignette {{ position:fixed; inset:0; z-index:2; pointer-events:none;
      background:radial-gradient(ellipse 80% 65% at 50% 38%,rgba(6,14,26,.08) 0%,rgba(6,14,26,.75) 100%); }}
    canvas#qi {{ position:fixed; inset:0; z-index:3; pointer-events:none; }}
    .shell {{ position:relative; z-index:4; min-height:100vh; padding:28px 18px 40px; }}
    .layout {{ display:grid; grid-template-columns:300px minmax(0,1fr) 300px; gap:40px; align-items:start; max-width:1440px; margin:0 auto; }}
    .side {{ display:flex; flex-direction:column; gap:16px; }}
    .center-stage {{ min-height:calc(100vh - 56px); display:flex; flex-direction:column; justify-content:space-between; padding:18px 0 10px; }}
    .overline {{ color:var(--gold); letter-spacing:.22em; font-size:11px; text-transform:uppercase; margin-bottom:14px; opacity:.8; }}
    h1 {{ margin:0 0 16px; font-size:clamp(26px,3.8vw,42px); font-weight:500; letter-spacing:.5rem; line-height:1.2; background:linear-gradient(180deg,#F8FAFC 0%,#C5D8FF 55%,#F8FAFC 100%); -webkit-background-clip:text; background-clip:text; color:transparent; text-shadow:0 0 18px rgba(180,210,255,.28); }}
    .hero-copy p {{ margin:0; font-size:14px; line-height:1.95; color:var(--muted); max-width:36ch; }}
    .accent {{ color:var(--gold); font-style:normal; }}
    .core-metrics {{ display:flex; gap:16px; flex-wrap:wrap; }}
    .stone {{ flex:1; min-width:160px; text-align:center; padding:20px 16px; background:var(--panel); backdrop-filter:blur(28px); border-radius:24px; border:1px solid rgba(255,255,255,.05); }}
    .stone span {{ display:block; font-size:11px; letter-spacing:.2em; color:var(--muted); text-transform:uppercase; }}
    .stone strong {{ display:block; margin-top:8px; font-size:36px; color:var(--gold); font-weight:600; }}
    .glass {{ background:var(--panel); backdrop-filter:blur(28px) saturate(1.05); border-radius:28px; border:1px solid rgba(255,255,255,.05); padding:18px; }}
    .panel-head {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:12px; }}
    .sword-line {{ width:3px; min-height:48px; border-radius:999px; background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(143,184,242,.85),rgba(255,255,255,.04)); box-shadow:0 0 10px rgba(143,184,242,.4); flex-shrink:0; }}
    .panel-head h3 {{ margin:0; font-size:17px; font-weight:600; color:var(--text); }}
    .panel-head p {{ margin:5px 0 0; color:var(--muted); font-size:12px; line-height:1.7; }}
    .theme-pill {{ display:inline-flex; align-items:center; gap:10px; margin-top:14px; padding:9px 14px; border-radius:999px; background:rgba(255,255,255,.07); color:var(--gold); font-size:13px; }}
    .theme-pill i {{ width:9px; height:9px; border-radius:50%; background:radial-gradient(circle,rgba(255,255,255,.9),rgba(143,184,242,.3) 50%,transparent 70%); box-shadow:0 0 12px rgba(143,184,242,.8); animation:aura 2.6s ease-in-out infinite; }}
    @keyframes aura {{ 0%,100%{{transform:scale(.88); opacity:.65;}} 50%{{transform:scale(1.2); opacity:1;}} }}
    .tags {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
    .tags span {{ font-size:11px; color:var(--muted); padding:5px 10px; border-radius:999px; background:rgba(255,255,255,.05); }}
    .analysis-list {{ margin:12px 0 0; padding-left:16px; color:var(--muted); line-height:1.9; font-size:13px; }}
    .row {{ display:grid; grid-template-columns:38px minmax(0,1fr) 110px; gap:12px; align-items:start; padding:16px 0; background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent); position:relative; }}
    .row::after {{ content:''; position:absolute; left:0; right:0; bottom:0; height:1px; background:linear-gradient(90deg,transparent,rgba(143,184,242,.15),transparent); }}
    .rank {{ font-size:17px; color:var(--gold); padding-top:1px; }}
    .title {{ font-size:14px; color:var(--text); line-height:1.4; }}
    .meta {{ margin-top:5px; color:var(--muted); font-size:11px; line-height:1.7; }}
    .metric {{ justify-self:end; color:var(--muted); font-size:11px; text-align:right; max-width:110px; }}
    .glow-num {{ text-shadow:0 0 8px rgba(143,184,242,.38),0 0 18px rgba(143,184,242,.2); }}
    .empty {{ padding:14px 0 6px; color:var(--muted); font-size:13px; }}
    .progress-wrap {{ margin-top:12px; }}
    .plabel {{ display:flex; justify-content:space-between; font-size:12px; color:var(--muted); }}
    .plabel strong {{ color:var(--gold); font-size:16px; }}
    .progress {{ margin-top:10px; height:8px; border-radius:999px; background:rgba(255,255,255,.09); overflow:hidden; }}
    .bar {{ height:100%; border-radius:999px; background:linear-gradient(90deg,rgba(143,184,242,.4),rgba(190,220,255,.85)); }}
    .pmeta {{ margin-top:8px; font-size:11px; color:var(--muted); }}
    .tall-panel {{ min-height:520px; }}
    @media(max-width:1140px){{ .layout{{ grid-template-columns:1fr; gap:24px; }} .center-stage{{ min-height:auto; gap:18px; }} .core-metrics{{ justify-content:flex-start; }} }}
  </style>
</head>
<body>
  <div class='scene-bg'></div>
  <!-- SVG turbulence: creates organic ink-wash / nebula mist texture -->
  <svg class='scene-mist' viewBox='0 0 800 600' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>
    <filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.012 0.008' numOctaves='5' seed='7' stitchTiles='stitch' result='noise'/><feColorMatrix type='saturate' values='0' in='noise'/><feComponentTransfer in='noise'><feFuncR type='linear' slope='1.2' intercept='-0.05'/><feFuncG type='linear' slope='1.1' intercept='-0.02'/><feFuncB type='linear' slope='1.4' intercept='0.0'/></feComponentTransfer><feComposite operator='in' in2='SourceGraphic'/></filter>
    <filter id='n2'><feTurbulence type='fractalNoise' baseFrequency='0.022 0.016' numOctaves='4' seed='19' stitchTiles='stitch' result='noise'/><feColorMatrix type='saturate' values='0' in='noise'/><feComponentTransfer in='noise'><feFuncR type='linear' slope='0.9' intercept='0'/><feFuncG type='linear' slope='0.85' intercept='0'/><feFuncB type='linear' slope='1.2' intercept='0'/></feComponentTransfer><feComposite operator='in' in2='SourceGraphic'/></filter>
    <rect width='800' height='600' filter='url(#n)' opacity='0.85'/>
    <rect width='800' height='600' filter='url(#n2)' opacity='0.6' transform='translate(60,40)'/>
  </svg>
  <div class='scene-vignette'></div>
  <canvas id='qi'></canvas>
  <main class='shell'>
    <section class='layout'>
      <aside class='side left'>{left}</aside>
      {center}
      <aside class='side right'>{right}</aside>
    </section>
  </main>
  <script>
    let mx=0,my=0;
    document.documentElement.style.setProperty('--mx','0px');
    document.documentElement.style.setProperty('--my','0px');
    window.addEventListener('mousemove',e=>{{
      const rx=(e.clientX/window.innerWidth-.5)*12;
      const ry=(e.clientY/window.innerHeight-.5)*8;
      document.documentElement.style.setProperty('--mx',rx+'px');
      document.documentElement.style.setProperty('--my',ry+'px');
      const bg=document.querySelector('.scene-bg');
      if(bg) bg.style.transform="translate3d("+rx+"px,"+ry+"px,0) scale(1.02)";
    }});
    const canvas=document.getElementById('qi'),ctx=canvas.getContext('2d');
    let pts=[];
    function resize(){{
      const dpr=Math.min(devicePixelRatio,2);
      canvas.width=window.innerWidth*dpr; canvas.height=window.innerHeight*dpr;
      canvas.style.width=window.innerWidth+'px'; canvas.style.height=window.innerHeight+'px';
      ctx.setTransform(dpr,0,0,dpr,0,0);
    }}
    function spawn(x,y){{for(var i=0;i<5;i++)pts.push({{x:x,y:y,tx:x+(Math.random()-.5)*60,ty:y+(Math.random()-.5)*60,life:35+Math.random()*20,r:1+Math.random()*2}});if(pts.length>120)pts=pts.slice(-120);}}
    window.addEventListener('mousemove',e=>{{spawn(e.clientX,e.clientY);}});
    def tick(){{
      ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
      pts.forEach(function(p){{p.x+=(p.tx-p.x)*.028;p.y+=(p.ty-p.y)*.028;p.life-=.8;ctx.fillStyle='rgba(180,210,255,'+(Math.max(0,p.life/55))+')';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}});
      pts=pts.filter(function(p){{return p.life>0;}});
      requestAnimationFrame(tick);
    }}
    resize();tick();window.addEventListener('resize',resize);
  </script>
</body>
</html>"""

    out = data_dir / "site" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def run_analysis() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "analysis").mkdir(parents=True, exist_ok=True)
    reports = []
    for key in RANKINGS:
        snap_dir = OUTPUT_DIR / "snapshots" / key
        if not snap_dir.exists(): continue
        day_dirs = sorted([d for d in snap_dir.iterdir() if d.is_dir()], reverse=True)
        if not day_dirs: continue
        snap_files = sorted(day_dirs[0].glob("*.json"), reverse=True)
        if not snap_files: continue
        current = json.loads(snap_files[0].read_text(encoding="utf-8"))
        prev_file = None
        if len(day_dirs) > 1:
            prev_snaps = sorted(day_dirs[1].glob("*.json"), reverse=True)
            if prev_snaps: prev_file = prev_snaps[0]
        previous = json.loads(prev_file.read_text(encoding="utf-8")) if prev_file else None
        summary, analysis = compare_snapshots(current, previous)
        report = {"ranking_key": key, "generated_at": datetime.now(timezone.utc).isoformat(), "summary": summary, "analysis": analysis}
        rd = OUTPUT_DIR / "analysis" / key
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "latest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        reports.append(report)
    return reports


if __name__ == "__main__":
    reports = run_analysis()
    site_path = build_html(OUTPUT_DIR)
    print(f"Analysis: {len(reports)} reports, Site: {site_path}")