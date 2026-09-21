---
name: Editorial Craft
colors:
  surface: '#fbf9f9'
  surface-dim: '#dbdad9'
  surface-bright: '#fbf9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f3'
  surface-container: '#efeded'
  surface-container-high: '#e9e8e7'
  surface-container-highest: '#e3e2e2'
  on-surface: '#1b1c1c'
  on-surface-variant: '#55433c'
  inverse-surface: '#303031'
  inverse-on-surface: '#f2f0f0'
  outline: '#88726b'
  outline-variant: '#dbc1b8'
  surface-tint: '#974724'
  primary: '#944522'
  on-primary: '#ffffff'
  primary-container: '#b35d38'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb598'
  secondary: '#605e5c'
  on-secondary: '#ffffff'
  secondary-container: '#e6e2df'
  on-secondary-container: '#666462'
  tertiary: '#38654d'
  on-tertiary: '#ffffff'
  tertiary-container: '#507e65'
  on-tertiary-container: '#f6fff6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbce'
  primary-fixed-dim: '#ffb598'
  on-primary-fixed: '#370e00'
  on-primary-fixed-variant: '#79310f'
  secondary-fixed: '#e6e2df'
  secondary-fixed-dim: '#cac6c4'
  on-secondary-fixed: '#1c1b1a'
  on-secondary-fixed-variant: '#484645'
  tertiary-fixed: '#bceecf'
  tertiary-fixed-dim: '#a1d1b4'
  on-tertiary-fixed: '#002112'
  on-tertiary-fixed-variant: '#224f39'
  background: '#fbf9f9'
  on-background: '#1b1c1c'
  surface-variant: '#e3e2e2'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 52px
    fontWeight: '600'
    lineHeight: 60px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 38px
    fontWeight: '600'
    lineHeight: 46px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Playfair Display
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 30px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: 0em
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: -0.01em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 3rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system establishes an intellectual, highly crafted aesthetic tailored for autonomous technical publishing. It bridges the gap between the structured precision of modern developer tooling (Linear, Stripe) and the quiet prestige of heritage publishing (Stripe Press, New York Times, Substack). 

The visual personality reflects quiet confidence, intellectual rigor, and editorial authority. It deliberately eschews high-saturation AI clichés—such as synthetic neon gradients, glassmorphic glows, and floating spark motifs—in favor of physical print metaphors: tactile warm paper stocks, razor-sharp hairline borders, disciplined typographic pacing, and restrained, intentional motion.

Key characteristics:
- **Tone:** Academic yet pragmatic, modern yet timeless, dependable, uncompromisingly legible.
- **Visual Style:** Refined Minimalist Editorial with high-density utility controls. Surfaces emulate heavy archival paper, paired with stark 1px architectural lines.
- **Audience:** Senior software engineers, engineering leaders, technical founders, and serious technical authors who demand developer ergonomics and publication-ready typography.

## Colors

The palette is rooted in print heritage and developer ergonomics, balanced around a warm canvas rather than sterile optical white.

- **Canvas & Surfaces:**
  - Base Canvas (`#F7F5F0`): Warm archival ivory base tone.
  - Surface Raised (`#FCFBF9`): Premium off-white for cards, drawers, and panels to create low-frequency separation without elevation blur.
  - Code Surface (`#1C1B1A`): Deep matte charcoal for syntax blocks, terminal telemetry, and code editors.
- **Text & Hierarchy:**
  - Primary Text (`#171717`): Deep warm charcoal offering high contrast while avoiding the harshness of pure black.
  - Secondary Text (`#737373`): Balanced warm gray for metadata, structural timestamps, and labels.
  - Muted Text (`#A8A29E`): Subtle sand-stone tone for inactive hints and secondary border indications.
- **Accents & Semantics:**
  - Primary Accent (`#B65F3A`): Muted copper / burnt terracotta for primary calls-to-action, active tabs, and key focus moments.
  - Accent Hover (`#9E4F2E`): Deep terracotta for interactive feedback states.
  - Accent Tint (`rgba(182, 95, 58, 0.08)`): Subdued wash for selection rings, active list items, and highlights.
  - Success / Stable (`#2D5A43`): Heritage dark forest green for successful automated pipelines, published states, and test coverage.
  - Border Hairline (`#DDD9D0`): Crisp, soft warm sand gray for 1px layout grids, cell demarcations, and structural dividers.

## Typography

The typographical pairing sets up a deliberate contrast between editorial narrative depth and engineered utility:

- **Display & Headings:** `Playfair Display` evokes publication authority, craft, and intellectual depth. Reserved for document titles, chapter headings, and key editorial summaries. Maintain tight negative tracking (`-0.01em` to `-0.02em`) to preserve a modern, tailored silhouette.
- **Interface & Prose:** `Geist` provides clinical neutrality and high legibility across long-form analysis, settings panels, and documentation tables.
- **Telemetry, Code & Metadata:** `JetBrains Mono` governs status indicators, execution traces, word counters, and commit hashes. Always set uppercase labels with expanded tracking (`0.04em` to `0.08em`) for immediate technical scanning.

