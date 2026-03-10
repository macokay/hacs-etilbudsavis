# Changelog

## [1.0.1] - 2026-03-10

### Changed
- Added standard HACS structure (info.md, CHANGELOG.md, brand/icon.png, GitHub workflows and issue templates)
- Fixed strings.json to be English (identical to translations/en.json) per HA convention

## [1.0.0] - 2026-03-01

### Added
- Initial release
- One sensor per search term with offer count and full offer details as attributes
- `best_offer` attribute with lowest price (or price/liter)
- Filter by store, cans only, search radius
- Optional price per liter calculation
- GUI setup and options flow (no YAML required)
- Updates every 6 hours via shared coordinator
