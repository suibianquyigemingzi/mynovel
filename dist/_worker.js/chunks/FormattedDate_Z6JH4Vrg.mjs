globalThis.process ??= {}; globalThis.process.env ??= {};
import { e as createAstro, c as createComponent, d as addAttribute, a as renderTemplate, m as maybeRenderHead } from './astro/server_CJHwISMA.mjs';
/* empty css                         */

const $$Astro$1 = createAstro("https://mynovel.me");
const $$BaseHead = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$1, $$props, $$slots);
  Astro2.self = $$BaseHead;
  const canonicalURL = new URL(Astro2.url.pathname, Astro2.site);
  const { title, description, image = "/blog-placeholder-1.jpg" } = Astro2.props;
  return renderTemplate`<!-- Global Metadata --><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta name="generator"${addAttribute(Astro2.generator, "content")}><!-- Font preloads --><link rel="preload" href="/fonts/atkinson-regular.woff" as="font" type="font/woff" crossorigin><link rel="preload" href="/fonts/atkinson-bold.woff" as="font" type="font/woff" crossorigin><!-- Canonical URL --><link rel="canonical"${addAttribute(canonicalURL, "href")}><!-- Primary Meta Tags --><title>${title}</title><meta name="title"${addAttribute(title, "content")}><meta name="description"${addAttribute(description, "content")}><!-- Open Graph / Facebook --><meta property="og:type" content="website"><meta property="og:url"${addAttribute(Astro2.url, "content")}><meta property="og:title"${addAttribute(title, "content")}><meta property="og:description"${addAttribute(description, "content")}><meta property="og:image"${addAttribute(new URL(image, Astro2.url), "content")}><!-- Twitter --><meta property="twitter:card" content="summary_large_image"><meta property="twitter:url"${addAttribute(Astro2.url, "content")}><meta property="twitter:title"${addAttribute(title, "content")}><meta property="twitter:description"${addAttribute(description, "content")}><meta property="twitter:image"${addAttribute(new URL(image, Astro2.url), "content")}>`;
}, "/tmp/mynovel/src/components/BaseHead.astro", void 0);

const $$Header = createComponent(($$result, $$props, $$slots) => {
  const navLinks = [
    { href: "/", label: "\u9996\u9875" },
    { href: "/rankings", label: "\u6392\u884C\u699C" },
    { href: "/categories", label: "\u5206\u7C7B" },
    { href: "/complete", label: "\u5B8C\u672C" }
  ];
  return renderTemplate`${maybeRenderHead()}<header class="site-header" data-astro-cid-3ef6ksr2> <div class="header-inner" data-astro-cid-3ef6ksr2> <a href="/" class="logo" data-astro-cid-3ef6ksr2>起点中文网</a> <nav class="main-nav" data-astro-cid-3ef6ksr2> ${navLinks.map((link) => renderTemplate`<a${addAttribute(link.href, "href")} data-astro-cid-3ef6ksr2>${link.label}</a>`)} </nav> <div class="header-actions" data-astro-cid-3ef6ksr2> <input type="text" placeholder="搜索书名/作者" class="search-input" data-astro-cid-3ef6ksr2> <button class="btn-primary" data-astro-cid-3ef6ksr2>登录</button> </div> </div> </header> `;
}, "/tmp/mynovel/src/components/Header.astro", void 0);

const $$Footer = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${maybeRenderHead()}<footer class="site-footer" data-astro-cid-sz7xmlte> <div class="footer-inner" data-astro-cid-sz7xmlte> <p data-astro-cid-sz7xmlte>© 2024 起点中文网 | 仅供学习交流</p> <p data-astro-cid-sz7xmlte>本平台不存储任何小说内容，所有资源均来自公开网络</p> </div> </footer> `;
}, "/tmp/mynovel/src/components/Footer.astro", void 0);

const $$Astro = createAstro("https://mynovel.me");
const $$FormattedDate = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$FormattedDate;
  const { date } = Astro2.props;
  return renderTemplate`${maybeRenderHead()}<time${addAttribute(date.toISOString(), "datetime")}> ${date.toLocaleDateString("en-us", {
    year: "numeric",
    month: "short",
    day: "numeric"
  })} </time>`;
}, "/tmp/mynovel/src/components/FormattedDate.astro", void 0);

export { $$BaseHead as $, $$Header as a, $$FormattedDate as b, $$Footer as c };
