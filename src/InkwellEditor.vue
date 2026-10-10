<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, useId, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { safeLink, sanitizeHTML } from './sanitize.js'
import './style.css'
const props = defineProps({ modelValue: { type: String, default: '' }, label: { type: String, default: 'Rich text editor' }, disabled: Boolean, readOnly: Boolean })
const emit = defineEmits(['update:modelValue', 'change'])
const editor = shallowRef(null), revision = ref(0), toolbar = ref(null), toolbarIndex = ref(0)
const linkOpen = ref(false), linkValue = ref(''), linkError = ref(''), linkInput = ref(null)
const id = useId(), locked = computed(() => props.disabled || props.readOnly)
const commands = [
 ['Bold', 'B', 'bold', e => e.chain().focus().toggleBold().run()],
 ['Italic', 'I', 'italic', e => e.chain().focus().toggleItalic().run()],
 ['Heading 2', 'H₂', ['heading', { level: 2 }], e => e.chain().focus().toggleHeading({ level: 2 }).run()],
 ['Heading 3', 'H₃', ['heading', { level: 3 }], e => e.chain().focus().toggleHeading({ level: 3 }).run()],
 ['Bullet list', '• List', 'bulletList', e => e.chain().focus().toggleBulletList().run()],
 ['Numbered list', '1. List', 'orderedList', e => e.chain().focus().toggleOrderedList().run()],
 ['Link', 'Link', 'link', openLink],
 ['Undo', '↶', null, e => e.chain().focus().undo().run()],
 ['Redo', '↷', null, e => e.chain().focus().redo().run()],
]
const buttons = computed(() => { revision.value; return commands.map(([label, text, mark, run]) => ({ label, text, run, pressed: mark && !!editor.value?.isActive(...(Array.isArray(mark) ? mark : [mark])) })) })
onMounted(() => {
 editor.value = new Editor({
  extensions: [StarterKit.configure({ heading: { levels: [2,3] }, blockquote: false, code: false, codeBlock: false, horizontalRule: false, strike: false, underline: false, link: { openOnClick: false, autolink: false, linkOnPaste: false, HTMLAttributes: { target: null, rel: 'noopener noreferrer' } } })],
  content: sanitizeHTML(props.modelValue), editable: !locked.value,
  editorProps: { attributes: { role: 'textbox', 'aria-label': props.label, 'aria-multiline': 'true', 'aria-readonly': String(locked.value), 'aria-disabled': String(props.disabled), tabindex: props.disabled ? '-1' : '0' }, transformPastedHTML: sanitizeHTML },
  onTransaction: () => { revision.value++ },
  onUpdate: ({ editor: current }) => { const html = sanitizeHTML(current.getHTML()); emit('update:modelValue', html); emit('change', { html, text: current.getText() }) },
 })
})
watch(() => props.modelValue, value => {
 const clean = sanitizeHTML(value)
 if (editor.value && clean !== sanitizeHTML(editor.value.getHTML())) editor.value.commands.setContent(clean, { emitUpdate: false })
})
watch([locked, () => props.disabled, () => props.label], () => {
 if (!editor.value) return
 editor.value.setEditable(!locked.value, false)
 editor.value.setOptions({ editorProps: { attributes: { role: 'textbox', 'aria-label': props.label, 'aria-multiline': 'true', 'aria-readonly': String(locked.value), 'aria-disabled': String(props.disabled), tabindex: props.disabled ? '-1' : '0' } } })
 if (locked.value) linkOpen.value = false
})
onBeforeUnmount(() => editor.value?.destroy())
function toolbarKeys(event) {
 if (!['ArrowRight','ArrowLeft','Home','End'].includes(event.key)) return
 event.preventDefault()
 toolbarIndex.value = event.key === 'Home' ? 0 : event.key === 'End' ? commands.length - 1 : (toolbarIndex.value + (event.key === 'ArrowRight' ? 1 : -1) + commands.length) % commands.length
 toolbar.value.querySelectorAll('button')[toolbarIndex.value].focus()
}
async function openLink() { linkValue.value = editor.value.getAttributes('link').href || ''; linkError.value = ''; linkOpen.value = true; await nextTick(); linkInput.value.focus() }
function closeLink() { linkOpen.value = false; editor.value?.commands.focus() }
function saveLink() {
 const href = safeLink(linkValue.value)
 if (!href) { linkError.value = 'Enter a full https://, http:// or mailto: address.'; return }
 editor.value.chain().focus().extendMarkRange('link').setLink({ href }).run(); linkOpen.value = false
}
function removeLink() { editor.value.chain().focus().extendMarkRange('link').unsetLink().run(); linkOpen.value = false }
defineExpose({ focus: () => { if (!props.disabled) editor.value?.commands.focus() }, getHTML: () => sanitizeHTML(editor.value?.getHTML() || '') })
</script>
<template>
 <div class="inkwell" :class="{ 'inkwell-disabled': disabled }">
  <div ref="toolbar" role="toolbar" :aria-label="`${label} formatting`" class="inkwell-toolbar" @keydown="toolbarKeys">
   <button v-for="(button, index) in buttons" :key="button.label" type="button" :aria-label="button.label" :title="button.label" :aria-pressed="button.pressed === null ? undefined : button.pressed" :disabled="locked || !editor" :tabindex="index === toolbarIndex ? 0 : -1" @focus="toolbarIndex = index" @mousedown.prevent @click="button.run(editor)">{{ button.text }}</button>
  </div>
  <form v-if="linkOpen" class="inkwell-link" aria-label="Edit link" @submit.prevent="saveLink" @keydown.esc.prevent="closeLink">
   <label :for="`${id}-link`">Link address</label><input :id="`${id}-link`" ref="linkInput" v-model="linkValue" type="text" placeholder="https://example.com" :aria-invalid="!!linkError" :aria-describedby="linkError ? `${id}-error` : undefined"/>
   <button type="submit">Apply link</button><button type="button" @click="removeLink">Remove link</button><button type="button" @click="closeLink">Cancel</button>
   <p v-if="linkError" :id="`${id}-error`" role="alert">{{ linkError }}</p>
  </form>
  <EditorContent :editor="editor" class="inkwell-content"/>
  <p v-if="!editor" class="inkwell-loading">Preparing editor…</p>
  <div class="inkwell-footer"><span>{{ disabled ? 'Disabled' : readOnly ? 'Read only · select and copy' : 'Select text to format · ⌘/Ctrl+B or I' }}</span><span>Tiptap + ProseMirror</span></div>
 </div>
</template>
