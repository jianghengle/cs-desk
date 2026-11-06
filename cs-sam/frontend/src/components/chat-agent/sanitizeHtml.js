// Sanitizes HTML produced from the model's markdown before it goes into v-html.
//
// Model output can be steered by prompt injection, so it is untrusted:
// - DOMPurify removes scripts, event handlers (onerror=...) and javascript: URLs.
// - Images, media, embeds, forms, SVG and inline styles are also removed: they
//   load automatically, so a URL like https://evil.example/?d=<data> would leak
//   data without any click (CSS url() in style attributes can do the same).
// - Links are kept but open in a new tab without a referrer.
import DOMPurify from 'dompurify'

const FORBID_TAGS = [
  'img', 'picture', 'source', 'video', 'audio', 'track', 'iframe', 'frame', 'object', 'embed',
  'form', 'input', 'button', 'select', 'textarea', 'style', 'link', 'meta', 'base', 'svg', 'math',
]
const FORBID_ATTR = ['style', 'srcset', 'background', 'poster', 'action', 'formaction', 'ping']

let hookInstalled = false

export function sanitizeHtml (html) {
  if (!hookInstalled) {
    DOMPurify.addHook('afterSanitizeAttributes', function (node) {
      if (node.tagName === 'A' && node.hasAttribute('href')) {
        node.setAttribute('target', '_blank')
        node.setAttribute('rel', 'noopener noreferrer')
      }
    })
    hookInstalled = true
  }
  return DOMPurify.sanitize(html || '', {
    FORBID_TAGS: FORBID_TAGS,
    FORBID_ATTR: FORBID_ATTR,
    ALLOW_DATA_ATTR: false,
  })
}
