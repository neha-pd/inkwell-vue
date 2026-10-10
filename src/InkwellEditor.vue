<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, useId, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { closeHistory } from '@tiptap/pm/history'
import { TableKit } from '@tiptap/extension-table'
import { TextStyleKit } from '@tiptap/extension-text-style'
import TextAlign from '@tiptap/extension-text-align'
import Image from '@tiptap/extension-image'
import Highlight from '@tiptap/extension-highlight'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import { TaskList, TaskItem } from '@tiptap/extension-list'
import { Markdown } from '@tiptap/markdown'
import { safeLink, safeImage, sanitizeHTML } from './sanitize.js'
import { PhTextB, PhTextItalic, PhTextUnderline, PhTextStrikethrough, PhHighlighter, PhTextSubscript, PhTextSuperscript, PhTextH, PhListBullets, PhListNumbers, PhListChecks, PhQuotes, PhCode, PhCodeBlock, PhMinus, PhLink, PhImage, PhTable, PhEraser, PhArrowUUpLeft, PhArrowUUpRight } from '@phosphor-icons/vue'
import './style.css'
import InkSelect from './InkSelect.vue'
const props = defineProps({ modelValue: { type: String, default: '' }, label: { type: String, default: 'Rich text editor' }, placeholder: {type:String,default:'Start writing…'}, disabled: Boolean, readOnly: Boolean })
const emit = defineEmits(['update:modelValue', 'change'])
let applyingExternal=false
const editor = shallowRef(null), revision = ref(0), toolbar = ref(null), toolbarIndex = ref(0)
const linkOpen = ref(false), linkValue = ref(''), linkError = ref(''), linkInput = ref(null)
const imageOpen=ref(false), imageValue=ref(''), imageAlt=ref(''), imageError=ref(''), imageInput=ref(null)
const findOpen=ref(false), findValue=ref(''), replacement=ref(''), findStatus=ref(''), full=ref(false)
const root=ref(null), floating=ref(null), contextMenu=ref(null), linkPanel=ref(null)
const surface=ref(''), surfacePosition=ref({left:'12px',top:'12px'}), selectedWords=ref(0)
let savedSelection=null, surfaceAnchor=null, positionFrame=0
const icons=[PhTextB,PhTextItalic,PhTextUnderline,PhTextStrikethrough,PhHighlighter,PhTextSubscript,PhTextSuperscript,PhTextH,PhTextH,PhListBullets,PhListNumbers,PhListChecks,PhQuotes,PhCode,PhCodeBlock,PhMinus,PhLink,PhImage,PhTable,PhEraser,PhArrowUUpLeft,PhArrowUUpRight]
const quickLabels=['Bold','Italic','Underline','Highlight','Link','Clear formatting']
const id = useId(), locked = computed(() => props.disabled || props.readOnly)
const commands = [
 ['Bold', 'B', 'bold', e => e.chain().focus().toggleBold().run()],
 ['Italic', 'I', 'italic', e => e.chain().focus().toggleItalic().run()],
 ['Underline', 'U', 'underline', e => e.chain().focus().toggleUnderline().run()],
 ['Strikethrough', 'S̶', 'strike', e => e.chain().focus().toggleStrike().run()],
 ['Highlight', 'Mark', 'highlight', e => e.chain().focus().toggleHighlight({color:'#fff1a8'}).run()],
 ['Subscript', 'x₂', 'subscript', e => e.chain().focus().toggleSubscript().run()],
 ['Superscript', 'x²', 'superscript', e => e.chain().focus().toggleSuperscript().run()],
 ['Heading 2', 'H₂', ['heading', { level: 2 }], e => e.chain().focus().toggleHeading({ level: 2 }).run()],
 ['Heading 3', 'H₃', ['heading', { level: 3 }], e => e.chain().focus().toggleHeading({ level: 3 }).run()],
 ['Bullet list', '• List', 'bulletList', e => e.chain().focus().toggleBulletList().run()],
 ['Numbered list', '1. List', 'orderedList', e => e.chain().focus().toggleOrderedList().run()],
 ['Checklist', '☑ List', 'taskList', e => e.chain().focus().toggleTaskList().run()],
 ['Quote', '“ ”', 'blockquote', e => e.chain().focus().toggleBlockquote().run()],
 ['Inline code', '</>', 'code', e => e.chain().focus().toggleCode().run()],
 ['Code block', '{ }', 'codeBlock', e => e.chain().focus().toggleCodeBlock().run()],
 ['Divider', '―', null, e => e.chain().focus().setHorizontalRule().run()],
 ['Link', 'Link', 'link', openLink],
 ['Insert image', 'Image', null, openImage],
 ['Insert table', 'Table', null, e=>e.chain().focus().insertTable({rows:3,cols:3,withHeaderRow:true}).run()],
 ['Clear formatting', 'Tx', null, e=>e.chain().focus().unsetAllMarks().clearNodes().run()],
 ['Undo', '↶', null, e => e.chain().focus().undo().run()],
 ['Redo', '↷', null, e => e.chain().focus().redo().run()],
]
const tableCommands=[['Row before','addRowBefore'],['Row after','addRowAfter'],['Column before','addColumnBefore'],['Column after','addColumnAfter'],['Delete row','deleteRow'],['Delete column','deleteColumn'],['Merge cells','mergeCells'],['Split cell','splitCell'],['Header row','toggleHeaderRow'],['Header column','toggleHeaderColumn'],['Delete table','deleteTable']]
const buttons = computed(() => { revision.value; return commands.map(([label, text, mark, run],index) => ({ label, text, run, icon:icons[index], pressed: mark && !!editor.value?.isActive(...(Array.isArray(mark) ? mark : [mark])) })) })
const quickButtons=computed(()=>buttons.value.filter(button=>quickLabels.includes(button.label)))
const stats=computed(()=>{revision.value;return {words:editor.value?.storage.characterCount.words()||0,characters:editor.value?.storage.characterCount.characters()||0}})
const inTable=computed(()=>{revision.value;return editor.value?.isActive('table')})
const block=computed(()=>{revision.value;const level=editor.value?.getAttributes('heading').level;return level ? `h${level}`:'p'})
const font=computed(()=>{revision.value;return editor.value?.getAttributes('textStyle').fontFamily||'serif'})
const fontSize=computed(()=>{revision.value;return editor.value?.getAttributes('textStyle').fontSize||'18px'})
function styleValue(kind,value){if(locked.value||!editor.value)return;restoreSelection();const chain=editor.value.chain().focus();if(kind==='block'){value==='p'?chain.setParagraph().run():chain.setHeading({level:Number(value.slice(1))}).run()}else if(kind==='font')chain.setFontFamily(value).run();else if(kind==='size')chain.setFontSize(value).run();else chain.setTextAlign(value).run()}
const align=computed(()=>{revision.value;return editor.value?.getAttributes(editor.value?.isActive('heading')?'heading':'paragraph').textAlign||'left'})
const extensions=()=>[StarterKit.configure({heading:{levels:[1,2,3,4,5,6]},link:{openOnClick:false,autolink:false,linkOnPaste:false,HTMLAttributes:{target:null,rel:'noopener noreferrer'}}}),TableKit,TextStyleKit,TextAlign.configure({types:['heading','paragraph']}),Image.configure({allowBase64:true}),Highlight.configure({multicolor:true}),Subscript,Superscript,TaskList,TaskItem.configure({nested:true}),Placeholder.configure({placeholder:props.placeholder}),CharacterCount,Markdown]
const attrs=()=>({role:'textbox','aria-label':props.label,'aria-multiline':'true','aria-readonly':String(locked.value),'aria-disabled':String(props.disabled),tabindex:props.disabled?'-1':'0'})
onMounted(() => { document.addEventListener('pointerdown',outsideSurface);window.addEventListener('resize',dismissSurfaces);document.addEventListener('scroll',scrollSurface,true); editor.value = new Editor({extensions:extensions(),content:sanitizeHTML(props.modelValue),editable:!locked.value,editorProps:{attributes:attrs(),transformPastedHTML:sanitizeHTML},onTransaction:()=>{revision.value++;syncSelection()},onFocus:syncSelection,onBlur:()=>nextTick(()=>{if(!root.value?.contains(document.activeElement)&&surface.value==='selection')surface.value=''}),onUpdate:({editor:current})=>{if(applyingExternal)return;const html=sanitizeHTML(current.getHTML());emit('update:modelValue',html);emit('change',{html,text:current.getText()})}}) })
watch(()=>props.modelValue,value=>{const clean=sanitizeHTML(value);if(editor.value && clean!==sanitizeHTML(editor.value.getHTML())){dismissSurfaces();savedSelection=null;applyingExternal=true;try{editor.value.view.dispatch(closeHistory(editor.value.state.tr));editor.value.commands.setContent(clean,{emitUpdate:false});editor.value.view.dispatch(closeHistory(editor.value.state.tr))}finally{applyingExternal=false}}})
watch([locked,()=>props.disabled,()=>props.label],()=>{if(!editor.value)return;editor.value.setEditable(!locked.value,false);editor.value.setOptions({editorProps:{attributes:attrs()}});if(locked.value){dismissSurfaces();imageOpen.value=false;findOpen.value=false}})
onBeforeUnmount(()=>{editor.value?.destroy();document.removeEventListener('pointerdown',outsideSurface);window.removeEventListener('resize',dismissSurfaces);document.removeEventListener('scroll',scrollSurface,true);cancelAnimationFrame(positionFrame)})
function toolbarKeys(event){if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;event.preventDefault();toolbarIndex.value=event.key==='Home'?0:event.key==='End'?commands.length-1:(toolbarIndex.value+(event.key==='ArrowRight'?1:-1)+commands.length)%commands.length;toolbar.value.querySelectorAll('button')[toolbarIndex.value].focus()}
// Retain the ProseMirror range while focus moves into a menu or link field.
function rememberSelection(){if(editor.value){const {from,to}=editor.value.state.selection;savedSelection={from,to}}}
function restoreSelection(){if(!locked.value&&editor.value&&savedSelection)editor.value.commands.setTextSelection(savedSelection)}
function selectionAnchor(){const e=editor.value;if(!e)return {left:12,top:12,bottom:40};const {from,to}=e.state.selection;const a=e.view.coordsAtPos(from),b=e.view.coordsAtPos(to);return {left:(a.left+b.right)/2,top:Math.min(a.top,b.top),bottom:Math.max(a.bottom,b.bottom)}}
async function placeSurface(anchor=surfaceAnchor){if(!anchor)return;surfaceAnchor=anchor;await nextTick();const panel=linkOpen.value?linkPanel.value:surface.value==='context'?contextMenu.value:floating.value;if(!panel)return;const rect=panel.getBoundingClientRect(),pad=12;let left=surface.value==='context'?anchor.left:anchor.left-rect.width/2;let top=anchor.top-rect.height-10;if(surface.value==='context'||top<pad)top=anchor.bottom+10;surfacePosition.value={left:Math.max(pad,Math.min(left,window.innerWidth-rect.width-pad))+'px',top:Math.max(pad,Math.min(top,window.innerHeight-rect.height-pad))+'px'}}
function syncSelection(){if(!editor.value||locked.value)return;const e=editor.value;const {from,to,empty}=e.state.selection;selectedWords.value=e.state.doc.textBetween(from,to,' ').trim().split(/\s+/).filter(Boolean).length;if(surface.value==='context'||linkOpen.value)return;if(empty)savedSelection=null;if(empty||!e.isFocused||imageOpen.value||findOpen.value){surface.value='';return}savedSelection={from,to};surface.value='selection';cancelAnimationFrame(positionFrame);positionFrame=requestAnimationFrame(()=>placeSurface(selectionAnchor()))}
function dismissSurfaces(){surface.value='';linkOpen.value=false;surfaceAnchor=null}
function outsideSurface(event){if(event.target.closest?.('.inkwell-popover'))return;if(linkOpen.value||surface.value==='context')dismissSurfaces();else if(!root.value?.contains(event.target))surface.value=''}
function scrollSurface(event){if(event.target?.closest?.('.inkwell-popover'))return;if(surface.value==='selection'){cancelAnimationFrame(positionFrame);positionFrame=requestAnimationFrame(()=>placeSurface(selectionAnchor()))}else dismissSurfaces()}
function runCommand(button,preserve=false){if(locked.value||!editor.value)return;if(preserve)restoreSelection();if(button.label!=='Link')surface.value='';button.run(editor.value)}
async function openContext(event){if(locked.value||!editor.value||!event.target.closest('.inkwell-content'))return;event.preventDefault();rememberSelection();linkOpen.value=false;surface.value='context';const keyboard=event.type==='keydown';const anchor=keyboard?selectionAnchor():{left:event.clientX,top:event.clientY,bottom:event.clientY};await placeSurface(anchor);await new Promise(requestAnimationFrame);contextMenu.value?.querySelector('button')?.focus()}
function surfaceKeys(event){if(event.key==='Escape'&&(surface.value||linkOpen.value)){event.preventDefault();event.stopPropagation();closeLink();return}if((event.key==='F10'&&event.shiftKey)||event.key==='ContextMenu')openContext(event)}
function menuKeys(event){if(event.key==='Tab'){dismissSurfaces();return}if(!['ArrowDown','ArrowUp','Home','End'].includes(event.key))return;event.preventDefault();const items=[...contextMenu.value.querySelectorAll('button')];const index=items.indexOf(document.activeElement);items[event.key==='Home'?0:event.key==='End'?items.length-1:(index+(event.key==='ArrowDown'?1:-1)+items.length)%items.length]?.focus()}
async function openLink(){if(locked.value||!editor.value)return;rememberSelection();linkValue.value=editor.value.getAttributes('link').href||'';linkError.value='';surface.value='';linkOpen.value=true;imageOpen.value=false;await placeSurface(selectionAnchor());linkInput.value?.focus()}
function closeLink(){dismissSurfaces();restoreSelection();if(!props.disabled)editor.value?.commands.focus();surface.value=''}
function saveLink(){if(locked.value||!editor.value)return;const href=safeLink(linkValue.value);if(!href){linkError.value='Enter a full https://, http:// or mailto: address.';placeSurface();return}restoreSelection();editor.value.chain().focus().extendMarkRange('link').setLink({href}).run();dismissSurfaces()}
function removeLink(){if(locked.value||!editor.value)return;restoreSelection();editor.value.chain().focus().extendMarkRange('link').unsetLink().run();dismissSurfaces()}
async function openImage(){dismissSurfaces();imageOpen.value=true;linkOpen.value=false;imageValue.value='';imageAlt.value='';imageError.value='';await nextTick();imageInput.value.focus()}
function insertImage(){const src=safeImage(imageValue.value);if(!src){imageError.value='Use an HTTPS image URL or choose a PNG, JPEG, WebP or GIF under 2 MB.';return}if(!imageAlt.value.trim()){imageError.value='Add a description for people who cannot see the image.';return}editor.value.chain().focus().setImage({src,alt:imageAlt.value.trim()}).run();imageOpen.value=false}
function loadImage(event){const file=event.target.files?.[0];if(!file)return;if(file.size>2*1024*1024||!['image/png','image/jpeg','image/webp','image/gif'].includes(file.type)){imageError.value='Choose a PNG, JPEG, WebP or GIF under 2 MB.';return}const reader=new FileReader();reader.onload=()=>{imageValue.value=reader.result;imageError.value=''};reader.readAsDataURL(file)}
function setBlock(value){const chain=editor.value.chain().focus();value==='p'?chain.setParagraph().run():chain.setHeading({level:Number(value.slice(1))}).run()}
function matchRanges(){const term=findValue.value;if(!term)return[];const matches=[];editor.value.state.doc.descendants((node,pos)=>{if(!node.isText)return;let start=0;while(start<=node.text.length-term.length){const at=node.text.toLocaleLowerCase().indexOf(term.toLocaleLowerCase(),start);if(at<0)break;matches.push({from:pos+at,to:pos+at+term.length});start=at+term.length}});return matches}
function findNext(){const ranges=matchRanges();if(!ranges.length){findStatus.value='No matches.';return}const next=ranges.find(r=>r.from>=editor.value.state.selection.to)||ranges[0];editor.value.chain().focus().setTextSelection(next).run();findStatus.value=`${ranges.length} matches. Selected ${ranges.indexOf(next)+1}.`}
function replaceAll(){if(locked.value)return;const ranges=matchRanges();if(!ranges.length){findStatus.value='No matches.';return}let tr=closeHistory(editor.value.state.tr);for(const range of ranges.reverse()){tr=replacement.value?tr.insertText(replacement.value,range.from,range.to):tr.delete(range.from,range.to)}editor.value.view.dispatch(tr);editor.value.view.dispatch(closeHistory(editor.value.state.tr));findStatus.value=`Replaced ${ranges.length} matches. Undo restores them.`}
function focusKeys(event){if(!full.value||event.defaultPrevented)return;if(event.key==='Escape'&&!linkOpen.value&&!imageOpen.value&&!findOpen.value){full.value=false;return}if(event.key!=='Tab')return;const all=[...root.value.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),[contenteditable=true],[tabindex="0"]')].filter(el=>el.tabIndex>=0&&el.getClientRects().length);if(!all.length)return;const first=all[0],last=all[all.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus()}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus()}}
function getHTML(){return sanitizeHTML(editor.value?.getHTML()||'')}
function setHTML(value){if(locked.value||!editor.value)return false;applyingExternal=true;let result;try{editor.value.view.dispatch(closeHistory(editor.value.state.tr));result=editor.value.commands.setContent(sanitizeHTML(value),{emitUpdate:false});editor.value.view.dispatch(closeHistory(editor.value.state.tr))}finally{applyingExternal=false}const html=getHTML();emit('update:modelValue',html);emit('change',{html,text:editor.value.getText()});return result}
function setMarkdown(value){if(locked.value||!editor.value)return false;const temp=new Editor({extensions:extensions(),content:String(value),contentType:'markdown'});const html=sanitizeHTML(temp.getHTML());temp.destroy();return setHTML(html)}
defineExpose({focus:()=>{if(!props.disabled)editor.value?.commands.focus()},getHTML,getText:()=>editor.value?.getText()||'',getJSON:()=>editor.value?.getJSON()||null,getMarkdown:()=>editor.value?.getMarkdown()||'',setHTML,setMarkdown})
</script>
<template>
 <div ref="root" class="inkwell" @keydown="surfaceKeys($event);focusKeys($event)" @contextmenu="openContext" :class="{'inkwell-disabled':disabled,'inkwell-fullscreen':full}">
  <div class="inkwell-documentbar"><span>{{label}}</span><div><button type="button" :disabled="disabled" @click="findOpen=!findOpen">Find &amp; replace</button><button type="button" :aria-pressed="full" @click="full=!full">{{full?'Exit focus mode':'Focus mode'}}</button></div></div>
  <div class="inkwell-options">
   <InkSelect label="Structure" :model-value="block" :disabled="locked||!editor" :options="[{value:'p',label:'Paragraph'},...[1,2,3,4,5,6].map(n=>({value:`h${n}`,label:`Heading ${n}`}))]" @before-open="rememberSelection" @update:model-value="styleValue('block',$event)"/>
   <InkSelect label="Font" :model-value="font" :disabled="locked||!editor" :options="[{value:'serif',label:'Serif'},{value:'sans-serif',label:'Sans serif'},{value:'monospace',label:'Monospace'}]" @before-open="rememberSelection" @update:model-value="styleValue('font',$event)"/>
   <InkSelect label="Size" :model-value="fontSize" :disabled="locked||!editor" :options="[12,14,16,18,20,24,32,48].map(n=>({value:`${n}px`,label:`${n} px`}))" @before-open="rememberSelection" @update:model-value="styleValue('size',$event)"/>
   <InkSelect label="Align" :model-value="align" :disabled="locked||!editor" :options="['left','center','right','justify'].map(a=>({value:a,label:a[0].toUpperCase()+a.slice(1)}))" @before-open="rememberSelection" @update:model-value="styleValue('align',$event)"/>
   <label>Text color <input aria-label="Text color" type="color" value="#272b38" :disabled="locked||!editor" @input="editor.chain().focus().setColor($event.target.value).run()"/></label>
  </div>
  <div ref="toolbar" role="toolbar" :aria-label="`${label} formatting`" class="inkwell-toolbar" @keydown="toolbarKeys"><button v-for="(button,index) in buttons" :key="button.label" type="button" :aria-label="button.label" :title="button.label" :aria-pressed="button.pressed===null?undefined:button.pressed" :disabled="locked||!editor" :tabindex="index===toolbarIndex?0:-1" @focus="toolbarIndex=index" @mousedown.prevent @click="runCommand(button)"><component :is="button.icon" :size="18" weight="regular" aria-hidden="true"/><span v-if="button.label==='Heading 2'||button.label==='Heading 3'" class="inkwell-icon-sub">{{button.label.slice(-1)}}</span></button></div>
  <div v-if="inTable" class="inkwell-tablebar" aria-label="Table controls"><span>Table</span><button v-for="[title,command] in tableCommands" :key="command" type="button" :disabled="locked||!editor.can()[command]()" @mousedown.prevent @click="editor.chain().focus()[command]().run()">{{title}}</button></div>
  <form v-if="linkOpen" ref="linkPanel" :style="surfacePosition" class="inkwell-link inkwell-popover inkwell-link-popover" aria-label="Edit link" @submit.prevent="saveLink" @keydown.esc.prevent="closeLink"><label :for="`${id}-link`">Link address</label><input :id="`${id}-link`" ref="linkInput" v-model="linkValue" type="text" placeholder="https://example.com" :aria-invalid="!!linkError" :aria-describedby="linkError?`${id}-error`:undefined"/><button type="submit">Apply link</button><button type="button" @click="removeLink">Remove link</button><button type="button" @click="closeLink">Cancel</button><p v-if="linkError" :id="`${id}-error`" role="alert">{{linkError}}</p></form>
  <form v-if="imageOpen" class="inkwell-link" aria-label="Insert image" @submit.prevent="insertImage" @keydown.esc.prevent="imageOpen=false;editor.commands.focus()"><label :for="`${id}-image`">Image URL</label><input :id="`${id}-image`" ref="imageInput" v-model="imageValue" placeholder="https://…"/><label class="iw-upload">Choose a local image<input :id="`${id}-file`" aria-label="Or local image" type="file" accept="image/png,image/jpeg,image/webp,image/gif" @change="loadImage"/></label><label :for="`${id}-alt`">Image description</label><input :id="`${id}-alt`" v-model="imageAlt"/><button type="submit">Add image</button><button type="button" @click="imageOpen=false;editor.commands.focus()">Cancel</button><p v-if="imageError" role="alert">{{imageError}}</p></form>
  <form v-if="findOpen" class="inkwell-link" aria-label="Find and replace" @submit.prevent="findNext" @keydown.esc.prevent="findOpen=false;editor.commands.focus()"><label :for="`${id}-find`">Find text</label><input :id="`${id}-find`" v-model="findValue"/><label :for="`${id}-replace`">Replace with</label><input :id="`${id}-replace`" v-model="replacement" :disabled="locked"/><button type="submit">Find next</button><button type="button" :disabled="locked" @click="replaceAll">Replace all</button><button type="button" @click="findOpen=false;editor.commands.focus()">Close search</button><p role="status">{{findStatus}} Matches are case-insensitive within each formatted text span.</p></form>
  <div v-if="surface==='selection'&&!locked" ref="floating" class="inkwell-popover inkwell-floating" :style="surfacePosition" role="toolbar" aria-label="Selection formatting">
   <span class="inkwell-selection-count">{{selectedWords}} {{selectedWords===1?'word':'words'}}</span><button v-for="button in quickButtons" :key="button.label" type="button" :aria-label="`Selection ${button.label.toLowerCase()}`" :title="button.label" :aria-pressed="button.pressed===null?undefined:button.pressed" @mousedown.prevent @click="runCommand(button,true)"><component :is="button.icon" :size="18" weight="regular" aria-hidden="true"/></button>
  </div>
  <div v-if="surface==='context'&&!locked" ref="contextMenu" class="inkwell-popover inkwell-context" :style="surfacePosition" role="menu" aria-label="Text editing" @keydown="menuKeys">
   <p>{{selectedWords?`${selectedWords} selected words`:'At your cursor'}}</p><button v-for="button in quickButtons" :key="button.label" type="button" :aria-label="button.label" :role="button.pressed===null?'menuitem':'menuitemcheckbox'" :aria-checked="button.pressed===null?undefined:!!button.pressed" @mousedown.prevent @click="runCommand(button,true)"><component :is="button.icon" :size="18" weight="regular" aria-hidden="true"/><span>{{button.label}}</span><kbd aria-hidden="true" v-if="['Bold','Italic','Underline'].includes(button.label)">{{button.label.slice(0,1)}}</kbd></button><span class="inkwell-menu-hint">Esc to dismiss · ↑ ↓ to navigate</span>
  </div>
  <EditorContent :editor="editor" class="inkwell-content"/>
  <p v-if="!editor" class="inkwell-loading">Preparing editor…</p>
  <div class="inkwell-footer"><span>{{disabled?'Disabled':readOnly?'Read only · select and copy':'Select text for quick tools · Shift+F10 for menu'}}</span><span>{{stats.words}} words · {{stats.characters}} characters</span></div>
 </div>
</template>
