# Coffee Optimizer

Optimization toolkit for AeroPress and pour over experiments with a new premium web UI.

## What is included

- Python/Optuna CLI optimizer for deeper experimentation (`optimize.py`).
- Premium web interface (`web/`) for quick recommendations.
- Cloudflare Pages deployment workflow (`.github/workflows/deploy-cloudflare-pages.yml`).

## CLI usage

Install deps:

```bash
pip install -r requirements.txt
```

Run optimizer on AeroPress data:

```bash
python optimize.py aeropress.
```

Helpful flags:

```bash
python optimize.py aeropress. --best
python optimize.py aeropress. --method mean --persons nick tom
python optimize.py aeropress. --importance --scores
```

## Premium UI usage (local)

Serve the repository root so the app and dataset can load:

```bash
python -m http.server 8000
```

Then open:

- `http://localhost:8000/web/`


All CLI flags are now available in the web UI controls:

- `--best` via **Best mode** toggle
- `--persons` via **Persons** multi-select chips
- `--method` via **Scoring method**
- `--weight` via **Prior weight** slider
- Visualization flags (`--time`, `--relations`, `--edf`, `--importance`, `--slice`, `--scores`) via **Visualizations** toggles


## Deploy to Cloudflare

### Option 1: Cloudflare Pages (recommended)

1. Create Pages project named `coffee-28b` (or update the GitHub workflow project name to your actual Pages project).
2. Set build output directory to `web`.
3. Add repo secrets in GitHub:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
4. Push to `main` and the GitHub Action deploys automatically.

You can view deployments in:

- GitHub Actions tab (workflow runs)
- Cloudflare Pages project → **Deployments**

### Option 2: Wrangler static assets

```bash
npx wrangler deploy
```

using `wrangler.toml` in this repo.

### 404 troubleshooting

If your deployment succeeds but `*.pages.dev` shows **404 Not Found**, one of these is usually wrong:

1. **Project name mismatch** between GitHub workflow and Cloudflare Pages project.
2. **Build output directory** should be `web` (for this repo layout).
3. **Wrong branch** deployed vs your Pages production branch.

This repo now includes a root `index.html` redirect to `/web/` as a safety fallback when the root directory is deployed.
