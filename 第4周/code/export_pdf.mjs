// Set WEEK4_TOOLS to a directory containing unpacked marked, mermaid,
// playwright-core and pdfjs-dist packages; set BROWSER_BIN if needed.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath, pathToFileURL} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = process.env.WEEK4_TOOLS;
if (!tools) throw Error('Set WEEK4_TOOLS to the render dependency directory.');
const {marked} = await import(pathToFileURL(path.join(tools,'marked/lib/marked.esm.js')));
const {chromium} = await import(pathToFileURL(path.join(tools,'playwright-core/index.mjs')));
const name = '20241328蔡贸俊《密码系统设计》';
const md = fs.readFileSync(path.join(root,`${name}.md`),'utf8');
const diagram = fs.readFileSync(path.join(root,'assets/week4-mindmap.mmd'),'utf8');
const inlineDiagram = md.match(/```mermaid\n([\s\S]*?)\n```/)[1];
if (inlineDiagram.trim() !== diagram.trim()) throw Error('Mindmap source differs from report.');
const types = {'.js':'text/javascript','.mjs':'text/javascript','.html':'text/html; charset=utf-8',
  '.png':'image/png','.svg':'image/svg+xml','.pdf':'application/pdf'};
const server = http.createServer((req,res) => {
  const pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  let base=root, rel=pathname;
  if (pathname.startsWith('/vendor/')) {base=tools;rel=pathname.slice(7);}
  const target=path.resolve(base,'.'+rel);
  if (!target.startsWith(path.resolve(base)+path.sep)) {res.writeHead(403).end();return;}
  try {res.setHeader('Content-Type',types[path.extname(target)] || 'text/plain; charset=utf-8');res.end(fs.readFileSync(target));}
  catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({executablePath:process.env.BROWSER_BIN ||
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
try {
  const page=await browser.newPage({viewport:{width:2000,height:1600},deviceScaleFactor:2});
  await page.goto(origin+'/README.md');
  await page.setContent('<html><body style="margin:24px;background:#fff"><div id="map"></div></body></html>');
  await page.addScriptTag({type:'module',content:`
    import mermaid from '${origin}/vendor/mermaid/dist/mermaid.esm.min.mjs';
    window.mermaid=mermaid;
  `});
  await page.waitForFunction(()=>!!window.mermaid);
  const dimensions=await page.evaluate(async source => {
    mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'default',
      fontFamily:'Microsoft YaHei, sans-serif',mindmap:{padding:20,useMaxWidth:false}});
    const {svg}=await mermaid.render('week4map',source);
    document.getElementById('map').innerHTML=svg;
    await document.fonts.ready;
    const el=document.querySelector('#map svg');
    const box=el.viewBox.baseVal;
    el.style.maxWidth='none';el.style.width=`${Math.ceil(box.width)}px`;el.style.height=`${Math.ceil(box.height)}px`;
    document.getElementById('map').style.width=`${Math.ceil(box.width)}px`;
    return {width:Math.ceil(box.width),height:Math.ceil(box.height)};
  },diagram);
  await page.setViewportSize({width:dimensions.width+48,height:dimensions.height+48});
  await page.locator('#map').screenshot({path:path.join(root,'assets/week4-mindmap.png')});
  fs.writeFileSync(path.join(root,'assets/week4-mindmap.svg'),await page.locator('#map').innerHTML(),'utf8');
  let body=marked.parse(md);
  body=body.replace(/<p><img src="assets\/week4-mindmap.png"[^>]*><\/p>/,
    '<figure class="map"><img src="assets/week4-mindmap.png" alt="第四周学习思维导图"><figcaption>第四周学习思维导图 · Mermaid 实际渲染</figcaption></figure>');
  const css=`
    @page {size:A4; margin:17mm 16mm 19mm;}
    * {box-sizing:border-box;}
    body {font-family:"Microsoft YaHei","SimSun",sans-serif;color:#243041;font-size:10pt;line-height:1.65;margin:0;}
    h1 {font-size:23pt;color:#123d6a;line-height:1.35;border-bottom:3px solid #2c6fa8;padding-bottom:12px;margin:8px 0 20px;}
    h2 {font-size:15pt;color:#123d6a;border-bottom:1px solid #bdcfe0;padding-bottom:5px;margin:23px 0 12px;}
    h3 {font-size:12pt;color:#205880;margin:17px 0 9px;}
    h4 {font-size:10.7pt;color:#205880;margin:14px 0 7px;}
    h1,h2,h3,h4 {break-after:avoid;}
    p {margin:8px 0;orphans:3;widows:3;}
    a {color:#175b8c;text-decoration:none;overflow-wrap:anywhere;}
    strong {color:#173d60;}
    blockquote {margin:12px 0;padding:8px 12px;background:#f1f6fa;border-left:3px solid #5289b5;color:#4d5e70;font-size:9pt;}
    blockquote p {margin:3px 0;}
    table {border-collapse:collapse;width:100%;margin:12px 0;font-size:9pt;}
    th,td {border:1px solid #cbd7e0;padding:6px 8px;vertical-align:top;}
    th {background:#eaf1f7;color:#173d60;}
    th {white-space:nowrap;}
    tr {break-inside:avoid;}
    pre {white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;border:1px solid #dce3ea;border-radius:4px;padding:10px 12px;font-size:8pt;line-height:1.5;}
    code {font-family:Consolas,"Microsoft YaHei",monospace;font-size:.91em;}
    p code,li code,td code {background:#f0f3f6;padding:1px 3px;overflow-wrap:anywhere;}
    pre code {font-size:inherit;}
    ul,ol {padding-left:23px;margin:8px 0;}
    li {margin:4px 0;}
    hr {border:0;border-top:1px solid #d4e0ea;margin:20px 0;}
    img {max-width:100%;}
    figure.map {margin:10px 0;break-inside:avoid;text-align:center;}
    figure.map img {max-height:220mm;object-fit:contain;}
    figcaption {font-size:8pt;color:#68788b;}
    @media screen {body {max-width:794px;margin:30px auto;padding:30px 50px;background:white;}html{background:#e9edf2;}}
  `;
  const html=`<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>第四周预习报告 · 20241328蔡贸俊</title><style>${css}</style></head><body>${body}</body></html>`;
  fs.writeFileSync(path.join(root,`${name}第4周.html`),html,'utf8');
  await page.setViewportSize({width:1000,height:1300});
  await page.goto(origin+'/'+encodeURIComponent(`${name}第4周.html`));
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
  await page.pdf({path:path.join(root,`${name}第4周.pdf`),format:'A4',printBackground:true,
    preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
    footerTemplate:'<div style="font-size:8px;color:#61758a;width:100%;text-align:center;">20241328 蔡贸俊 · 密码系统设计 · 第四周　<span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
  console.log('Generated HTML, PNG, SVG and PDF. Mindmap size:',dimensions);
  // Extract text from every PDF page and render two actual PDF pages for review.
  await page.goto(origin+'/README.md');
  await page.setContent('<html><body style="margin:0"><canvas id="pdf"></canvas></body></html>');
  await page.addScriptTag({type:'module',content:`
    import * as pdfjs from '${origin}/vendor/pdfjs-dist/build/pdf.mjs';
    pdfjs.GlobalWorkerOptions.workerSrc='${origin}/vendor/pdfjs-dist/build/pdf.worker.mjs';
    window.pdfDoc=await pdfjs.getDocument('${origin}/${encodeURIComponent(name+'第4周.pdf')}').promise;
  `});
  await page.waitForFunction(()=>!!window.pdfDoc);
  const pages=await page.evaluate(async()=>{
    const result=[];
    for(let n=1;n<=pdfDoc.numPages;n++){
      const p=await pdfDoc.getPage(n);const content=await p.getTextContent();
      result.push({page:n,text:content.items.map(i=>i.str).join(' ')});
    }
    return result;
  });
  const text=pages.map(p=>`PAGE ${p.page}\n${p.text}`).join('\n\n');
  fs.writeFileSync(path.join(root,'evidence/pdf-text-check.txt'),text,'utf8');
  const required=['第四周预习报告','AI 对学习内容的总结','反思与补充','学习思维导图','基于 AI 的学习','学习实践过程遇到的问题','作业提交要求','参考资料'];
  for(const section of required) if(!text.replace(/\s+/g,'').includes(section.replace(/\s+/g,''))) throw Error(`Missing PDF section: ${section}`);
  const mapPage=pages.find(p=>p.text.includes('Mermaid 实际渲染'))?.page || 1;
  for(const n of [...new Set([1,mapPage,pages.length])]){
    const size=await page.evaluate(async n=>{
      const p=await pdfDoc.getPage(n),v=p.getViewport({scale:1.5}),c=document.getElementById('pdf');
      c.width=Math.ceil(v.width);c.height=Math.ceil(v.height);
      await p.render({canvasContext:c.getContext('2d'),viewport:v}).promise;
      return {width:c.width,height:c.height};
    },n);
    await page.setViewportSize(size);
    await page.locator('#pdf').screenshot({path:path.join(root,`evidence/pdf-page-${n}.png`)});
  }
  console.log('PDF verified:',pages.length,'pages; all required sections present; diagram page',mapPage);
} finally {
  await browser.close();
  await new Promise(resolve=>server.close(resolve));
}
