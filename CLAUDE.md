# HyperCTui

PyQt GUI for hyperspectral CT reconstruction at the VENUS beamline (SNS).

## Names

- PyPI/conda package: `hyperctui` (conda channel: `neutronimaging`)
- Python module: `hyperctui` (src layout under `src/`)
- GitHub repo: `HyperCTui`

## Environment and commands

Pixi-managed — run everything through `pixi run`.

- `pixi run test` — pytest with coverage, offscreen Qt
  (`QT_QPA_PLATFORM=offscreen` is set in tests/conftest.py)
- `pixi run pre-commit run --files <files>` — lint
- Packaging tasks live in the isolated `package` environment:
  `pixi run -e package verify-conda` / `build-pypi`. The package feature
  (boa/conda-build) caps Python at 3.11 — that is WHY it has its own
  solve-group; do not merge it back into default.
- `jupyter` env for notebook work.

## Branch flow

`next` (default, development) → `qa` → `main`. PRs target `next`.
package.yml (conda + PyPI publish) only runs on qa/main/tags, so packaging
breakage on next stays latent — the packaging-smoke CI job exists to catch
the wheel-content part early.

## Conventions and caveats

- `crop.py` loads `*_SummedImg.fits` directly via astropy (NeuNorm removed
  in #179). The load contract is pinned by
  `tests/unit/hyperctui/crop/test_load_projections.py`: positional 0/180
  identity, native float32, singleton-3D squeeze, NeuNorm-1.x-parity gamma
  filter, exactly-2 projection guard. Do not "simplify" the gamma filter or
  re-sort the projection list.
- `config.json` MUST stay in package-data ("*.json" glob) — every published
  artifact crashed at startup when it was missing. The packaging-smoke job
  guards this.
- Developer mode is `HYPERCTUI_DEBUG=1` (env var), never a hardcoded flag;
  homepath falls back to "/" for beamline machines.
- tomopy is conda-only and lazily imported; keep it out of
  [project.dependencies].
- Coverage policy (codecov.yml): project floored just below current so it
  ratchets up; patch is informational until the GUI has a real test
  harness. The suite has ~150 skipped placeholder tests — a "passed" run
  does not imply broad coverage.
- Known open items: TOF ROI transpose (#181, needs visual GUI
  verification), SNAP-vs-VENUS source-detector distance (#182, instrument
  decision), boa→pixi-build migration (would free the package env's Python
  cap entirely).
