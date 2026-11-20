```markdown
# Care Carry

A Django web application styled with **Tailwind CSS v4** (built via npm/PostCSS — not `django-tailwind`).

- **Backend:** Django
- **Styling:** Tailwind CSS v4 + PostCSS
- **Fonts:** Poppins (headings) · Montserrat (body)
- **Design language:** Sharp edges, hard offset shadows, navy & gold brand palette

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Environment variables](#3-environment-variables)
4. [Tailwind CSS setup](#4-tailwind-css-setup)
5. [Running the project](#5-running-the-project)
6. [Building for production](#6-building-for-production)
7. [Project structure](#7-project-structure)
8. [Design system reference](#8-design-system-reference)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

Make sure you have:

| Tool | Version | Check |
|---|---|---|
| Python | ≥ 3.11 | `python --version` |
| pip | latest | `pip --version` |
| Node.js | ≥ 18 | `node --version` |
| npm | ≥ 9 | `npm --version` |

> ⚠️ **Node 18+ is required.** Tailwind CSS v4 relies on modern Node features. Node 16 or below will break the build silently.

---

## 2. Installation

### 2.1 Clone the repo

```bash
git clone <repo-url> care-carry
cd care-carry
```

### 2.2 Python — create and activate a virtual environment

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2.3 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Install Node dependencies

```bash
npm install
```

This installs Tailwind v4, `@tailwindcss/postcss`, `postcss-cli`, and the supporting build tools listed in `package.json`.

### 2.5 Apply database migrations

```bash
python manage.py migrate
```

### 2.6 Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

---

## 3. Environment variables

Create a `.env` file at the project root (copy from `.env.example` if present):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Generate a fresh secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. Tailwind CSS setup

This project **does not use `django-tailwind`**. The build is driven entirely by npm and PostCSS. Here's how it's wired so you can modify it safely.

### 4.1 The build pipeline

```
theme/static_src/src/styles.css     ← you edit this (your @theme + component styles)
          │
          ▼  postcss + @tailwindcss/postcss
          │
theme/static/css/dist/styles.css    ← generated, consumed by Django templates
```

### 4.2 `postcss.config.js`

Tailwind v4 uses the **dedicated** `@tailwindcss/postcss` plugin (not `tailwindcss`):

```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

### 4.3 `theme/static_src/src/styles.css`

The entry file starts with:

```css
@import "tailwindcss";

/* Tell Tailwind where your Django templates live.
   Path is RELATIVE to this CSS file.
   From theme/static_src/src/  →  3 levels up  →  project root. */
@source "../../../**/*.{html,py}";
@source "../../../**/templates/**/*.html";

@theme static {
  /* brand tokens, fonts, radii, shadows — see section 8 */
}
```

> **The `@source` glob is the #1 cause of "my classes don't compile" bugs.** If your `styles.css` is not exactly at `theme/static_src/src/styles.css`, adjust the number of `../` so that the path resolves to your project root (where `manage.py` lives). Verify with:
> ```bash
> cd theme/static_src/src && realpath ../../../   # must be the project root
> ```

### 4.4 Django settings — `settings.py`

```python
STATIC_URL = '/static/'                  # leading slash required

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'theme' / 'static',       # ⚠️ required — theme/static must be discoverable
]

STATIC_ROOT = BASE_DIR / 'staticfiles' / 'static'
```

> **Do not** leave `theme/static` out of `STATICFILES_DIRS`. Django's staticfiles finder won't see your compiled CSS and every page will 404 on `styles.css`.

**You do not need** `TAILWIND_APP_NAME` or `'tailwind'` in `INSTALLED_APPS`. That configuration belongs to the `django-tailwind` Python package, which this project does not use.

### 4.5 Base template

Your `base.html` must:

1. Load fonts via Google Fonts `<link>`
2. Load the compiled stylesheet via `{% static %}`

```django
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Home{% endblock title %} | Care Carry</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="{% static 'css/dist/styles.css' %}">
  </head>
  <body>
    {% block content %}{% endblock content %}
  </body>
</html>
```

> Tailwind generates `font-display` / `font-body` utilities, but it never downloads the font files — the `<link>` above is mandatory.

---

## 5. Running the project

Development requires **two terminals** running side by side: one for Django, one for Tailwind's watch mode.

### Terminal 1 — Django dev server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>

### Terminal 2 — Tailwind watcher

```bash
npm run dev
```

This runs `postcss` in watch mode. Any edit to `styles.css` **or** to a template that introduces a new utility class triggers a rebuild of `theme/static/css/dist/styles.css` within ~200 ms.

