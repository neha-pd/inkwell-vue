import type { ComponentOptionsMixin, DefineComponent } from 'vue'
export interface InkwellEditorProps { modelValue?: string; label?: string; disabled?: boolean; readOnly?: boolean }
export interface InkwellChange { html: string; text: string }
export interface InkwellEditorHandle { focus(): void; getHTML(): string }
export const InkwellEditor: DefineComponent<
 InkwellEditorProps, InkwellEditorHandle, {}, {}, {}, ComponentOptionsMixin, ComponentOptionsMixin,
 { 'update:modelValue': (html: string) => void; change: (value: InkwellChange) => void }
>
/** Browser-only sanitizer for the supported HTML subset; returns '' outside the browser. */
export function sanitizeHTML(value?: string): string
