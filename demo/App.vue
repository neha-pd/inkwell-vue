<script setup>
import { ref } from 'vue'
import { InkwellEditor, sanitizeHTML } from '../src/index.js'
const sample='<h2>A little space to think.</h2><p>The best tools make room for the work. A clear thought, a useful note, a first draft that finally gets written.</p><p>This is <strong>Inkwell</strong>: a rich-text component for Vue. Select a few words and make them <em>yours</em>.</p><ul><li><p>Write something worth keeping.</p></li><li><p>Give it a little structure.</p></li><li><p>Let the words do the rest.</p></li></ul>'
const editorRef=ref(null), exportType=ref('html'), importType=ref('html')
const html=ref(sample), readOnly=ref(false), disabled=ref(false), source=ref(sample), status=ref(''), output=ref('html')
function replace(){ html.value=sanitizeHTML(source.value);status.value='Content replaced using the component’s v-model.' }
async function copy(){try{await navigator.clipboard.writeText(sanitizeHTML(html.value));status.value='HTML copied.'}catch{status.value='Clipboard unavailable. Select and copy the HTML below.'}}
function download(){const format=exportType.value;const data=format==='markdown'?editorRef.value.getMarkdown():format==='text'?editorRef.value.getText():format==='json'?JSON.stringify(editorRef.value.getJSON(),null,2):sanitizeHTML(html.value);const ext={html:'html',markdown:'md',text:'txt',json:'json'}[format];const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type:format==='html'?'text/html':'text/plain'}));a.download='inkwell-document.'+ext;a.click();URL.revokeObjectURL(a.href);status.value=format+' exported. Markdown does not preserve every rich-text style.'}
function saveDraft(){try{localStorage.setItem('inkwell-draft-v2',sanitizeHTML(html.value));status.value='Draft saved in this browser. Use Restore saved draft to load it.'}catch{status.value='Browser storage unavailable; export the document instead.'}}
function restoreDraft(){try{const draft=localStorage.getItem('inkwell-draft-v2');if(draft===null){status.value='No saved draft in this browser.';return}html.value=sanitizeHTML(draft);status.value='Saved draft restored.'}catch{status.value='Browser storage unavailable.'}}
function importDocument(event){const file=event.target.files?.[0];if(!file)return;if(file.size>3*1024*1024){status.value='Choose a document under 3 MB.';return}const reader=new FileReader();reader.onload=()=>{if(/\.md$/i.test(file.name)){editorRef.value.setMarkdown(reader.result)}else if(/\.html?$/i.test(file.name)){editorRef.value.setHTML(reader.result)}else if(/\.txt$/i.test(file.name)){const div=document.createElement('div');div.textContent=reader.result;editorRef.value.setHTML('<p>'+div.innerHTML.replaceAll('\n','</p><p>')+'</p>')}else{status.value='Choose .html, .md or .txt.';return}status.value='Document imported. Unsupported HTML is removed.'};reader.onerror=()=>{status.value='Could not read file.'};reader.readAsText(file);event.target.value=''}
</script>
<template>
 <a class="skip" href="#playground">Skip to editor</a>
 <header><a class="brand" href="#"><span class="mark">i.</span> inkwell <small>for Vue</small></a><nav aria-label="Project"><a href="./inkwell-vue-source.zip">Source bundle ↗</a><a href="#integration">Integration</a><span>0.2 · preview</span></nav></header>
 <main>
  <section class="intro"><div><p class="eyebrow">A rich-text component, with room to breathe.</p><h1>Give your words<br/>a <em>place.</em></h1><p class="lede">Thoughtful editing. A familiar Vue API.<br/>Built on Tiptap and ProseMirror, ready to explore.</p></div><aside><span class="side-number">01 /</span><p>Start with a sentence.<br/>The structure can follow.</p><a href="#playground">Open the playground ↓</a></aside></section>
  <section id="playground" aria-labelledby="playground-title"><div class="section-heading"><div><p class="eyebrow">The working playground</p><h2 id="playground-title">Make yourself at home.</h2></div><span class="local-note">Browser editing · no server or AI</span></div>
  <div class="workspace"><div><InkwellEditor ref="editorRef" v-model="html" label="Draft document" :read-only="readOnly" :disabled="disabled"/><div class="editor-meta"><span>HTML v-model</span><button @click="html=sample;status='Fictional sample restored.'">Restore sample</button></div></div>
   <aside class="settings"><p class="eyebrow">Component controls</p><h3>Small API.<br/>Real control.</h3><label><input type="checkbox" v-model="readOnly"/> Read only</label><p>Select and copy, without editing.</p><label><input type="checkbox" v-model="disabled"/> Disabled</label><p>Remove the editing surface from keyboard navigation.</p><div class="settings-note">Try selecting text, then applying a heading or link. Arrow keys move through the toolbar.</div><label class="document-control">Export format<select aria-label="Export format" v-model="exportType"><option value="html">HTML</option><option value="markdown">Markdown</option><option value="text">Plain text</option><option value="json">Tiptap JSON</option></select></label><button class="export" @click="download">{{exportType==='html'?'Export HTML':'Export document'}} ↗</button><label class="document-control">Import document<input type="file" accept=".html,.htm,.md,.txt" :disabled="readOnly||disabled" @change="importDocument"/></label><button @click="saveDraft">Save draft locally</button><button :disabled="readOnly||disabled" @click="restoreDraft">Restore saved draft</button><p>Saving is manual, in this browser only. Imported files replace the current document. Export a copy first.</p></aside>
  </div>
  <div class="output"><div class="output-top"><h3>What goes in. What comes out.</h3><button @click="copy">Copy HTML</button></div><p>The component emits HTML through <code>v-model</code>. This view is text, never executed markup.</p><pre id="html-output">{{html}}</pre><details><summary>Test an external content update</summary><label for="source">HTML source</label><textarea id="source" v-model="source" rows="5"></textarea><button @click="replace">Replace document</button><p>Unsupported tags, attributes and unsafe links are removed before editing.</p></details></div><p role="status" class="status">{{status}}</p>
  </section>
  <section id="integration" class="integration"><div><p class="eyebrow">For your next Vue interface</p><h2>A component.<br/>Not a whole new workflow.</h2><p>Import the editor, connect a string and keep ownership of your data. Download the source or the installable package below. It is not yet published to the npm registry.</p><a href="./README.md">Read the setup guide ↗</a><p><a href="./neha-pd-inkwell-vue-0.2.0.tgz">Download npm package ↗</a></p></div><pre><code>&lt;script setup&gt;
import { ref } from 'vue'
import { InkwellEditor } from '@neha-pd/inkwell-vue'
import '@neha-pd/inkwell-vue/style.css'

const draft = ref('&lt;p&gt;Start here.&lt;/p&gt;')
&lt;/script&gt;

&lt;template&gt;
  &lt;InkwellEditor v-model="draft"
    label="Article body" /&gt;
&lt;/template&gt;</code></pre></section>
 </main><footer><div>Inkwell Vue <span>by Neha Desai</span></div><p>Preview · single-user editing · optional browser-local draft</p><a href="https://neha-desai.de5.net/">Portfolio ↗</a></footer>
</template>