> **First-time run:** if `theme/static/css/dist/styles.css` does not exist yet, run `npm run build` once (see section 6) before starting the watcher. Otherwise Django will 404 the stylesheet until the first rebuild.

### Optional — combine both commands

If you want a single command for both (e.g. using `concurrently` or `honcho`):

```bash
# example with honcho
honcho start
```

Otherwise, two terminals is the simplest setup.

---

## 6. Building for production

```bash
npm run build
```

The `build` script does two things:

1. **`build:clean`** — wipes `theme/static/css/dist/` via `rimraf`
2. **`build:tailwind`** — compiles and minifies into `theme/static/css/dist/styles.css`

Then collect static files for deployment:

```bash
python manage.py collectstatic --noinput
```

Static output goes to `STATIC_ROOT` (`staticfiles/static/`). This project's layout is intentionally nested under a `static/` subfolder so it lines up with Vercel's `/static/(.*)` route — see `vercel.json`.

**Before deploying, always:**

1. `npm run build` (fresh compiled CSS)
2. `python manage.py collectstatic --noinput`
3. Confirm the file exists: `ls staticfiles/static/css/dist/styles.css`

---

## 7. Project structure

```
care-carry/
├── manage.py
├── package.json                    ← npm scripts & Tailwind dev deps
├── postcss.config.js               ← @tailwindcss/postcss plugin
├── requirements.txt                ← Django & Python deps
├── vercel.json                     ← static-build config
│
├── config/                         ← Django project (settings, urls, wsgi)
│   ├── settings.py
│   └── urls.py
│
├── theme/                          ← styling app
│   ├── static_src/
│   │   └── src/
│   │       └── styles.css          ← ⚠️ you edit this — @theme lives here
│   │   └── src/
│   │       └── styles.css          ← entry point for PostCSS
│   │
│   ├── static/
│   │   └── css/
│   │       └── dist/
│   │           └── styles.css      ← ⚠️ generated — never edit by hand
│   │
│   └── templates/
│       └── root-layout.html        ← base template
│
├── static/                         ← hand-written static assets (images, favicon)
├── staticfiles/                    ← collectstatic output (deployed)
└── media/                          ← user uploads
```

**Never edit `theme/static/css/dist/styles.css`** — it gets wiped on every build.

---

## 8. Design system reference

All design tokens live in the `@theme` block inside `theme/static_src/src/styles.css`. Add new tokens there; Tailwind auto-generates the utilities.

### Colors

| Token | Value | Utility examples |
|---|---|---|
| `--color-cay-primary` | `#05162D` (navy) | `bg-cay-primary` `text-cay-primary` |
| `--color-cay-primary-soft` | `#EDF1F7` | `bg-cay-primary-soft` |
| `--color-cay-secondary` | `#D19611` (gold) | `text-cay-secondary` `bg-cay-secondary` |
| `--color-cay-secondary-soft` | `#FBF1DC` | `bg-cay-secondary-soft` |
| `--color-cay-accent` | `#45536D` | `text-cay-accent` |
| `--color-cay-neutral` | `#E9D0AE` | `bg-cay-neutral` |
| `--color-cay-light` | `#F2F3F8` | `bg-cay-light` |
| `--color-success` … `--color-info` | semantic | `text-success` `bg-error-soft` etc. |
| `--color-neutral-0` … `--color-neutral-900` | slate scale | `text-neutral-500` etc. |

### Radii

All radii are `0` except `--radius-full` (used for pills/avatars). Everything is squared off by design.

### Shadows

| Token | Effect |
|---|---|
| `--shadow-xs` … `--shadow-lg` | Subtle offset in brand navy |
| `--shadow-hard-sm` / `--shadow-hard` / `--shadow-hard-lg` | Solid 2/4/6 px navy offset |
| `--shadow-hard-brand` | Gold offset — reserved for primary CTAs |

Usage: `.executive-card:hover` applies `shadow-hard`.

### Fonts

| Utility | Family |
|---|---|
| `font-display` | **Poppins** (headings, `h1`–`h4`) |
| `font-body` | **Montserrat** (everything else — applied to `body` in base) |
| `font-mono` | JetBrains Mono (falls back to system mono) |

### Component classes

Reusable `@layer components` classes available out of the box:

