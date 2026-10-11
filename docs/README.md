# Inkwell Vue

A reusable Vue 3 rich-text editor built on Tiptap and ProseMirror. The 0.3 preview adds selection tools, a keyboard-accessible context menu and an inline link popover, alongside structured documents, tables, images, search and portable exports.

[Open the playground](https://neha-desai.de5.net/inkwell/) · [Neha’s portfolio](https://neha-desai.de5.net/)

## Working features

| Area | Included |
|---|---|
| Formatting | Bold, italic, underline, strikethrough, highlight, subscript, superscript, inline code and clear formatting |
| Typography | Six heading levels, paragraphs, serif/sans/mono, font sizes, text color and four alignments |
| Structure | Bullet/numbered lists, nested checklists, quotes, code blocks and horizontal rules |
| Tables | Insert, add/remove rows and columns, merge/split selected cells, header rows/columns, remove table |
| Images and links | HTTPS images or bounded local raster files, required image descriptions; validated web/email links |
| Editing | Undo/redo, case-insensitive find/replace within text spans, focus mode, words/characters, placeholder |
| Integration | HTML v-model, change events, typed public methods, reactive read-only/disabled states |
| Documents | HTML/Markdown/text import; HTML/Markdown/text/Tiptap JSON export in the demo; explicit browser-local draft save/restore |
| Contextual editing | Selection toolbar with word count; right-click or Shift+F10 menu; retained-selection link popover; viewport clamping |
| Keyboard | Roving formatting toolbar, labeled controls, link/image forms, Escape dismissal, focus-mode tab containment |

The editor is a single-user preview, not a complete document platform. Collaboration, comments, tracked changes, DOCX/PDF conversion, server uploads, permissions and AI generation are **not implemented**. Syntax highlighting is not included. Markdown does not preserve all HTML styling or complex table layouts. Find/replace matches within individual formatted text spans, not across mark boundaries. Mobile IME, screen-reader audits and full Nuxt hydration still need wider testing.

## Use the package

The package is not published to the npm registry. Download the versioned tarball from the playground or build it locally:

```sh
npm install
npm run build
npm pack
# In your Vue application:
npm install ./neha-pd-inkwell-vue-0.3.1.tgz
```

```vue
<script setup>
import { ref } from 'vue'
import { InkwellEditor } from '@neha-pd/inkwell-vue'
import '@neha-pd/inkwell-vue/style.css'
const document = ref('<h2>A useful first draft</h2><p>Start here.</p>')
const editor = ref(null)
</script>
<template>
  <InkwellEditor ref="editor" v-model="document" label="Article body"
    placeholder="Write an introduction…" />
</template>
```

Requires Vue 3.5 or later. The package externalizes Vue and Tiptap dependencies, with those dependencies declared in package.json. The demo includes the full editing engine; consumers can choose their own application-level lazy loading.

### Props, events and methods

- Props: `modelValue`, `label`, `placeholder` (initial value), `readOnly`, `disabled`.
- Events: `update:modelValue` emits supported sanitized HTML; `change` emits `{ html, text }`.
- Ref methods: `focus()`, `getHTML()`, `getText()`, `getJSON()`, `getMarkdown()`, `setHTML(value)`, `setMarkdown(value)`.
- Imperative setters reject editing when read-only/disabled. Parent-controlled v-model replacements remain allowed and can alter selection/history.
- The component does not save or upload data. Draft storage and downloads belong to the demo, not the library. An HTTPS image URL is fetched by the browser when displayed; local raster files are embedded into the document.

## Content handling

Untrusted initial HTML, external HTML updates, paste HTML, imported Markdown output and emitted HTML pass through a restricted DOMPurify sanitizer. Links allow HTTP, HTTPS and mailto. Images allow HTTPS and bounded base64 PNG/JPEG/WebP/GIF, not SVG or executable URLs. Formatting CSS is limited to specific alignment, color, font and size values; event handlers and URL-bearing styles are removed. Table spans are bounded.

This is not a security certification. Applications must enforce authorization, storage/upload limits and content validation at their own boundaries. The exported sanitizer returns an empty string outside a browser. Server rendering is a placeholder; supplied document HTML is not rendered server-side by this component.

## Development and validation

```sh
npm install
npm run dev          # 127.0.0.1:8842
npm run build        # library and type declarations
npm run build:demo   # static docs/
python tests/browser.py
python tests/extended.py
python tests/contextual.py
python tests/controls.py
```

Python browser tests require Playwright and Chromium. `INKWELL_URL` can target the built or deployed demo. Checks exercise actual editing, clipboard paste, read-only state, sanitization, table/list round trips, import/export, local drafts and narrow viewports. Screenshots in artifacts are from the running demo. Passing automated checks does not establish WCAG conformance.

## Sources and license

- [Tiptap table commands](https://tiptap.dev/docs/editor/extensions/nodes/table)
- [Tiptap TextStyleKit](https://tiptap.dev/docs/editor/extensions/functionality/text-style-kit)
- [Tiptap Markdown](https://tiptap.dev/docs/editor/markdown)
- MIT license. Dependencies and bundled font licensing are recorded in THIRD_PARTY_NOTICES.md.

### Contextual editing

Select text to reveal the compact formatting toolbar. Right-click within the editable document, or press Shift+F10 / the Context Menu key, to open formatting actions. Arrow keys, Home and End navigate the menu; Enter activates an action. Escape dismisses contextual tools and returns focus to the document. Scrolling closes the context/link menu; selection tools follow the range. Read-only and disabled editors retain the browser’s native context menu. Parent content replacement dismisses stale contextual selections.

The warm paper/copper demo uses self-hosted Manrope and official Phosphor Vue icons. The editor uses native labeled selects for predictable keyboard and assistive-technology behavior.

Built with AI assistance. No customer adoption or production-readiness claims.

### 0.3 control refinement

Structure, font, size and alignment use a shared custom listbox with arrow/Home/End navigation, typeahead, Escape, Tab dismissal and outside-click handling. The demo inspector uses native checkbox switches, a radio-group export selector and an accessible styled file input. Secondary import and local-draft controls are expandable. Selected document ranges are retained when applying formatting. Reference sources and original design decisions are recorded in `artifacts/design-references/README.md`.

Patch 0.3.1 applies the image-description requirement consistently to pasted/imported HTML as well as the image dialog. Undescribed images are removed; HTTPS or bounded raster images with meaningful alt text remain supported.