## Layout & Spacing

The layout is built on a disciplined, fixed-proportion grid structure reminiscent of broadsheet layouts and modular IDE interfaces:

- **Desktop (1280px+):** 12-column grid flanked by a fixed 280px utility sidebar and an 800px maximum reading column for pure editorial composition. Gutter set to `1.5rem` (`24px`), page outer margins set to `3rem` (`48px`).
- **Tablet (768px - 1279px):** 8-column layout with collapsing navigation rail and modular full-bleed card groupings. Gutters remain `1.5rem`.
- **Mobile (<768px):** 4-column linear layout. Margins collapse to `1.25rem` (`20px`), gutters reduce to `1rem` (`16px`).
- **Spatial Rhythm:** Consistent multiples of `4px` and `8px`. White space must feel deliberate, wide, and unhurried around narrative text, contrasting with dense, space-efficient control panels.

## Elevation & Depth

This design system avoids heavy drop shadows, synthetic blurs, and floating spatial physics. Depth is conveyed strictly through structural borders and surface luminance:

- **Level 0 (Base Canvas):** `#F7F5F0`. The default root canvas for pages, feeds, and background panes.
- **Level 1 (Card & Module Layer):** `#FCFBF9`. Used for isolated interactive panels, code execution blocks, and active writing cards. Separated by a sharp 1px hairline border (`#DDD9D0`) rather than a shadow.
- **Level 2 (Popovers, Command Palettes, Dropdowns):** `#FCFBF9` bounded by an assertive `#DDD9D0` border, accompanied only by an ultra-subtle architectural shadow: `0 4px 16px -2px rgba(23, 23, 23, 0.05)`.
- **Code & Runtime Layer:** Deep Charcoal (`#1C1B1A`) with an inset or flush hairline border (`#2D2B2A`), introducing stark tactile depth for developer outputs and syntax inspectors.

## Shapes

The design system employs a crisp, razor-honed geometry (`roundedness: 1`):

- **Base Radius:** `2px` (`rounded-sm`) to `4px` (`rounded-md`) maximum. Surfaces, cards, and input fields never feature bubbly or pill shapes.
- **Badges & Tags:** Precise rectangular tags with `2px` corner softening, reinforcing an archival, index-card tactile feel.
- **Dividers & Structural Rules:** Unbroken 1px horizontal and vertical rules (`#DDD9D0`). No fading or dotted border treatments, only disciplined lines.

## Components

### Buttons
- **Primary:** Solid terracotta (`#B65F3A`), text `#FCFBF9`, `2px` border radius, font `Geist` Medium (13px). Hover transitions to `#9E4F2E`. Active state scales subtly down (`0.99`). Zero box shadow.
- **Secondary / Outline:** Background `#FCFBF9`, border 1px `#DDD9D0`, text `#171717`. Hover applies `#F7F5F0` background and darkens border to `#A8A29E`.
- **Ghost / Utility:** Transparent background, text `#737373`. Hover applies `#DDD9D0` at 30% opacity with `#171717` text.

### Input Fields & Textareas
- Base background `#FCFBF9` with a continuous 1px `#DDD9D0` perimeter border and `2px` radius. Padding `8px 12px`.
- Typography: `Geist` 14px for natural text, `JetBrains Mono` 13px for CLI parameters and slugs.
- Focus state replaces the border with `#B65F3A` and adds a faint `0 0 0 1px #B65F3A` ring. No glowing halos.

### Cards & Panels
- Container: Background `#FCFBF9`, border 1px solid `#DDD9D0`, `4px` corner radius.
- Padding: `24px` for writing cards, `16px` for dense telemetry modules.
- Headers are divided from body sections with a clean 1px bottom border (`#DDD9D0`), anchoring headline serif typography directly above the content area.

### Chips & Badges
- Status / Execution Badges: Background `rgba(182, 95, 58, 0.08)`, text `#B65F3A`, border 1px solid `rgba(182, 95, 58, 0.25)`. Font: `JetBrains Mono` (10px / Uppercase).
- Success / Live Indicators: Background `rgba(45, 90, 67, 0.08)`, text `#2D5A43`, border 1px solid `rgba(45, 90, 67, 0.25)`. Includes a solid 6px circular green glyph.

### Checkboxes & Radios
- Square 14px x 14px boxes with a sharp `2px` corner radius. 1px border `#DDD9D0`.
- Checked state: `#B65F3A` fill with a sharp white checkmark glyph. No elastic animations; transition duration is strictly 100ms ease-out.

### Code Snippets & Terminal Panels
- Surface `#1C1B1A`, hairline border `#2D2B2A`, rounded `2px`.
- Header rail contains document path or branch telemetry set in `JetBrains Mono` 11px uppercase in `#737373`, separated by a 1px border from the code pane. Syntax highlighting follows warm ochre, forest green, and muted stone hues.