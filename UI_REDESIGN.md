# UI Redesign Audit + Implementation Notes

## A) Audit of current UI before redesign

### Routes/pages found
- `/` (Brew)
- `/history`
- `/insights`

### Components found
- App-level: `App.tsx`, `TopNav.tsx`
- Brew: `RecipeCard`, `AdvancedControls`, `PersonsSelector`, `BrewInputsCard`, `OnboardingEmptyState`
- History: `HistoryTable`
- Insights charts: `OptimizationHistoryChart`, `ImportanceChart`, `ScoresBoxChart`, `EdfChart`, `SliceChart`

### Existing backend/data integration points
- `loadData(dataset)` -> fetches `/public/data/*.csv` from `web/src/lib/data.ts`
- `getState()` + `recommendationFromHistorical()` in `web/src/lib/optimizer.ts`
- `getScore()` in `web/src/lib/scoring.ts`
- Brew logging previously used direct `localStorage.setItem('coffee:last-log', ...)`

### Per-page user actions and backend mapping
- Brew page:
  - Dataset switcher -> should trigger `loadData(dataset)` and refresh calculations.
  - "Get next recipe" -> should recompute recommendation from historical data.
  - "Log result" -> should persist a typed brew log entry.
  - Scoring method/weight/best/person filters -> should recompute optimizer state and recommendation.
- History page:
  - table view/filtering -> should reflect derived optimizer historical rows.
- Insights page:
  - chart toggles + slice parameter -> should render charts from optimizer state and dataset fields.

### Problems identified
- No service layer (UI called lib methods and localStorage directly in components).
- Partial action wiring (buttons like Import/Add brew were placeholders).
- Sparse validation (no numeric validation for log score before write).
- Weak state UX (minimal loading/error/empty states).
- Inconsistent layout and spacing; no app shell/sidebar.
- No reusable feedback system (toasts) for async action outcomes.

## B-F) New structure and design system

## New component structure
- Layout:
  - `PageShell` (sidebar + header + content)
  - `AppSidebar` (nav, collapsible)
  - `AppHeader` (route title, dataset selector, theme toggle)
- Shared UI:
  - `SectionCard`, `FilterBar`
  - state components: `EmptyState`, `ErrorState`, `SkeletonBlock`
  - `ToastProvider` for success/error feedback
- Existing feature components modernized:
  - `BrewInputsCard`, `AdvancedControls`, `PersonsSelector`, `RecipeCard`, `HistoryTable`

## Design tokens
- 8pt rhythm by using spacing classes in 2/4/6/8 patterns.
- Centralized color tokens in CSS variables (`--background`, `--foreground`, `--card`, `--primary`, etc).
- Light/dark mode supported by toggling `html.dark` class.
- Unified radius/shadow from Tailwind config (`rounded-lg/xl`, subtle `shadow-sm`).

## Service layer (single source of truth)
- `src/services/datasetService.ts`
  - `listDatasets()`
  - `load(dataset)` wraps CSV fetch logic and returns typed `ServiceResult`.
- `src/services/recommendationService.ts`
  - `generate(loaded, preferences)` validates preferences and computes `state + recommendation`.
- `src/services/brewLogService.ts`
  - `create(payload)` validates score (0-10), stores typed log entry in localStorage.
  - `list()` returns logs.
- Shared service types in `src/services/types.ts`.

## UI actions -> backend calls (final)
- Dataset selector: `datasetService.load(dataset)`
- Get next recipe: `datasetService.load(dataset)` refresh + `recommendationService.generate(...)`
- Save brew log: `brewLogService.create(payload)` (typed + validated)
- Advanced controls: `recommendationService.generate(...)` via reactive state update
- History and insights rendering: derived from `recommendationService.generate(...).data.state`

## Error/loading/empty handling
- Global dataset load error state in app shell content.
- Recommendation validation error state.
- Skeletons while loading datasets/recommendations.
- Empty state for missing historical data in Brew/History/Insights.
- Toasts on brew log success/error.

## TypeScript and maintainability improvements
- Added typed service interfaces/payloads/results.
- Removed direct localStorage side-effect from route and centralized in service.
- Improved route/component prop typing (including async refresh action type).

## Testing
- Added service layer tests using Vitest for:
  - recommendation validation and generation
  - brew log validation and persistence
