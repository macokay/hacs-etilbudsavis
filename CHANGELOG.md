# Changelog

## [1.1.8] - 2026-10-22

### Added
- Watch catalogs from chosen stores: one timestamp sensor per store showing when its newest catalog was released, with current and upcoming catalogs (label, valid dates, page count, PDF link, cover image) as attributes
- Setup now starts by asking what to follow: search terms, store catalogs, or both. Search settings only appear when search is selected
- Store names are checked against eTilbudsavis during setup, so a store without catalogs is rejected instead of giving a silent `unknown` sensor
- Digital (incito) catalogs are included, which covers Biltema, BAUHAUS, Bygma and XL-BYG
- `Fakta` in the store filter now matches Coop 365, since Fakta was renamed
- Stores added under Configure are checked against eTilbudsavis, the same as at setup

### Changed
- Minimum Home Assistant version is now 2024.10 (selector translations in setup, and the automation example syntax)
- Search terms are now optional in the options flow, as long as at least one store catalog is watched
- Catalogs are fetched for all of Denmark instead of within the search radius, so border shops and other stores far from home work. The radius now only applies to item search
- Setup with only catalogs selected finishes after the store list, since there are no search settings to ask about
- Catalog sensors keep their last known value when an update fails, instead of turning `unknown`

## [1.1.7] - 2026-09-29

### Fixed
- Store filter now matches store names regardless of case, spaces and punctuation. `Rema1000` matches the API's `REMA 1000`, which previously returned 0 offers ([#7](https://github.com/macokay/hacs-etilbudsavis/issues/7))
- `Coop 365` now matches the API's `365discount`, which previously returned 0 offers
- Fetch up to 100 offers per search term (was 24) before filtering by store, so stores further down the result list are no longer cut off

## [1.1.1] - 2026-04-09

### Changed
- README restructured to standard template format — logo, badges, Buy Me A Coffee, structured sections
- Issue templates updated to standard format — added Actual behaviour section and log filter instructions
- `.gitignore` removed (managed by global gitignore)
- Bumped version to force HACS translation cache refresh

## [1.1.0] - 2026-03-11

### Added
- Price per kg option (similar to price per liter, for food items)

### Changed
- Fixed store name casing: `fakta` → `Fakta`, `Rema 1000` → `Rema1000`

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
