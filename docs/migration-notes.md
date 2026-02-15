# Migration Notes

## What changed
1. Removed monolithic CLI runtime and helper modules.
2. Introduced layered backend architecture with clear module boundaries.
3. Preserved core optimization behavior by porting logic into `OptimizerService`.
4. Added web frontend with typed API integration and modular feature structure.
5. Added Docker and Make targets for standardized local/prod workflows.

## Backward compatibility
- CLI interface is intentionally removed.
- Existing CSV datasets are now loaded from `backend/data/`.
- API replaces direct script execution.
