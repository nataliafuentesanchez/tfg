# Changelog - AnalisisImagenes

All notable changes to this project are documented in this file.
This format follows Keep a Changelog and Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-07-24

### Added
- Initial SDD setup for project context and planning.
- FastAPI web app with endpoints `GET /`, `GET /health`, and `POST /analyze`.
- Baseline dermatology image analysis service with:
  - primary classification (`sano` / `enfermo`)
  - severity levels (`ninguno`, `bajo`, `medio`, `peligro`)
  - probable lesion type (`benigno_probable` / `maligno_probable`)
  - referral recommendation for dermatology
- Human-readable report (`user_report`) in addition to technical JSON output.
- Frontend redesign for demo presentation quality.
- Frontend assets organized into dedicated folders:
  - `app/static/css/styles.css`
  - `app/static/js/app.js`
- Cross-platform run scripts:
  - Windows: `start.cmd`, `stop.cmd`
  - macOS/Linux: `start.sh`, `stop.sh`
- Initial test suite (unit + integration) for core logic and health endpoint.

### Changed
- `README.md` updated with real installation and run instructions.
- UI updated to show both understandable narrative output and machine-readable JSON.

### Fixed
- Consistency of analysis response payload to support both technical and non-technical users.
