#!/usr/bin/env node
const fs = require('fs');

function loadJSON(path) {
  return JSON.parse(fs.readFileSync(path, 'utf-8'));
}

const yuepiao  = loadJSON('data/latest/yuepiao.json');
const hotsales = loadJSON('data/latest/hotsales.json');
const recom    = loadJSON('data/latest/recom.json');
const collect  = loadJSON('data/latest/collect.json');
const reviews  = loadJSON('data/site/reviews.json');

function scoreRank(rank) { return 21 - rank; }

const scoreMap = {};
for (const src of [yuepiao, hotsales, recom]) {
  for (const e of src.entries) {
    const key = e.title + '|' + e.author;
    if (!scoreMap[key]) {
      scoreMap[key] = { title: e.title, author: e.author, category: e.category || '未知', score: 0, sources: [] };
    }
    scoreMap[key].score += scoreRank(e.rank);
  }
}

const top10 = Object.values(scoreMap).sort((a, b) => b.score - a.score).slice(0, 10);

function makeRows(entries) {
  return entries.map(e =>
    "<div class='row'><div class='rank glow-num'>" + String(e.rank).padStart(2,'0') + "</div><div class='book'><div class='title'>" + e.title + "</div><div class='meta'>" + e.author + " · " + (e.category||'') + " · " + (e.status||'') + "</div></div></div>"
  ).join('\n');
}

