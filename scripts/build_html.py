#!/usr/bin/env python3
import json

def loadJSON(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

yuepiao  = loadJSON('data/latest/yuepiao.json')
hotsales = loadJSON('data/latest/hotsales.json')
recom    = loadJSON('data/latest/recom.json')
collect  = loadJSON('data/latest/collect.json')

def scoreRank(rank): return 21 - rank

scoreMap = {}
for src in [yuepiao, hotsales, recom]:
    for e in src['entries']:
        key = e['title'] + '|' + e['author']
        if key not in scoreMap:
            scoreMap[key] = {'title': e['title'], 'author': e['author'],
                             'category': e.get('category', ''), 'score': 0}
        scoreMap[key]['score'] += scoreRank(e['rank'])

top10 = sorted(scoreMap.values(), key=lambda x: -x['score'])[:10]

def makeRows(entries):
    return '\n'.join(
        "<div class='row'><div class='rank glow-num'>{:02d}</div><div class='book'><div class='title'>{title}</div><div class='meta'>{author} · {cat} · {status}</div></div></div>".format(
            e['rank'], title=e['title'], author=e['author'],
            cat=e.get('category',''), status=e.get('status',''))
        for e in entries
    )

def topRow(book, i):
    medal = ['🥇','🥈','🥉'][i] if i < 3 else str(i+1)
    bar   = int((book['score'] / top10[0]['score']) * 100)
    return ("<div class='top-row'>"
            "<div class='top-medal'>{medal}</div>"
            "<div class='top-info'>"
            "<div class='top-title'>{title}</div>"
            "<div class='top-meta'>{author} · {cat}</div>"
            "<div class='top-bar-bg'><div class='top-bar-fill' style='width:{bar}%'></div></div>"
            "</div>"
            "<div class='top-score'>{score}分</div>"
            "</div>").format(medal=medal, title=book['title'], author=book['author'],
                             cat=book['category'], bar=bar, score=book['score'])

analysis_rows = '\n'.join(topRow(b,i) for i,b in enumerate(top10))

CSS = """
    .layout { display:grid; grid-template-columns:210px 1fr 1fr; gap:18px; align-items:start; width:100%; max-width:min(1440px,60vw); margin:0 auto; }
    .side { display:flex; flex-direction:column; gap:16px; justify-content:flex-start; }
    .glass { background:var(--panel); backdrop-filter:blur(28px) saturate(1.05); border-radius:28px; border:1px solid rgba(255,255,255,.05); padding:16px; }
    .panel-head { display:flex; gap:12px; align-items:flex-start; margin-bottom:10px; flex-shrink:0; }
    .sword-line { width:3px; min-height:48px; border-radius:999px; background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(143,184,242,.85),rgba(255,255,255,.04)); box-shadow:0 0 10px rgba(143,184,242,.4); flex-shrink:0; }
    .panel-head h3 { margin:0; font-size:15px; font-weight:600; color:var(--text); }
    .panel-head p { margin:4px 0 0; color:var(--muted); font-size:11px; line-height:1.6; }
    .rows-scroll { flex:1; overflow-y:auto; min-height:0; max-height:490px; }
    .rows-scroll::-webkit-scrollbar { width:3px; }
    .rows-scroll::-webkit-scrollbar-thumb { background:rgba(143,184,242,0.3); border-radius:3px; }
    .rows-scroll::-webkit-scrollbar-track { background:transparent; }
    .row { display:grid; grid-template-columns:38px minmax(0,1fr); gap:12px; align-items:start; padding:9px 0; background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent); position:relative; }
    .row::after { content:''; position:absolute; left:0; right:0; bottom:0; height:1px; background:linear-gradient(90deg,transparent,rgba(143,184,242,.15),transparent); }
    .rank { font-size:16px; color:var(--gold); padding-top:1px; }
    .title { font-size:13px; color:var(--text); line-height:1.4; }
    .meta { margin-top:3px; color:var(--muted); font-size:11px; line-height:1.5; }
    .glow-num { text-shadow:0 0 8px rgba(143,184,242,.38),0 0 18px rgba(143,184,242,.2); }
    .theme-pill { display:inline-flex; align-items:center; gap:10px; margin-top:12px; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.07); color:var(--gold); font-size:12px; }
    .theme-pill i { width:8px; height:8px; border-radius:50%; background:radial-gradient(circle,rgba(255,255,255,.9),rgba(143,184,242,.3) 50%,transparent 70%); box-shadow:0 0 12px rgba(143,184,242,.8); animation:aura 2.6s ease-in-out infinite; }
    @keyframes aura { 0%,100%{transform:scale(.88); opacity:.65;} 50%{transform:scale(1.2); opacity:1;} }
    .tags { display:flex; flex-wrap:wrap; gap:7px; margin-top:10px; }
    .tags span { font-size:11px; color:var(--muted); padding:4px 9px; border-radius:999px; background:rgba(255,255,255,.05); }
    .analysis-list { margin:10px 0 0; padding-left:14px; color:var(--muted); line-height:1.9; font-size:12px; }
    .progress-panel { flex:0 0 auto; min-height:110px; }
    .progress-wrap { margin-top:10px; }
    .plabel { display:flex; justify-content:space-between; font-size:12px; color:var(--muted); }
    .plabel strong { color:var(--gold); font-size:15px; }
    .progress { margin-top:8px; height:7px; border-radius:999px; background:rgba(255,255,255,.09); overflow:hidden; }
    .bar { height:100%; border-radius:999px; background:linear-gradient(90deg,rgba(143,184,242,.4),rgba(190,220,255,.85)); }
    .pmeta { margin-top:6px; font-size:13px; color:var(--gold); font-weight:500; }
    .top-analysis-panel { flex:0 0 auto; }
    .top-list { display:flex; flex-direction:column; gap:6px; }
    .top-row { display:flex; align-items:center; gap:8px; padding:7px 0; border-bottom:1px solid rgba(143,184,242,0.07); }
    .top-row:last-child { border-bottom:none; }
    .top-medal { font-size:13px; width:22px; text-align:center; flex-shrink:0; }
    .top-info { flex:1; min-width:0; }
    .top-title { font-size:12px; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .top-meta { font-size:10px; color:var(--muted); margin-top:1px; }
    .top-bar-bg { margin-top:4px; height:3px; background:rgba(255,255,255,0.07); border-radius:999px; }
    .top-bar-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,rgba(143,184,242,.4),rgba(190,220,255,.85)); }
    .top-score { font-size:11px; color:var(--gold); flex-shrink:0; min-width:34px; text-align:right; }
    @media(max-width:1100px) { .layout{ grid-template-columns:1fr; } }
"""

# Build the full page
html = (
    "<!doctype html>\n"
    "<html lang='zh-CN'>\n"
    "<head>\n"
    "  <meta charset='utf-8' />\n"
    "  <meta name='viewport' content='width=device-width, initial-scale=1' />\n"
    "  <meta name='description' content='起点中文网榜单追踪 - 四榜实时数据，题材权重动态换肤' />\n"
    "  <title>起点榜单追踪 · 玄幻</title>\n"
    "  <style>\n"
    "    :root { --bg:#101019; --bg2:#1B1428; --panel:rgba(248,250,252,0.08); --text:#F8FAFC; --muted:#D8D2CA; --gold:#F0D8A7; }\n"
    "    *,*::before,*::after { box-sizing:border-box; }\n"
    "    html,body { margin:0; min-height:100vh; }\n"
    "    body { color:var(--text); font-family:\"PingFang SC\",\"Noto Serif SC\",\"STSong\",serif; background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%); overflow-x:hidden; }\n"
    "    .scene-bg { position:fixed; inset:0; z-index:0; opacity:.12; background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%); }\n"
    "    .scene-vignette { position:fixed; inset:0; z-index:1; background:radial-gradient(ellipse 80% 60% at 50% 38%,rgba(6,14,26,.18) 0%,rgba(6,14,26,.72) 100%); }\n"
    "    canvas#sword { position:fixed; inset:0; z-index:2; pointer-events:none; }\n"
    "    .shell { position:relative; z-index:3; min-height:100vh; padding:28px 18px 40px; }\n"
    + CSS +
    "  </style>\n"
    "</head>\n"
    "<body>\n"
    "  <div class='scene-bg'></div>\n"
    "  <div class='scene-vignette'></div>\n"
    "  <canvas id='sword'></canvas>\n"
    "  <main class='shell'>\n"
    "    <section class='layout'>\n"
    "\n"
    "      <!-- COL 1: Analysis + Theme -->\n"
    "      <div class='side left-col'>\n"
    "        <div class='glass top-analysis-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>🔥 综合热度</h3><p>月票·畅销·推荐三榜加权</p></div></div>\n"
    "          <div class='top-list'>" + analysis_rows + "</div>\n"
    "        </div>\n"
    "        <div class='glass theme-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>本周题材</h3><p>裂天遗迹 · 断崖幽冥，位面战场，黑暗旷野</p></div></div>\n"
    "          <div class='theme-pill'><i></i><span>玄幻</span></div>\n"
    "          <div class='tags'><span>玄幻 261.0</span><span>仙侠 193.4</span><span>都市 171.6</span><span>科幻 60.2</span><span>轻小说 39.0</span></div>\n"
    "          <ul class='analysis-list'>\n"
    "<li>榜首保持不变：玄鉴仙族。</li>\n"
    "<li>本轮没有新进榜作品。</li>\n"
    "<li>本轮没有掉榜作品。</li>\n"
    "</ul>\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      <!-- COL 2: 月票 + 推荐 -->\n"
    "      <div class='side'>\n"
    "        <div class='glass list-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>月票榜</h3><p>主榜热度与硬强度</p></div></div>\n"
    "          <div class='rows-scroll'>" + makeRows(yuepiao['entries']) + "</div>\n"
    "        </div>\n"
    "        <div class='glass list-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>推荐榜</h3><p>扩散速度与读者投票</p></div></div>\n"
    "          <div class='rows-scroll'>" + makeRows(recom['entries']) + "</div>\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      <!-- COL 3: 储能 + 畅销 + 收藏 -->\n"
    "      <div class='side'>\n"
    "        <div class='glass progress-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>剑匣储能</h3><p>灵力规模模拟</p></div></div>\n"
    "          <div class='progress-wrap'>\n"
    "            <div class='plabel'><span>储能</span><strong class='glow-num'>100%</strong></div>\n"
    "            <div class='progress'><div class='bar' style='width:100%'></div></div>\n"
    "            <div class='pmeta'>下次更新: 2026-04-18 18:00 MDT (埃德蒙顿)</div>\n"
    "          </div>\n"
    "        </div>\n"
    "        <div class='glass list-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>畅销榜</h3><p>付费意愿与消费热度</p></div></div>\n"
    "          <div class='rows-scroll'>" + makeRows(hotsales['entries']) + "</div>\n"
    "        </div>\n"
    "        <div class='glass list-panel'>\n"
    "          <div class='panel-head'><div class='sword-line'></div><div><h3>收藏榜</h3><p>长期积累与经典沉淀</p></div></div>\n"
    "          <div class='rows-scroll'>" + makeRows(collect['entries']) + "</div>\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "    </section>\n"
    "  </main>\n"
    "  <script>\n"
    "  (function(){\n"
    "    var canvas=document.getElementById('sword'),ctx=canvas.getContext('2d'),dpr=Math.min(devicePixelRatio,2);\n"
    "    function rs(){canvas.width=window.innerWidth*dpr;canvas.height=window.innerHeight*dpr;canvas.style.cssText='width:'+window.innerWidth+'px;height:'+window.innerHeight+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}\n"
    "    rs();window.addEventListener('resize',rs);\n"
    "    var mx=window.innerWidth/2,my=window.innerHeight/2,tx=mx,ty=my,angle=-Math.PI/2,trail=[],sparks=[],t=0;\n"
    "    window.addEventListener('mousemove',function(e){tx=e.clientX;ty=e.clientY;});\n"
    "    function update(){\n"
    "      mx+=(tx-mx)*0.1;my+=(ty-my)*0.1;\n"
    "      var dx=tx-mx,dy=ty-my;\n"
    "      if(Math.abs(dx)>0.5||Math.abs(dy)>0.5){var ta=Math.atan2(dy,dx);var diff=ta-angle;while(diff>Math.PI)diff-=Math.PI*2;while(diff<-Math.PI)diff+=Math.PI*2;angle+=diff*0.1;}\n"
    "      if(Math.random()<0.95){trail.push({x:mx,y:my,vx:-Math.cos(angle)*(1+Math.random()),vy:-Math.sin(angle)*(1+Math.random()),life:1.5,size:1.5+Math.random()*2});}\n"
    "      var speed=Math.sqrt((tx-mx)*(tx-mx)+(ty-my)*(ty-my));\n"
    "      if(speed>1.5&&Math.random()<0.8){sparks.push({x:mx,y:my,vx:(Math.random()-0.5)*14,vy:(Math.random()-0.5)*14,life:1.2,size:2+Math.random()*3});}\n"
    "      for(var i=trail.length-1;i>=0;i--){var p=trail[i];p.x+=p.vx;p.y+=p.vy;p.vx*=0.95;p.vy*=0.95;p.life-=0.018;if(p.life<=0)trail.splice(i,1);}\n"
    "      if(trail.length>150)trail=trail.slice(-150);\n"
    "      for(var i=sparks.length-1;i>=0;i--){var p=sparks[i];p.x+=p.vx;p.y+=p.vy;p.vx*=0.92;p.vy*=0.92;p.life-=0.025;if(p.life<=0)sparks.splice(i,1);}\n"
    "      if(sparks.length>80)sparks=sparks.slice(-80);t++;\n"
    "    }\n"
    "    function drawSword(x,y,ang){\n"
    "      ctx.save();ctx.translate(x,y);ctx.rotate(ang);\n"
    "      var grd=ctx.createRadialGradient(0,0,0,0,0,90);grd.addColorStop(0,'rgba(180,210,255,0.1)');grd.addColorStop(1,'rgba(180,210,255,0)');ctx.beginPath();ctx.arc(0,0,90,0,Math.PI*2);ctx.fillStyle=grd;ctx.fill();\n"
    "      ctx.shadowColor='rgba(200,220,255,0.6)';ctx.shadowBlur=16;\n"
    "      var tipX=75,shoulderW=3.5,guardX=-14;\n"
    "      ctx.beginPath();ctx.moveTo(tipX,0);ctx.lineTo(20,-shoulderW);ctx.lineTo(guardX,-3);ctx.lineTo(guardX,3);ctx.lineTo(20,shoulderW);ctx.closePath();\n"
    "      var bladeGrd=ctx.createLinearGradient(guardX,0,tipX,0);bladeGrd.addColorStop(0,'rgba(80,100,160,0.5)');bladeGrd.addColorStop(0.25,'rgba(160,200,255,0.85)');bladeGrd.addColorStop(0.6,'rgba(220,240,255,0.95)');bladeGrd.addColorStop(1,'rgba(255,255,255,1)');ctx.fillStyle=bladeGrd;ctx.fill();\n"
    "      ctx.shadowBlur=0;ctx.beginPath();ctx.moveTo(-12,0);ctx.lineTo(65,0);ctx.strokeStyle='rgba(255,255,255,0.75)';ctx.lineWidth=1;ctx.stroke();\n"
    "      ctx.beginPath();ctx.moveTo(8,-2.2);ctx.quadraticCurveTo(40,-1,62,0);ctx.strokeStyle='rgba(160,200,255,0.3)';ctx.lineWidth=0.7;ctx.stroke();\n"
    "      ctx.beginPath();ctx.moveTo(8,2.2);ctx.quadraticCurveTo(40,1,62,0);ctx.strokeStyle='rgba(160,200,255,0.3)';ctx.lineWidth=0.7;ctx.stroke();\n"
    "      ctx.beginPath();ctx.arc(-15,0,9,0,Math.PI*2);var gg=ctx.createRadialGradient(-15,0,1,-15,0,9);gg.addColorStop(0,'rgba(255,230,150,1)');gg.addColorStop(0.6,'rgba(210,170,80,0.95)');gg.addColorStop(1,'rgba(160,120,40,0.85)');ctx.fillStyle=gg;ctx.fill();ctx.strokeStyle='rgba(255,220,100,0.6)';ctx.lineWidth=1.5;ctx.stroke();\n"
    "      ctx.beginPath();ctx.moveTo(-22,0);ctx.lineTo(-8,0);ctx.strokeStyle='rgba(140,100,30,0.8)';ctx.lineWidth=2;ctx.stroke();\n"
    "      ctx.beginPath();ctx.arc(-15,0,3.5,0,Math.PI*2);ctx.strokeStyle='rgba(140,100,30,0.6)';ctx.lineWidth=1;ctx.stroke();\n"
    "      ctx.beginPath();ctx.moveTo(-15,-3.2);ctx.bezierCurveTo(-22,-3.2,-22,3.2,-15,3.2);ctx.lineTo(-15,-3.2);ctx.fillStyle='rgba(60,40,15,0.95)';ctx.fill();\n"
    "      for(var gi=0;gi<7;gi++){var px=-17-gi*2.5;ctx.beginPath();ctx.moveTo(px,-3.2);ctx.bezierCurveTo(px-0.5,0,px-0.5,0,px,3.2);ctx.strokeStyle='rgba(140,180,240,0.45)';ctx.lineWidth=1.5;ctx.stroke();}\n"
    "      ctx.beginPath();ctx.moveTo(-34,-2.5);ctx.bezierCurveTo(-40,-1.5,-40,1.5,-34,2.5);ctx.lineTo(-34,-2.5);ctx.fillStyle='rgba(50,30,10,0.9)';ctx.fill();\n"
    "      var tt=Date.now()*0.002;\n"
    "      ctx.beginPath();ctx.arc(-41,0,6,0,Math.PI*2);var pg=ctx.createRadialGradient(-41,0,0,-41,0,6);pg.addColorStop(0,'rgba(200,230,255,0.9)');pg.addColorStop(0.5,'rgba(140,190,255,0.7)');pg.addColorStop(1,'rgba(80,140,220,0.5)');ctx.fillStyle=pg;ctx.shadowColor='rgba(180,210,255,0.8)';ctx.shadowBlur=12;ctx.fill();ctx.strokeStyle='rgba(255,255,255,0.4)';ctx.lineWidth=1;ctx.stroke();\n"
    "      ctx.beginPath();ctx.arc(-41,0,2.5,0,Math.PI*2);ctx.fillStyle='rgba(60,40,15,0.8)';ctx.shadowBlur=0;ctx.fill();\n"
    "      for(var ti=0;ti<3;ti++){var tx=-41,ty=0,phase=ti*0.8+tt;ctx.beginPath();ctx.moveTo(tx,ty+(ti-1)*2);ctx.quadraticCurveTo(tx-8,ty+(ti-1)*2+Math.sin(phase)*4,tx-15,ty+(ti-1)*2+Math.sin(phase)*6+5);ctx.strokeStyle='rgba(160,200,255,0.65)';ctx.lineWidth=1;ctx.stroke();}\n"
    "      ctx.restore();\n"
    "    }\n"
    "    function render(){\n"
    "      ctx.clearRect(0,0,canvas.width,canvas.height);\n"
    "      for(var i=0;i<trail.length;i++){var p=trail[i];ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fillStyle='rgba(180,210,255,'+(p.life*0.5)+')';ctx.shadowColor='rgba(180,210,255,0.5)';ctx.shadowBlur=6;ctx.fill();}\n"
    "      ctx.shadowBlur=0;\n"
    "      for(var i=0;i<sparks.length;i++){var p=sparks[i];ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fillStyle='rgba(180,220,255,'+(p.life*0.8)+')';ctx.shadowColor='rgba(180,220,255,0.6)';ctx.shadowBlur=8;ctx.fill();}\n"
    "      ctx.shadowBlur=0;drawSword(mx,my,angle);\n"
    "    }\n"
    "    function loop(){update();render();requestAnimationFrame(loop);}\n"
    "    loop();\n"
    "  })();\n"
    "  </script>\n"
    "</body>\n"
    "</html>"
)

with open('data/site/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Written', len(html), 'bytes')
print('Top 10:')
for i, b in enumerate(top10):
    print(f'  {i+1}. {b["title"]} ({b["score"]}pts)')