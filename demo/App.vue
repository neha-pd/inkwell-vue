<script setup>
import { computed, ref } from 'vue'
import { InkwellEditor, sanitizeHTML } from '../src/index.js'
const sample='<h2>A little space to think.</h2><p>The best tools make room for the work. A clear thought, a useful note, a first draft that finally gets written.</p><p>This is <strong>Inkwell</strong>: a small rich-text component for Vue. Select a few words and make them <em>yours</em>.</p><ul><li><p>Write something worth keeping.</p></li><li><p>Give it a little structure.</p></li><li><p>Let the words do the rest.</p></li></ul>'
const html=ref(sample), readOnly=ref(false), disabled=ref(false), source=ref(sample), status=ref(''), output=ref('html')
const wordCount=computed(()=>{const doc=new DOMParser().parseFromString(sanitizeHTML(html.value),'text/html'); return doc.body.textContent.trim().split(/\s+/).filter(Boolean).length})
function replace(){ html.value=sanitizeHTML(source.value);status.value='Content replaced using the component’s v-model.' }
async function copy(){try{await navigator.clipboard.writeText(sanitizeHTML(html.value));status.value='HTML copied.'}catch{status.value='Clipboard unavailable. Select and copy the HTML below.'}}
function download(){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([sanitizeHTML(html.value)],{type:'text/html'}));a.download='inkwell-document.html';a.click();URL.revokeObjectURL(a.href);status.value='HTML exported.'}
</script>
<template>
 <a class="skip" href="#playground">Skip to editor</a>
 <header><a class="brand" href="#"><span class="mark">i.</span> inkwell <small>for Vue</small></a><nav aria-label="Project"><a href="https://github.com/neha-pd/inkwell-vue">Source ↗</a><a href="#integration">Integration</a><span>0.1 · prototype</span></nav></header>
 <main>
  <section class="intro"><div><p class="eyebrow">A rich-text component, with room to breathe.</p><h1>Give your words<br/>a <em>place.</em></h1><p class="lede">Thoughtful editing. A familiar Vue API.<br/>Built on Tiptap and ProseMirror, ready to explore.</p></div><aside><span class="side-number">01 /</span><p>Start with a sentence.<br/>The structure can follow.</p><a href="#playground">Open the playground ↓</a></aside></section>
  <section id="playground" aria-labelledby="playground-title"><div class="section-heading"><div><p class="eyebrow">The working playground</p><h2 id="playground-title">Make yourself at home.</h2></div><span class="local-note">In this tab only · no server or AI</span></div>
  <div class="workspace"><div><InkwellEditor v-model="html" label="Draft document" :read-only="readOnly" :disabled="disabled"/><div class="editor-meta"><span>{{wordCount}} words</span><button @click="html=sample;status='Fictional sample restored.'">Restore sample</button></div></div>
   <aside class="settings"><p class="eyebrow">Component controls</p><h3>Small API.<br/>Real control.</h3><label><input type="checkbox" v-model="readOnly"/> Read only</label><p>Select and copy, without editing.</p><label><input type="checkbox" v-model="disabled"/> Disabled</label><p>Remove the editing surface from keyboard navigation.</p><div class="settings-note">Try selecting text, then applying a heading or link. Arrow keys move through the toolbar.</div><button class="export" @click="download">Export HTML ↗</button></aside>
  </div>
  <div class="output"><div class="output-top"><h3>What goes in. What comes out.</h3><button @click="copy">Copy HTML</button></div><p>The component emits HTML through <code>v-model</code>. This view is text, never executed markup.</p><pre id="html-output">{{html}}</pre><details><summary>Test an external content update</summary><label for="source">HTML source</label><textarea id="source" v-model="source" rows="5"></textarea><button @click="replace">Replace document</button><p>Unsupported tags, attributes and unsafe links are removed before editing.</p></details></div><p role="status" class="status">{{status}}</p>
  </section>
  <section id="integration" class="integration"><div><p class="eyebrow">For your next Vue interface</p><h2>A component.<br/>Not a whole new workflow.</h2><p>Import the editor, connect a string and keep ownership of your data. The repository includes a locally packable npm package. It is not yet published to the npm registry.</p><a href="https://github.com/neha-pd/inkwell-vue#use-the-package">Read the setup guide ↗</a></div><pre><code>&lt;script setup&gt;
import { ref } from 'vue'
import { InkwellEditor } from '@neha-pd/inkwell-vue'
import '@neha-pd/inkwell-vue/style.css'

const draft = ref('&lt;p&gt;Start here.&lt;/p&gt;')
&lt;/script&gt;

&lt;template&gt;
  &lt;InkwellEditor v-model="draft"
    label="Article body" /&gt;
&lt;/template&gt;</code></pre></section>
 </main><footer><div>Inkwell Vue <span>by Neha Desai</span></div><p>Early prototype · browser editing only · no collaboration or storage</p><a href="https://neha-pd.github.io/">Portfolio ↗</a></footer>
</template>