function topRow(book, i) {
  const medals = ['🥇','🥈','🥉'];
  const medal = i < 3 ? medals[i] : String(i + 1);
  const bar = Math.round((book.score / top10[0].score) * 100);
  const rank = top10.indexOf(book) + 1;
  return "<div class='top-row' onclick=\"showBookModal('" + book.title.replace(/'/g,"\\'") + "')\">" +
    "<div class='top-medal'>" + medal + "</div>" +
    "<div class='top-info'>" +
    "<div class='top-title'>" + book.title + "</div>" +
    "<div class='top-meta'>" + book.author + " · " + book.category + "</div>" +
    "<div class='top-bar-bg'><div class='top-bar-fill' style='width:" + bar + "%'></div></div>" +
    "</div>" +
    "<div class='top-score'>" + book.score + "分</div>" +
    "</div>";
}

const analysis_rows = top10.map((b, i) => topRow(b, i)).join('\n');

const reviewItems = Object.entries(reviews).slice(0, 15).map(([title, item]) => {
  const snippet = (item.snippets && item.snippets[0]) ? item.snippets[0] : '';
  return `<div class='review-item' onclick="showBookModal('${title.replace(/'/g, "\\'")}')" style='cursor:pointer'><div class='review-book'>📖 ${title}</div><div class='review-snippet'>${snippet}</div></div>`;
}).join('\n');

const bookDataJS = JSON.stringify({
  '玄鉴仙族': { bid: '1035420986', score: top10[0] ? top10[0].score + '分' : '59分', summary: '陆江仙残魂附于青灰色铜镜，飘落修仙世界。小家族拾镜，传仙道授仙法，开启波澜壮阔的新时代。' },
  '夜无疆': { bid: '1040765595', score: top10[1] ? top10[1].score + '分' : '57分', summary: '辰东东方玄幻新作。那一天太阳落下再也没有升起……' },
  '捞尸人': { bid: '1041637443', score: top10[2] ? top10[2].score + '分' : '55分', summary: '长江捞尸人：捞尸价3.6万，曾一月捞上百人。悬疑灵异题材，紧张刺激。' }
}, null, 0).replace(/\n/g, '');

const CSS = `.layout{display:grid;grid-template-columns:500px 1fr 1fr 1.3fr;gap:18px;align-items:start;width:100%;max-width:min(2100px,96vw);margin:0 auto}.side{display:flex;flex-direction:column;gap:16px;justify-content:flex-start}.glass{background:var(--panel);backdrop-filter:blur(28px) saturate(1.05);border-radius:28px;border:1px solid rgba(255,255,255,.05);padding:16px}.panel-head{display:flex;gap:12px;align-items:flex-start;margin-bottom:10px;flex-shrink:0}.sword-line{width:3px;min-height:48px;border-radius:999px;background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(143,184,242,.85),rgba(255,255,255,.04));box-shadow:0 0 10px rgba(143,184,242,.4);flex-shrink:0}.panel-head h3{margin:0;font-size:15px;font-weight:600;color:var(--text)}.panel-head p{margin:4px 0 0;color:var(--muted);font-size:11px;line-height:1.6}.rows-scroll{flex:1;overflow-y:auto;min-height:0;max-height:490px}.rows-scroll::-webkit-scrollbar{width:3px}.rows-scroll::-webkit-scrollbar-thumb{background:rgba(143,184,242,0.3);border-radius:3px}.rows-scroll::-webkit-scrollbar-track{background:transparent}.row{display:grid;grid-template-columns:38px minmax(0,1fr);gap:12px;align-items:start;padding:9px 0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);position:relative}.row::after{content:'';position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,transparent,rgba(143,184,242,.15),transparent)}.rank{font-size:16px;color:var(--gold);padding-top:1px}.title{font-size:13px;color:var(--text);line-height:1.4}.meta{margin-top:3px;color:var(--muted);font-size:11px;line-height:1.5}.glow-num{text-shadow:0 0 8px rgba(143,184,242,.38),0 0 18px rgba(143,184,242,.2)}.theme-pill{display:inline-flex;align-items:center;gap:10px;margin-top:12px;padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.07);color:var(--gold);font-size:12px}.theme-pill i{width:8px;height:8px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.9),rgba(143,184,242,.3) 50%,transparent 70%);box-shadow:0 0 12px rgba(143,184,242,.8);animation:aura 2.6s ease-in-out infinite}@keyframes aura{0%,100%{transform:scale(.88);opacity:.65}50%{transform:scale(1.2);opacity:1}}.tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}.tags span{font-size:11px;color:var(--muted);padding:4px 9px;border-radius:999px;background:rgba(255,255,255,.05)}.analysis-list{margin:10px 0 0;padding-left:14px;color:var(--muted);line-height:1.9;font-size:12px}.progress-panel{flex:0 0 auto;min-height:110px}.progress-wrap{margin-top:10px}.plabel{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}.plabel strong{color:var(--gold);font-size:15px}.progress{margin-top:8px;height:7px;border-radius:999px;background:rgba(255,255,255,.09);overflow:hidden}.bar{height:100%;border-radius:999px;background:linear-gradient(90deg,rgba(143,184,242,.4),rgba(190,220,255,.85))}.pmeta{margin-top:6px;font-size:13px;color:var(--gold);font-weight:500}.top-analysis-panel{flex:0 0 auto}.top-list{display:flex;flex-direction:column;gap:6px}.top-row{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid rgba(143,184,242,0.07);cursor:pointer}.top-row:hover{background:rgba(255,255,255,0.03);border-radius:8px}.top-row:last-child{border-bottom:none}.top-medal{font-size:13px;width:22px;text-align:center;flex-shrink:0}.top-info{flex:1;min-width:0}.top-title{font-size:12px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.top-meta{font-size:10px;color:var(--muted);margin-top:1px}.top-bar-bg{margin-top:4px;height:3px;background:rgba(255,255,255,0.07);border-radius:999px}.top-bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,rgba(143,184,242,.4),rgba(190,220,255,.85))}.top-score{font-size:11px;color:var(--gold);flex-shrink:0;min-width:34px;text-align:right}.reviews-panel{flex:1 1 auto;min-height:200px}.reviews-list{display:flex;flex-direction:column;gap:10px;margin-top:4px;overflow-y:auto;max-height:520px}.review-item{padding-bottom:10px;border-bottom:1px solid rgba(180,210,255,.07)}.review-item:last-child{border-bottom:none}.review-book{font-size:13px;color:var(--gold);font-weight:600;margin-bottom:3px}.review-snippet{font-size:14px;color:var(--text);line-height:1.8}.review-src{font-size:10px;color:var(--muted);margin-top:2px}.review-loading{font-size:12px;color:var(--muted);padding:16px 0;text-align:center}@media(max-width:1100px){.layout{grid-template-columns:1fr}}`;

const MODAL_HTML = "<div id='book-modal' style='display:none;position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.75);backdrop-filter:blur(8px);align-items:center;justify-content:center;' onclick='if(event.target===this)closeBookModal()'>" +
  "<div style='background:var(--bg2);border:1px solid rgba(255,255,255,0.1);border-radius:24px;padding:32px;max-width:420px;width:90%;position:relative;'>" +
  "<button onclick='closeBookModal()' style='position:absolute;top:16px;right:16px;background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;'>✕</button>" +
  "<div id='m-title' style='font-size:20px;font-weight:700;color:var(--gold);margin-bottom:8px;'></div>" +
  "<div id='m-author' style='font-size:13px;color:var(--muted);margin-bottom:4px;'></div>" +
  "<div id='m-genre' style='font-size:12px;color:var(--muted);margin-bottom:12px;'></div>" +
  "<div id='m-score' style='font-size:28px;font-weight:700;color:var(--text);margin-bottom:16px;'></div>" +
  "<div id='m-summary' style='font-size:13px;color:var(--text);line-height:1.7;'></div>" +
  "<a id='m-link' href='#' target='_blank' style='display:inline-block;margin-top:16px;padding:10px 20px;background:rgba(143,184,242,0.15);color:var(--gold);border-radius:12px;text-decoration:none;font-size:13px;'>在起点阅读 →</a>" +
  "</div></div>";

const BOOK_DATA_SCRIPT = "<script>var bookData=" + bookDataJS + ";" +
  "function showBookModal(title){var b=bookData[title];if(!b)return;" +
  "document.getElementById('m-title').textContent=title;" +
  "document.getElementById('m-author').textContent=b.author||'';" +
  "document.getElementById('m-genre').textContent=b.category||'';" +
  "document.getElementById('m-score').textContent=b.score||'';" +
  "document.getElementById('m-summary').textContent=b.summary||'';" +
  "document.getElementById('m-link').href='https://www.qidian.com/book/'+(b.bid||'');" +
  "document.getElementById('book-modal').style.display='flex';" +
  "document.body.style.overflow='hidden';}" +
  "function closeBookModal(){document.getElementById('book-modal').style.display='none';document.body.style.overflow='';}" +
  "document.addEventListener('keydown',function(e){if(e.key==='+\"'\\\"'\"+')closeBookModal();});</" + "script>";

const SWORD_SCRIPT = "(function(){" +
  "var canvas=document.getElementById('sword'),ctx=canvas.getContext('2d'),dpr=Math.min(devicePixelRatio,2);" +
  "function rs(){canvas.width=window.innerWidth*dpr;canvas.height=window.innerHeight*dpr;canvas.style.cssText='width:'+window.innerWidth+'px;height:'+window.innerHeight+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}" +
  "rs();window.addEventListener('resize',rs);" +
  "var mx=window.innerWidth/2,my=window.innerHeight/2,tx=mx,ty=my,angle=-Math.PI/2,trail=[],sparks=[],t=0;" +
  "window.addEventListener('mousemove',function(e){tx=e.clientX;ty=e.clientY;});" +
  "function update(){" +
  "mx+=(tx-mx)*0.1;my+=(ty-my)*0.1;" +
  "var dx=tx-mx,dy=ty-my;" +
  "if(Math.abs(dx)>0.5||Math.abs(dy)>0.5){var ta=Math.atan2(dy,dx);var diff=ta-angle;while(diff>Math.PI)diff-=Math.PI*2;while(diff<-Math.PI)diff+=Math.PI*2;angle+=diff*0.1;}" +
  "if(Math.random()<0.95){trail.push({x:mx,y:my,vx:-Math.cos(angle)*(1+Math.random()),vy:-Math.sin(angle)*(1+Math.random()),life:1.5,size:1.5+Math.random()*2});}" +
  "var speed=Math.sqrt((tx-mx)*(tx-mx)+(ty-my)*(ty-my));" +
  "if(speed>1.5&&Math.random()<0.8){sparks.push({x:mx,y:my,vx:(Math.random()-0.5)*14,vy:(Math.random()-0.5)*14,life:1.2,size:2+Math.random()*3});}" +
  "for(var i=trail.length-1;i>=0;i--){var p=trail[i];p.x+=p.vx;p.y+=p.vy;p.vx*=0.95;p.vy*=0.95;p.life-=0.018;if(p.life<=0)trail.splice(i,1);}" +
  "if(trail.length>150)trail=trail.slice(-150);" +
  "for(var i=sparks.length-1;i>=0;i--){var p=sparks[i];p.x+=p.vx;p.y+=p.vy;p.vx*=0.92;p.vy*=0.92;p.life-=0.025;if(p.life<=0)sparks.splice(i,1);}" +
  "if(sparks.length>80)sparks=sparks.slice(-80);t++;" +
  "}" +
  "function drawSword(x,y,ang){" +
  "ctx.save();ctx.translate(x,y);ctx.rotate(ang);" +
  "var grd=ctx.createRadialGradient(0,0,0,0,0,90);grd.addColorStop(0,'rgba(180,210,255,0.1)');grd.addColorStop(1,'rgba(180,210,255,0)');ctx.beginPath();ctx.arc(0,0,90,0,Math.PI*2);ctx.fillStyle=grd;ctx.fill();" +
  "ctx.shadowColor='rgba(200,220,255,0.6)';ctx.shadowBlur=16;" +
  "var tipX=75,shoulderW=3.5,guardX=-14;" +
  "ctx.beginPath();ctx.moveTo(tipX,0);ctx.lineTo(20,-shoulderW);ctx.lineTo(guardX,-3);ctx.lineTo(guardX,3);ctx.lineTo(20,shoulderW);ctx.closePath();" +
  "var bladeGrd=ctx.createLinearGradient(guardX,0,tipX,0);bladeGrd.addColorStop(0,'rgba(80,100,160,0.5)');bladeGrd.addColorStop(0.25,'rgba(160,200,255,0.85)');bladeGrd.addColorStop(0.6,'rgba(220,240,255,0.95)');bladeGrd.addColorStop(1,'rgba(255,255,255,1)');ctx.fillStyle=bladeGrd;ctx.fill();" +
  "ctx.shadowBlur=0;ctx.beginPath();ctx.moveTo(-12,0);ctx.lineTo(65,0);ctx.strokeStyle='rgba(255,255,255,0.75)';ctx.lineWidth=1;ctx.stroke();" +
  "ctx.beginPath();ctx.moveTo(8,-2.2);ctx.quadraticCurveTo(40,-1,62,0);ctx.strokeStyle='rgba(160,200,255,0.3)';ctx.lineWidth=0.7;ctx.stroke();" +
  "ctx.beginPath();ctx.moveTo(8,2.2);ctx.quadraticCurveTo(40,1,62,0);ctx.strokeStyle='rgba(160,200,255,0.3)';ctx.lineWidth=0.7;ctx.stroke();" +
  "ctx.beginPath();ctx.arc(-15,0,9,0,Math.PI*2);var gg=ctx.createRadialGradient(-15,0,1,-15,0,9);gg.addColorStop(0,'rgba(255,230,150,1)');gg.addColorStop(0.6,'rgba(210,170,80,0.95)');gg.addColorStop(1,'rgba(160,120,40,0.85)');ctx.fillStyle=gg;ctx.fill();ctx.strokeStyle='rgba(255,220,100,0.6)';ctx.lineWidth=1.5;ctx.stroke();" +
  "ctx.beginPath();ctx.moveTo(-22,0);ctx.lineTo(-8,0);ctx.strokeStyle='rgba(140,100,30,0.8)';ctx.lineWidth=2;ctx.stroke();" +
  "ctx.beginPath();ctx.arc(-15,0,3.5,0,Math.PI*2);ctx.strokeStyle='rgba(140,100,30,0.6)';ctx.lineWidth=1;ctx.stroke();" +
  "ctx.beginPath();ctx.moveTo(-15,-3.2);ctx.bezierCurveTo(-22,-3.2,-22,3.2,-15,3.2);ctx.lineTo(-15,-3.2);ctx.fillStyle='rgba(60,40,15,0.95)';ctx.fill();" +
  "for(var gi=0;gi<7;gi++){var px=-17-gi*2.5;ctx.beginPath();ctx.moveTo(px,-3.2);ctx.bezierCurveTo(px-0.5,0,px-0.5,0,px,3.2);ctx.strokeStyle='rgba(140,180,240,0.45)';ctx.lineWidth=1.5;ctx.stroke();}" +
  "ctx.beginPath();ctx.moveTo(-34,-2.5);ctx.bezierCurveTo(-40,-1.5,-40,1.5,-34,2.5);ctx.lineTo(-34,-2.5);ctx.fillStyle='rgba(50,30,10,0.9)';ctx.fill();" +
  "ctx.beginPath();ctx.arc(-41,0,6,0,Math.PI*2);var pg=ctx.createRadialGradient(-41,0,0,-41,0,6);pg.addColorStop(0,'rgba(200,230,255,0.9)');pg.addColorStop(0.5,'rgba(140,190,255,0.7)');pg.addColorStop(1,'rgba(80,140,220,0.5)');ctx.fillStyle=pg;ctx.shadowColor='rgba(180,210,255,0.8)';ctx.shadowBlur=12;ctx.fill();ctx.strokeStyle='rgba(255,255,255,0.4)';ctx.lineWidth=1;ctx.stroke();" +
  "ctx.beginPath();ctx.arc(-41,0,2.5,0,Math.PI*2);ctx.fillStyle='rgba(60,40,15,0.8)';ctx.shadowBlur=0;ctx.fill();" +
  "for(var ti=0;ti<3;ti++){var _tx=-41,_ty=0,phase=ti*0.8+t*0.002;ctx.beginPath();ctx.moveTo(_tx,_ty+(ti-1)*2);ctx.quadraticCurveTo(_tx-8,_ty+(ti-1)*2+Math.sin(phase)*4,_tx-15,_ty+(ti-1)*2+Math.sin(phase)*6+5);ctx.strokeStyle='rgba(160,200,255,0.65)';ctx.lineWidth=1;ctx.stroke();}" +
  "ctx.restore();" +
  "}" +
  "function render(){" +
  "ctx.clearRect(0,0,canvas.width,canvas.height);" +
  "for(var i=0;i<trail.length;i++){var p=trail[i];ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fillStyle='rgba(180,210,255,'+(p.life*0.5)+')';ctx.shadowColor='rgba(180,210,255,0.5)';ctx.shadowBlur=6;ctx.fill();}" +
  "ctx.shadowBlur=0;" +
  "for(var i=0;i<sparks.length;i++){var p=sparks[i];ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fillStyle='rgba(180,220,255,'+(p.life*0.8)+')';ctx.shadowColor='rgba(180,220,255,0.6)';ctx.shadowBlur=8;ctx.fill();}" +
  "ctx.shadowBlur=0;drawSword(mx,my,angle);" +
  "}" +
  "function loop(){update();render();requestAnimationFrame(loop);}" +
  "loop();" +
  "})();";

const html = "<!doctype html>\n<html lang='zh-CN'>\n<head>\n  <meta charset='utf-8' />\n  <meta name='viewport' content='width=device-width, initial-scale=1' />\n  <meta name='description' content='起点中文网榜单追踪 - 四榜实时数据，题材权重动态换肤' />\n  <title>起点榜单追踪 · 玄幻</title>\n  <style>\n    :root{--bg:#101019;--bg2:#1B1428;--panel:rgba(248,250,252,0.08);--text:#F8FAFC;--muted:#D8D2CA;--gold:#F0D8A7}\n    *{box-sizing:border-box}html,body{margin:0;min-height:100vh}body{color:var(--text);font-family:\"PingFang SC\",\"Noto Serif SC\",\"STSong\",serif;background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%);overflow-x:hidden}.scene-bg{position:fixed;inset:0;z-index:0;opacity:.12;background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%)}.scene-vignette{position:fixed;inset:0;z-index:1;background:radial-gradient(ellipse 80% 60% at 50% 38%,rgba(6,14,26,.18) 0%,rgba(6,14,26,.72) 100%)}canvas#sword{position:fixed;inset:0;z-index:2;pointer-events:none}.shell{position:relative;z-index:3;min-height:100vh;padding:28px 18px 40px}" + CSS + "\n  </style>\n</head>\n<body>\n  <div class='scene-bg'></div>\n  <div class='scene-vignette'></div>\n  <canvas id='sword'></canvas>\n  <main class='shell'>\n    <section class='layout'>\n      <div class='side left-col'>\n        <div class='glass top-analysis-panel'>\n          <div class='panel-head'><div class='sword-line'></div><div><h3>🔥 综合热度</h3><p>月票·畅销·推荐三榜加权</p></div></div>\n          <div class='top-list'>" + analysis_rows + "</div>\n        </div>\n        <div class='glass theme-panel'>\n          <div class='panel-head'><div class='sword-line'></div><div><h3>本周题材</h3><p>裂天遗迹 · 断崖幽冥，位面压迫，黑暗旷野</p></div></div>\n          <div class='theme-pill'><i></i><span>玄幻</span></div>\n          <div class='tags'><span>玄幻 261.0</span><span>仙侠 193.4</span><span>都市 171.6</span><span>科幻 60.2</span><span>轻小说 39.0</span></div>\n          <ul class='analysis-list'><li>榜首保持不变：玄鉴仙族。</li><li>本轮没有新进榜作品。</li><li>本轮没有掉榜作品。</li></ul>\n        </div>\n      </div>\n      <div class='side'>\n        <div class='glass list-panel'><div class='panel-head'><div class='sword-line'></div><div><h3>月票榜</h3><p>主榜热度与硬强度</p></div></div><div class='rows-scroll'>" + makeRows(yuepiao.entries) + "</div></div>\n        <div class='glass list-panel'><div class='panel-head'><div class='sword-line'></div><div><h3>推荐榜</h3><p>扩散速度与读者投票</p></div></div><div class='rows-scroll'>" + makeRows(recom.entries) + "</div></div>\n      </div>\n      <div class='side'>\n        <div class='glass progress-panel'><div class='panel-head'><div class='sword-line'></div><div><h3>剑匣储能</h3><p>灵力规模模拟</p></div></div><div class='progress-wrap'><div class='plabel'><span>储能</span><strong class='glow-num'>100%</strong></div><div class='progress'><div class='bar' style='width:100%'></div></div><div class='pmeta'>下次更新: 2026-04-18 18:00 MDT (埃德蒙顿)</div></div></div>\n        <div class='glass list-panel'><div class='panel-head'><div class='sword-line'></div><div><h3>畅销榜</h3><p>付费意愿与消费热度</p></div></div><div class='rows-scroll'>" + makeRows(hotsales.entries) + "</div></div>\n        <div class='glass list-panel'><div class='panel-head'><div class='sword-line'></div><div><h3>收藏榜</h3><p>长期积累与经典沉淀</p></div></div><div class='rows-scroll'>" + makeRows(collect.entries) + "</div></div>\n      </div>\n      <div class='side'>\n        <div class='glass reviews-panel'>\n          <div class='panel-head'><div class='sword-line'></div><div><h3>📋 网评摘录</h3><p>来自读者社区 · 仅供参考</p></div></div>\n          <div class='reviews-list' id='reviews-list'>" + reviewItems + "</div>\n        </div>\n      </div>\n    </section>\n  </main>\n  " + MODAL_HTML + "\n  " + BOOK_DATA_SCRIPT + "\n  <script>" + SWORD_SCRIPT + "</" + "script>\n</body>\n</html>";

fs.mkdirSync('dist', { recursive: true });
fs.writeFileSync('dist/index.html', html);
fs.writeFileSync('data/site/index.html', html);
console.log('Generated index.html (' + html.length + ' chars)');
top10.forEach((b, i) => console.log('  ' + (i+1) + '. ' + b.title + ' (' + b.score + 'pts)'));
