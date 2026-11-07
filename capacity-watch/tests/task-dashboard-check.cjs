// Offline DOM contract checks. This deliberately makes no layout or visual claims.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
class Element {
  constructor(tag) { this.tagName = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.style = {}; this._text = ''; }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(''); }
  set innerHTML(value) { throw new Error('Task rendering must not interpret HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, fn) { this.handlers[k] = fn; }
  contains(node) { return this === node || this.children.some(c => c.contains(node)); }
  querySelectorAll(selector) { return flatten(this).filter(n => selector === '[data-focus]' && n.dataset.focus); }
  focus() { document.activeElement = this; }
  setSelectionRange(start) { this.selectionStart = start; }
  select() {}
}
const flatten = n => n.children.flatMap(c => [c, ...flatten(c)]);
const document = {activeElement: null, createElement: tag => new Element(tag)};
const draws = {}, calcs = {};
let data = [
  {task_key:'mesh:peer:a', title:'Alpha <script>bad()</script>', project:'one', outcome:'done', started:'2026-11-07', duration_min:'2', cost_usd:'1.5', tokens_out:'100', subagents:'2', tool_errors:'1', api_errors:'0', api_retries:'2', brief_excerpt:'Prompt <b>literal</b>', result_excerpt:'Done', ld_path:'/tmp/a.md', docs:'/tmp/doc.md', outputs:'a; b', billing:'subscription'},
  {task_key:'codex:local:b', title:'Beta', project:'two', outcome:'failed', started:'2026-11-06', duration_min:'10', cost_usd:'', tokens_out:'20', subagents:'', tool_errors:'', api_errors:'', brief_excerpt:'Second', ld_path:'/tmp/b.md'},
];
const dash = {calc:(k,v)=>{calcs[k]=v;}, draw:(k,fn)=>{draws[k]=fn;}, data:()=>({status:'ok',data:calcs.task_summary.fn(data)})};
const html = fs.readFileSync(process.argv[2], 'utf8');
vm.runInNewContext(html.split('<script>')[1].split('</script>')[0], {document,dash,d3:{format:()=>String}, Intl, console});
const root = new Element('div');
const find = pred => flatten(root).find(pred);
const click = n => { assert.ok(n); n.handlers.click({stopPropagation(){}}); };
const rowButtons = () => flatten(root).filter(n => n.dataset.focus?.startsWith('row-'));
draws['task-ledger'](root);
assert.equal(rowButtons().length, 2);
assert.equal(rowButtons()[0].textContent, data[0].title);
click(rowButtons()[0]);
assert.equal(find(n => n.tagName==='textarea').value, '/tmp/a.md');
assert.ok(find(n => n.tagName==='pre').textContent.includes('<b>literal</b>'));
assert.equal(rowButtons()[0].attrs['aria-expanded'], 'true');
assert.equal(rowButtons()[0].tagName, 'button'); // Native Enter and Space activation.
click(find(n => n.dataset.focus==='chip-failed'));
assert.equal(rowButtons().length, 1);
assert.equal(rowButtons()[0].textContent, 'Beta');
click(find(n => n.dataset.focus==='chip-all'));
click(find(n => n.dataset.focus==='sort-duration_min'));
assert.equal(rowButtons()[0].textContent, data[0].title);
click(find(n => n.dataset.focus==='sort-duration_min'));
assert.equal(rowButtons()[0].textContent, 'Beta');
let input = find(n=>n.dataset.focus==='filter'); input.value='one'; input.focus(); input.selectionStart=3; input.handlers.input();
assert.equal(rowButtons().length,1);
assert.equal(document.activeElement.dataset.focus,'filter');
assert.equal(document.activeElement.selectionStart,3);
input=document.activeElement; input.value='nothing matches'; input.handlers.input();
assert.equal(rowButtons().length,0);
assert.ok(find(n=>n.attrs.role==='status').textContent.startsWith('0 of 2'));
assert.equal(calcs.task_summary.fn(data)[1].failures,'');
assert.equal(calcs.task_summary.fn(data)[0].failures,1);
console.log('Task DOM checks passed: sorting, filtering, outcome chips, expansion, native buttons, focus, literal text, unknown metrics. Layout not tested.');
