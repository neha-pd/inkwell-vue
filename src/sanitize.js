import DOMPurify from 'dompurify'
export function safeLink(value) {
 try { const url = new URL(String(value).trim()); return ['https:', 'http:', 'mailto:'].includes(url.protocol) ? url.href : null } catch { return null }
}
export function safeImage(value) {
 const text=String(value).trim()
 if (/^data:image\/(png|jpeg|webp|gif);base64,[a-z0-9+/=]+$/i.test(text) && text.length < 3000000) return text
 try { const url=new URL(text); return url.protocol==='https:' ? url.href : null } catch { return null }
}
export function sanitizeHTML(value = '') {
 if (typeof window === 'undefined') return ''
 const clean = DOMPurify.sanitize(String(value), {
  ALLOWED_TAGS: ['p','br','strong','b','em','i','u','s','del','h1','h2','h3','h4','h5','h6','ul','ol','li','a','blockquote','pre','code','hr','span','mark','sub','sup','img','table','tbody','thead','tr','td','th','div'],
  ALLOWED_ATTR: ['href','start','src','alt','title','colspan','rowspan','style','data-type','data-checked','data-color'], ALLOW_DATA_ATTR: false, ALLOW_ARIA_ATTR: false,
 })
 const template = document.createElement('template'); template.innerHTML = clean
 template.content.querySelectorAll('*').forEach(el => {
  const style=el.style, keep=[]
  const color=v => /^(#[\da-f]{3,8}|rgba?\([\d.,%\s]+\))$/i.test(v)
  if (style) {
   if (['left','center','right','justify'].includes(style.textAlign)) keep.push(`text-align:${style.textAlign}`)
   if (color(style.color)) keep.push(`color:${style.color}`)
   if (color(style.backgroundColor)) keep.push(`background-color:${style.backgroundColor}`)
   if (/^(1[0-9]|[2-6][0-9]|7[0-2])px$/.test(style.fontSize)) keep.push(`font-size:${style.fontSize}`)
   if (['sans-serif','serif','monospace'].includes(style.fontFamily)) keep.push(`font-family:${style.fontFamily}`)
   if (/^(1|1\.5|2)$/.test(style.lineHeight)) keep.push(`line-height:${style.lineHeight}`)
   el.removeAttribute('style'); if(keep.length) el.setAttribute('style',keep.join(';'))
  }
  for(const attr of ['colspan','rowspan']) if(el.hasAttribute(attr)) { const n=Number(el.getAttribute(attr)); if(!Number.isInteger(n)||n<1||n>30) el.removeAttribute(attr) }
  if(el.hasAttribute('data-type') && !['taskList','taskItem'].includes(el.getAttribute('data-type'))) el.removeAttribute('data-type')
  if(el.hasAttribute('data-checked') && !['true','false'].includes(el.getAttribute('data-checked'))) el.removeAttribute('data-checked')
  if(el.hasAttribute('data-color') && !color(el.getAttribute('data-color'))) el.removeAttribute('data-color')
 })
 template.content.querySelectorAll('a').forEach(a => {
  const href = safeLink(a.getAttribute('href') || '')
  if (href) { a.setAttribute('href', href); a.setAttribute('rel', 'noopener noreferrer') }
  else a.replaceWith(...a.childNodes)
 })
 template.content.querySelectorAll('img').forEach(img=>{
  const src=safeImage(img.getAttribute('src')||'')
  const alt=(img.getAttribute('alt')||'').trim()
  // Clipboard HTML may resolve relative sources against an HTTPS page before
  // reaching us. Apply the same description requirement as the image dialog.
  if(!src || !alt) img.remove()
  else { img.setAttribute('src',src);img.setAttribute('alt',alt) }
 })
 return template.innerHTML
}
