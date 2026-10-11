<script setup>
import { ref } from 'vue'
import InkSelect from '../src/InkSelect.vue'
import {PhDownloadSimple,PhUploadSimple,PhFloppyDisk,PhArrowCounterClockwise} from '@phosphor-icons/vue'
import { InkwellEditor, sanitizeHTML } from '../src/index.js'
const sample='<h2>A little space to think.</h2><p>The best tools make room for the work. A clear thought, a useful note, a first draft that finally gets written.</p><p>This is <strong>Inkwell</strong>: a rich-text component for Vue. Select a few words and make them <em>yours</em>.</p><ul><li><p>Write something worth keeping.</p></li><li><p>Give it a little structure.</p></li><li><p>Let the words do the rest.</p></li></ul>'
const documentTitle=ref('A little space to think'), template=ref('essay')
const samples={essay:sample,meeting:'<h2>Team working session</h2><p>A fictional sample for trying structured notes.</p><h3>Decisions</h3><ul><li><p>Keep the first release focused on one useful workflow.</p></li></ul><h3>Next steps</h3><ul data-type="taskList"><li data-type="taskItem" data-checked="false"><p>Review the draft together</p></li></ul>',brief:'<h2>Project brief</h2><p>A fictional sample. Replace these notes with your own.</p><h3>The goal</h3><p>Make the customer enquiry easier to understand and complete.</p><h3>Scope</h3><p>One responsive page, clear fields and a review step.</p><h3>Success looks like</h3><p>A working, accessible flow that the team can maintain.</p>'}
function loadTemplate(){html.value=samples[template.value];documentTitle.value={essay:'A little space to think',meeting:'Team working session',brief:'Project brief'}[template.value];status.value='Fictional sample loaded. Current unsaved content was replaced.'}
const editorRef=ref(null), exportType=ref('html'), importType=ref('html')
const html=ref(sample), readOnly=ref(false), disabled=ref(false), source=ref(sample), status=ref(''), output=ref('html')
function replace(){ html.value=sanitizeHTML(source.value);status.value='Content replaced using the component’s v-model.' }
async function copy(){try{await navigator.clipboard.writeText(sanitizeHTML(html.value));status.value='HTML copied.'}catch{status.value='Clipboard unavailable. Select and copy the HTML below.'}}
function download(){const format=exportType.value;const data=format==='markdown'?editorRef.value.getMarkdown():format==='text'?editorRef.value.getText():format==='json'?JSON.stringify(editorRef.value.getJSON(),null,2):sanitizeHTML(html.value);const ext={html:'html',markdown:'md',text:'txt',json:'json'}[format];const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type:format==='html'?'text/html':'text/plain'}));a.download=(documentTitle.value.trim().replace(/[^a-z0-9 -]/gi,'').slice(0,70)||'inkwell-document')+'.'+ext;a.click();URL.revokeObjectURL(a.href);status.value=format+' exported. Markdown does not preserve every rich-text style.'}
function saveDraft(){try{localStorage.setItem('inkwell-draft-v2',sanitizeHTML(html.value));status.value='Draft saved in this browser. Use Restore saved draft to load it.'}catch{status.value='Browser storage unavailable; export the document instead.'}}
function restoreDraft(){try{const draft=localStorage.getItem('inkwell-draft-v2');if(draft===null){status.value='No saved draft in this browser.';return}html.value=sanitizeHTML(draft);status.value='Saved draft restored.'}catch{status.value='Browser storage unavailable.'}}
function importDocument(event){const file=event.target.files?.[0];if(!file)return;if(file.size>3*1024*1024){status.value='Choose a document under 3 MB.';return}const reader=new FileReader();reader.onload=()=>{if(/\.md$/i.test(file.name)){editorRef.value.setMarkdown(reader.result)}else if(/\.html?$/i.test(file.name)){editorRef.value.setHTML(reader.result)}else if(/\.txt$/i.test(file.name)){const div=document.createElement('div');div.textContent=reader.result;editorRef.value.setHTML('<p>'+div.innerHTML.replaceAll('\n','</p><p>')+'</p>')}else{status.value='Choose .html, .md or .txt.';return}status.value='Document imported. Unsupported HTML is removed.'};reader.onerror=()=>{status.value='Could not read file.'};reader.readAsText(file);event.target.value=''}
</script>
<template>
 <a class="skip" href="#playground">Skip to editor</a>
 <header><a class="brand" href="#"><span class="mark">i.</span> inkwell <small>for Vue</small></a><nav aria-label="Project"><a href="./inkwell-vue-source.zip">Source bundle ↗</a><a href="#integration">Integration</a><a href="https://github.com/neha-pd/inkwell-vue">GitHub ↗</a></nav></header>
 <main>
  <section class="intro"><div><p class="eyebrow">THE WRITING DESK FOR VUE</p><h1>Make room<br/>for <em>good ideas.</em></h1><p class="lede">A considered place to draft, shape and refine.<br/>Rich-text editing with the simplicity of Vue.</p></div><aside><span class="writing-line">A clearer thought starts here.</span><p>Select. Refine. Keep writing.<br/>Your tools, close at hand.</p><a href="#playground">Try the editor ↗</a></aside></section>
  <section id="playground" aria-labelledby="playground-title"><div class="section-heading"><div><p class="eyebrow">The working playground</p><h2 id="playground-title">A blank page. Every possibility.</h2></div><span class="local-note">Browser editing · no server or AI</span></div>
  <div class="workspace"><div><InkwellEditor ref="editorRef" v-model="html" label="Draft document" :read-only="readOnly" :disabled="disabled"/><div class="editor-meta"><span>HTML v-model</span><button @click="html=sample;documentTitle='A little space to think';template='essay';status='Fictional sample restored.'">Restore sample</button></div></div>
   <aside class="settings"><div class="inspector-heading"><p class="eyebrow">Document inspector</p><h3>Make it yours.</h3></div>
    <label class="document-control">Document title<input aria-label="Document title" v-model="documentTitle" type="text" maxlength="100" placeholder="Untitled document"/></label>
    <div class="mode-switches"><label class="mode-switch"><span>Read only<small>Select and copy</small></span><input type="checkbox" aria-label="Read only" v-model="readOnly"/></label><label class="mode-switch"><span>Disabled<small>Pause all editing</small></span><input type="checkbox" aria-label="Disabled" v-model="disabled"/></label></div>
    <fieldset class="export-formats"><legend>Export format</legend><label v-for="[value,name] in [['html','HTML'],['markdown','Markdown'],['text','Text'],['json','JSON']]" :key="value"><input type="radio" name="export-format" :value="value" v-model="exportType"/><span>{{name}}</span></label></fieldset>
    <button class="export" @click="download"><PhDownloadSimple :size="17" aria-hidden="true"/> {{exportType==='html'?'Export HTML':'Export document'}}</button>
    <details class="sample-picker"><summary>Try a sample document</summary><InkSelect label="Sample document" v-model="template" :options="[{value:'essay',label:'A short essay'},{value:'meeting',label:'Meeting notes'},{value:'brief',label:'Project brief'}]"/><button :disabled="readOnly||disabled" @click="loadTemplate">Load sample</button><p>Replaces the current draft. Export first to keep your work.</p></details>
    <details class="file-tools"><summary>Import &amp; local drafts</summary><label class="iw-upload"><PhUploadSimple :size="17" aria-hidden="true"/> Import document<input aria-label="Import document" type="file" accept=".html,.htm,.md,.txt" :disabled="readOnly||disabled" @change="importDocument"/></label><div class="draft-actions"><button @click="saveDraft"><PhFloppyDisk :size="16" aria-hidden="true"/> Save draft locally</button><button :disabled="readOnly||disabled" @click="restoreDraft"><PhArrowCounterClockwise :size="16" aria-hidden="true"/> Restore saved draft</button></div><p>Manual, in this browser only. Imports replace the draft. Export a copy first.</p></details>
    <p class="inspector-hint">Select text for quick tools.<br/>Right-click or Shift+F10 for more.</p>
   </aside>
  </div>
  <div class="output"><div class="output-top"><h3>What goes in. What comes out.</h3><button @click="copy">Copy HTML</button></div><p>The component emits HTML through <code>v-model</code>. This view is text, never executed markup.</p><pre id="html-output">{{html}}</pre><details><summary>Test an external content update</summary><label for="source">HTML source</label><textarea id="source" v-model="source" rows="5"></textarea><button @click="replace">Replace document</button><p>Unsupported tags, attributes and unsafe links are removed before editing.</p></details></div><p role="status" class="status">{{status}}</p>
  </section>
  <section id="integration" class="integration"><div><p class="eyebrow">For your next Vue interface</p><h2>A component.<br/>Not a whole new workflow.</h2><p>Import the editor, connect a string and keep ownership of your data. Download the source or the installable package below. It is not yet published to the npm registry.</p><a href="./README.md">Read the setup guide ↗</a><p><a href="./neha-pd-inkwell-vue-0.3.1.tgz">Download npm package ↗</a></p></div><pre><code>&lt;script setup&gt;
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
