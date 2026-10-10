# Inkwell 0.3 design references

Inspected 11 October 2026 before the final workspace revision. Reference captures are research only, excluded from the published demo and package; no third-party artwork reused.

- [Modern Writing & Documents App UI/UX Design, Md Mahade Hasan Munna](https://dribbble.com/shots/26925720-Modern-Writing-Documents-App-UI-UX-Design). Inspected the actual mobile screens in browser: document-first layout, a restrained action area beside the content, compact controls, and a strong distinction between a page and its surrounding workspace. Adopt the hierarchy and proximity of editing tools, not the blue gradient or artwork.
- [Minimalist Writing App Design, Cristian Virciu](https://www.behance.net/gallery/54099005/Minimalist-Writing-App-Design). Inspected primary project and typography/palette panel; the creator describes minimizing distractions from editing options. Adopt progressive disclosure for the document setup, and clear sans-serif product chrome with a separate writing surface. Do not claim the whole long case study was inspected.
- [Bear prototype, Anny Zhang](https://www.behance.net/gallery/55983999/Markdown-WritingApp-Design-Prototype-Bear). Primary indexed description only (direct web fetch denied). Secondary reference for separating navigation from drafting. No visual assets copied.

Design read: a working Vue editor playground for developers and writers, with a refined stationery aesthetic, warm paper/copper surfaces and a compact document-first workspace. Dials: variance6, motion2, density4. Taste-skill applies contextually to the presentation; accessibility and actual Tiptap behavior control the product UI.

Final decisions: shorten the introductory area so the real editor appears sooner; add working document-title and sample-document controls; organize the setup as a useful document inspector; retain native keyboard-accessible selects, styled consistently; use only official Phosphor icons; no fake collaboration, AI, publishing or cloud-save controls. Contextual tools require real selection and keep the range stable while keyboard focus moves. Mobile menus clamp to the viewport and offer 44px-height actions; dark/reduced-motion states preserved.

## Review refinement
The inspected document workspace references informed compact secondary controls. Stock select menus were replaced with an original shared listbox; native checkbox inputs were styled as switches, export choices use a segmented native radio group, and file inputs have a designed upload surface. Secondary file actions collapse so the inspector does not extend far below the writing canvas.
