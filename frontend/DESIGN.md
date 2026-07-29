---
name: ShipNova Inspired Logistics Platform
colors:
  surface: '#ffffff'
  surface-dim: '#f8fafc'
  surface-bright: '#ffffff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f5f9'
  surface-container: '#e2e8f0'
  surface-container-high: '#cbd5e1'
  surface-container-highest: '#94a3b8'
  on-surface: '#0f172a'
  on-surface-variant: '#64748b'
  inverse-surface: '#1e293b'
  inverse-on-surface: '#f8fafc'
  outline: '#e2e8f0'
  outline-variant: '#cbd5e1'
  surface-tint: '#3b82f6'
  primary: '#3b82f6'
  on-primary: '#ffffff'
  primary-container: '#eff6ff'
  on-primary-container: '#1e3a8a'
  inverse-primary: '#bfdbfe'
  secondary: '#f97316'
  on-secondary: '#ffffff'
  secondary-container: '#ffedd5'
  on-secondary-container: '#9a3412'
  tertiary: '#10b981'
  on-tertiary: '#ffffff'
  tertiary-container: '#d1fae5'
  on-tertiary-container: '#065f46'
  error: '#ef4444'
  on-error: '#ffffff'
  error-container: '#fee2e2'
  on-error-container: '#991b1b'
  background: '#f8fafc'
  on-background: '#0f172a'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  data-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  label-mono:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 1.5rem
  gutter: 1.5rem
  stack-compact: 0.5rem
  stack-default: 1rem
---

## Brand & Style
The design system draws inspiration from the ShipNova Logistics Platform, shifting the application from a dark "ops-tool" aesthetic to a bright, clean, and modern **Light Theme**. It emphasizes readability, generous whitespace, and soft shadows to create an approachable and highly functional enterprise interface.

## Colors
- **Foundations:** The application background uses a soft off-white (`#f8fafc`) to reduce glare, while cards and interactive containers pop out cleanly using pure white (`#ffffff`).
- **Borders & Dividers:** Subtle gray outlines (`#e2e8f0`) structure the layout without overpowering the content.
- **Accents:** 
  - **Primary Blue (`#3b82f6`):** Used for active navigation items, progress bars, primary buttons, and key map routes.
  - **Secondary Orange (`#f97316`):** Used for data visualization charts (e.g., secondary line graphs) and pending status indicators.
  - **Success Green (`#10b981`):** Used to highlight positive trends (e.g., `+12.5%`) and delivered statuses.

## Typography
- **Primary Typeface:** **Inter** is used globally across headings, body text, and labels. The `JetBrains Mono` font is removed in favor of standard sans-serif utility for a more consumer-friendly enterprise feel.
- **Data Values:** Large numerical values use a heavy bold weight (`700`) at 24px to ensure they stand out clearly against the white background.

## Elevation & Depth
- **Surface 0 (Background):** `#f8fafc`
- **Surface 1 (Cards):** `#ffffff` with a subtle drop shadow (`shadow-sm` or `shadow-md`) and a 1px border (`#e2e8f0`).

## Shapes
- **Corner Radii:** Cards, buttons, and badges utilize softer, rounded corners (8px to 12px / `rounded-lg` and `rounded-xl`), creating a modern, friendly interface compared to the previous harsh 4px corners.