- **Layout:** `.page-container`, `.page-header`
- **Nav:** `.nav-link`
- **Buttons:** `.btn` + `.btn-primary`, `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-block`
- **Cards:** `.card`, `.executive-card` (+ `__media`, `__body`, `__name`, `__position`, `__meta`)
- **Forms:** `.form-field`, `.form-label`, `.form-input`, `.form-select`, `.form-textarea`, `.form-help`, `.form-error`
- **Image upload:** `.image-upload` (+ `--filled`, `__preview`, `__remove`)
- **Badges:** `.badge` + `.badge-brand`, `.badge-gold`, `.badge-success`, `.badge-warning`, `.badge-error`
- **Alerts:** `.alert` + `-success`, `-info`, `-warning`, `-error`
- **Stats:** `.stat-card` (+ `__value`, `__label`, `__hint`)
- **Tables:** `.table-wrap`, `.table`, `.table-actions` (mobile → card layout under 640 px)
- **Danger zone:** `.danger-zone`

---

## 9. Troubleshooting

### ❌ My Tailwind classes don't compile — colors stay black, layout is unstyled

**This is almost always a `@source` path issue.** Tailwind only generates a utility if it finds the class name in a file matched by `@source`.

**Diagnose:**

```bash
# Is the class in the compiled CSS?
grep "text-cay-secondary" theme/static/css/dist/styles.css

# Any cay-* utility?
grep -c "cay-primary" theme/static/css/dist/styles.css
```

If those return nothing:

1. Confirm the file exists: `ls theme/static/css/dist/styles.css`
2. Re-run the watcher: `npm run dev`
3. If still missing, verify your `@source` glob resolves to the project root:

   ```bash
   cd theme/static_src/src
   realpath ../../../
   # must equal the directory containing manage.py
   ```
4. Fix the number of `../` in `styles.css` if it doesn't match.

> ⚠️ **VS Code's color swatches are misleading.** The little colored square next to `--color-cay-secondary: #D19611;` is an editor feature that parses CSS variables — it does **not** indicate that `text-cay-secondary` exists as a utility in the compiled output. Always verify with `grep`.

### ❌ `styles.css` returns 404 in DevTools

```bash
curl -I http://localhost:8000/static/css/dist/styles.css
```

- **404** → check `STATICFILES_DIRS` in `settings.py` includes `BASE_DIR / 'theme' / 'static'`, and that `STATIC_URL = '/static/'` has a leading slash.
- **200 but no styles** → the file exists but doesn't contain the utility. Go back to the `@source` issue above.

### ❌ Everything works on `/` but breaks on `/some/page/`

`STATIC_URL = 'static/'` (no leading slash) is the culprit. Change to `'/static/'`.

### ❌ Fonts aren't applying (Poppins / Montserrat)

Tailwind does not download fonts. Ensure the Google Fonts `<link>` is in `base.html`'s `<head>`. Inspect the `<h1>` in DevTools → Computed → `font-family` should show `Poppins, ...`.

### ❌ `npm run build` fails with "unknown utility class" or "unknown at-rule @theme"

Your installed Tailwind is **v3**, not v4. Check:

```bash
npm list tailwindcss
# must show 4.x.x
```

If it's 3.x, install v4 explicitly:

```bash
npm install -D tailwindcss@^4 @tailwindcss/postcss@^4
```

### ❌ `npm run dev` does nothing / no CSS is generated

Node version check — Tailwind v4 requires **Node 18+**:

```bash
node --version
```

If older, upgrade Node (via `nvm` is easiest).

### ❌ `collectstatic` complains about missing source files

If `theme/static/css/dist/styles.css` doesn't exist, `collectstatic` will fail on that entry. Always run `npm run build` **before** `collectstatic`.

---

## Quick reference — the commands you'll type daily

```bash
# terminal 1
python manage.py runserver

# terminal 2
npm run dev

# before deploying
npm run build
python manage.py collectstatic --noinput
```

---

## License

MIT
```

---

A few notes on what I baked in:

- **Section 4.4** explicitly calls out the `STATICFILES_DIRS` fix and the `STATIC_URL` leading slash — these were both live bugs in your setup.
- **Section 9** leads with the `@source` troubleshooting because that was your actual root cause.
- **VS Code swatch warning** is included because it misled you once and will mislead the next person too.
- **Two-terminal workflow** is documented rather than assuming `django-tailwind`'s management command.
- **No `django-tailwind`** anywhere — the README commits to the npm approach you actually built.
- **Design system section** means contributors don't have to reverse-engineer `@theme` — they can look up tokens in one place.

If your `vercel.json` or `requirements.txt` diverge from what I described, adjust those specific blocks to match.