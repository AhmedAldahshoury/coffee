# Coffee Optimizer Design System

## Theme tokens (Premium Dark Espresso)
All UI colors are defined as CSS variables in `frontend/src/app/styles.css`.

### Core surfaces
- `--bg0`: app background `#0E0C0A`
- `--bg1`: card base `#141210`
- `--bg2`: elevated card/popover `#1C1916`
- `--bg3`: input surface `#221F1B`

### Borders
- `--border-subtle`: `rgba(245,243,240,0.08)`
- `--border-strong`: `rgba(245,243,240,0.14)`

### Typography colors
- `--text-primary`: `#F5F3F0`
- `--text-secondary`: `#B8B4AE`
- `--text-muted`: `#7A756F`
- `--text-inverted`: `#0E0C0A`

### Accents
- `--accent-500`: `#C88A3D`
- `--accent-400`: `#E2A85C`
- `--accent-300`: `#F2C078`
- `--teal-600`: `#2F6F6D`
- `--teal-500`: `#3E8E8B`

### Status
- `--success`: `#3FAE6B`
- `--warning`: `#D9A441`
- `--error`: `#D06A5E`
- `--info`: `#4DA3FF`

### Glow
- `--accent-glow`: `rgba(200,138,61,0.25)`
- `--teal-glow`: `rgba(62,142,139,0.18)`

## Component rules
- **Buttons**: primary uses caramel gradient (`--accent-300` -> `--accent-500`), secondary uses neutral filled surface + border, ghost uses transparent surface with subtle hover fill.
- **Inputs**: always on `--bg3` with `--border-subtle`; focus ring uses `--accent-glow`.
- **Cards/Panels**: layered `--bg1`/`--bg2` gradient, subtle border and inset highlight for premium depth.
- **Navigation**: active item uses subtle accent-tinted pill + animated underline.
- **Tables**: subtle zebra + hover highlighting; high-contrast headers and row dividers.
- **Toasts**: elevated dark pill with status-specific shadow treatment.
- **Charts**: primary line in teal (`--teal-500`), interactive highlights in caramel accents.
- **Icons/logo**: unified custom SVG icon style in `frontend/src/components/icons.tsx`; app mark also used for favicon (`frontend/public/coffee-logo.svg`).

## Motion rules
- **Micro interactions** (hover/press): `--motion-micro` = 140ms.
- **Component enter/exit**: `--motion-component` = 220ms.
- **Page transition**: `--motion-page` = 300ms.
- **Easing**:
  - Enter: `--ease-enter` (`cubic-bezier(0.2, 0.8, 0.2, 1)`)
  - Exit: `--ease-exit` (`cubic-bezier(0.4, 0, 1, 1)`)
- **Patterns used globally**:
  - fade + translateY for panels/pages (`fadeUp`, `pageEnter`)
  - button press scale (`0.98`)
  - nav underline slide
  - skeleton shimmer loading state
