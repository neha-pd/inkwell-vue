<script setup>
import {computed,nextTick,onBeforeUnmount,onMounted,ref,useId,watch} from 'vue'
import {PhCaretDown,PhCheck} from '@phosphor-icons/vue'
const props=defineProps({modelValue:String,label:String,options:{type:Array,required:true},disabled:Boolean})
const emit=defineEmits(['update:modelValue','before-open'])
const uid=useId(),trigger=ref(null),panel=ref(null),opened=ref(false),active=ref(0),position=ref({})
const current=computed(()=>props.options.find(o=>o.value===props.modelValue)||props.options[0])
let query='',timer
async function open(){if(props.disabled)return;emit('before-open');active.value=Math.max(0,props.options.findIndex(o=>o.value===props.modelValue));opened.value=true;await nextTick();const rect=trigger.value.getBoundingClientRect(),height=panel.value.getBoundingClientRect().height,width=Math.max(164,rect.width);position.value={left:Math.max(8,Math.min(rect.left,innerWidth-width-8))+'px',top:(rect.bottom+height+8<innerHeight?rect.bottom+6:Math.max(8,rect.top-height-6))+'px',width:width+'px'};panel.value.focus();scrollActive()}
function close(focus=false){opened.value=false;query='';if(focus)trigger.value?.focus()}
function choose(index){if(props.disabled)return;emit('update:modelValue',props.options[index].value);close();requestAnimationFrame(()=>trigger.value?.focus())}
function scrollActive(){nextTick(()=>panel.value?.querySelector('[aria-selected=true]')?.scrollIntoView({block:'nearest'}))}
function keys(event){if(['ArrowDown','ArrowUp','Home','End','Enter',' ','Escape'].includes(event.key)){event.preventDefault();if(event.key==='Escape')return close(true);if(['Enter',' '].includes(event.key))return choose(active.value);active.value=event.key==='Home'?0:event.key==='End'?props.options.length-1:(active.value+(event.key==='ArrowDown'?1:-1)+props.options.length)%props.options.length;scrollActive()}else if(event.key==='Tab'){close(true)}else if(event.key.length===1&&!event.metaKey&&!event.ctrlKey&&!event.altKey){query+=event.key.toLowerCase();clearTimeout(timer);timer=setTimeout(()=>query='',600);const i=props.options.findIndex(o=>o.label.toLowerCase().startsWith(query));if(i>=0){active.value=i;scrollActive()}}}
function outside(event){if(!trigger.value?.contains(event.target)&&!panel.value?.contains(event.target))close()}
function reposition(event){if(!panel.value?.contains(event.target))close()}
onMounted(()=>{document.addEventListener('pointerdown',outside);window.addEventListener('resize',reposition);document.addEventListener('scroll',reposition,true)})
onBeforeUnmount(()=>{clearTimeout(timer);document.removeEventListener('pointerdown',outside);window.removeEventListener('resize',reposition);document.removeEventListener('scroll',reposition,true)})
watch(()=>props.disabled,value=>{if(value)close()})
</script>
<template>
 <div class="iw-select"><span class="iw-select-label" :id="`${uid}-label`">{{label}}</span><button ref="trigger" class="iw-select-trigger" type="button" :aria-label="label" aria-haspopup="listbox" :aria-expanded="opened" :aria-controls="opened?`${uid}-options`:undefined" :disabled="disabled" @click="opened?close():open()" @keydown.down.prevent="open" @keydown.up.prevent="open"><span>{{current.label}}</span><PhCaretDown :size="13" aria-hidden="true"/></button><Teleport to="body"><div v-if="opened" :id="`${uid}-options`" ref="panel" class="iw-select-panel" role="listbox" :aria-label="label" :aria-activedescendant="`${uid}-option-${active}`" tabindex="-1" :style="position" @keydown="keys"><div v-for="(option,index) in options" :id="`${uid}-option-${index}`" :key="option.value" role="option" :aria-selected="index===active" class="iw-select-option" @pointermove="active=index" @mousedown.prevent @click="choose(index)"><span>{{option.label}}</span><PhCheck v-if="option.value===modelValue" :size="14" aria-hidden="true"/></div></div></Teleport></div>
</template>
