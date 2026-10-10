import DOMPurify from 'dompurify'
export function safeLink(value) {
 try { const url = new URL(value.trim()); return ['https:', 'http:', 'mailto:'].includes(url.protocol) ? url.href : null } catch { return null }
}
export function sanitizeHTML(value = '') {
 if (typeof window === 'undefined') return ''
 const clean = DOMPurify.sanitize(String(value), {
  ALLOWED_TAGS: ['p','br','strong','b','em','i','h2','h3','ul','ol','li','a'],
  ALLOWED_ATTR: ['href','start'], ALLOW_DATA_ATTR: false, ALLOW_ARIA_ATTR: false,
 })
 const template = document.createElement('template'); template.innerHTML = clean
 template.content.querySelectorAll('a').forEach(a => {
  const href = safeLink(a.getAttribute('href') || '')
  if (href) { a.setAttribute('href', href); a.setAttribute('rel', 'noopener noreferrer') }
  else a.replaceWith(...a.childNodes)
 })
 return template.innerHTML
}
