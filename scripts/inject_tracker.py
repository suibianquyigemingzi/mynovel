#!/usr/bin/env python3
"""Inject generated tracker HTML into the Astro index page at build time."""
from pathlib import Path
import re

# Read the generated tracker HTML
tracker_html = Path("data/site/index.html").read_text(encoding="utf-8")

# Extract body content
body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", tracker_html, re.DOTALL)
body_content = body_match.group(1) if body_match else tracker_html

# Extract style content
style_match = re.search(r"<style[^>]*>([\s\S]*?)</style>", tracker_html, re.DOTALL)
style_content = style_match.group(1) if style_match else ""

# Escape for JS string use
body_js = body_content.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
style_js = style_content.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

astro = f'''---
import { readFileSync } from 'fs';
import {{ join }} from 'path';

const trackerHtmlPath = join(process.cwd(), 'data', 'site', 'index.html');
let trackerHtml = '<div style="padding:40px;color:#fff">数据加载中...</div>';

try {{
  const raw = readFileSync(trackerHtmlPath, 'utf-8');
  const bodyMatch = raw.match(/<body[^>]*>([\\\\s\\\\S]*?)<\\\\/body>/);
  const bodyContent = bodyMatch ? bodyMatch[1] : raw;
  const styleMatch = raw.match(/<style[^>]*>([\\\\s\\\\S]*?)<\\\\/style>/);
  const styleContent = styleMatch ? styleMatch[1] : '';
  trackerHtml = `<style is:global>${{styleContent}}</style>${{bodyContent}}`;
}} catch (e) {{
  // fallback
}}
---
<div class="tracker-root" set:html={{trackerHtml}} />

<script>
  let mx=0, my=0;
  document.documentElement.style.setProperty('--mx','0px');
  document.documentElement.style.setProperty('--my','0px');
  window.addEventListener('mousemove', e => {{
    const rx=(e.clientX/window.innerWidth-.5)*12;
    const ry=(e.clientY/window.innerHeight-.5)*8;
    document.documentElement.style.setProperty('--mx',rx+'px');
    document.documentElement.style.setProperty('--my',ry+'px');
    const bg=document.querySelector('.scene-bg');
    if(bg) bg.style.transform='translate3d('+rx+'px,'+ry+'px,0) scale(1.02)';
  }});

  const canvas=document.getElementById('qi');
  if (!canvas) {{
    const c=document.createElement('canvas');
    c.id='qi';
    c.style.cssText='position:fixed;inset:0;z-index:2;pointer-events:none';
    document.body.prepend(c);
  }}
  const qiCanvas=document.getElementById('qi');
  if(qiCanvas){{
    const ctx=qiCanvas.getContext('2d');
    let pts=[];
    function resize(){{
      const dpr=Math.min(devicePixelRatio,2);
      qiCanvas.width=window.innerWidth*dpr;
      qiCanvas.height=window.innerHeight*dpr;
      qiCanvas.style.width=window.innerWidth+'px';
      qiCanvas.style.height=window.innerHeight+'px';
      ctx.setTransform(dpr,0,0,dpr,0,0);
    }}
    function spawn(x,y){{
      for(let i=0;i<5;i++)
        pts.push({{x,y,tx:x+(Math.random()-.5)*60,ty:y+(Math.random()-.5)*60,life:35+Math.random()*20,r:1+Math.random()*2}});
      if(pts.length>120)pts=pts.slice(-120);
    }}
    window.addEventListener('mousemove',e=>{{spawn(e.clientX,e.clientY);}});
    function tick(){{
      ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
      pts.forEach(function(p){{
        p.x+=(p.tx-p.x)*.028;p.y+=(p.ty-p.y)*.028;p.life-=.8;
        ctx.fillStyle='rgba(180,210,255,'+(Math.max(0,p.life/55))+')';
        ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();
      }});
      pts=pts.filter(function(p){{return p.life>0;}});
      requestAnimationFrame(tick);
    }}
    resize();tick();
    window.addEventListener('resize',resize);
  }}
</script>
'''

Path("src/pages/index.astro").write_text(astro, encoding="utf-8")
print("Astro page updated successfully")