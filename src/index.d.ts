import type { ComponentOptionsMixin, DefineComponent } from 'vue'
export interface InkwellEditorProps { modelValue?: string; label?: string; placeholder?: string; disabled?: boolean; readOnly?: boolean }
export interface InkwellChange { html: string; text: string }
export interface InkwellEditorHandle { focus(): void; getHTML(): string; getText(): string; getJSON(): Record<string,unknown>|null; getMarkdown(): string; setHTML(value: string): boolean; setMarkdown(value: string): boolean }
export const InkwellEditor: DefineComponent<InkwellEditorProps, InkwellEditorHandle, {}, {}, {}, ComponentOptionsMixin, ComponentOptionsMixin, { 'update:modelValue': (html: string) => void; change: (value: InkwellChange) => void }>
/** Browser-only supported-HTML sanitizer. Returns an empty string outside the browser. */
export function sanitizeHTML(value?: string): string
