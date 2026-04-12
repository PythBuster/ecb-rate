## [Unreleased]

### Added

### Changed

### Removed

---
## [0.5.2] - 2026-04-12

### Changed
- Replaced runtime loading from `pyproject.toml` with installed package metadata

### Removed
- Removed `utils.py` and the `load_pyproject()` helper


## [0.5.1] - 2026-04-12

### Added
- Added `LICENSE` and `MANIFEST.in` to improve PyPI packaging

### Changed
- Updated `pyproject.toml` metadata for PyPI publishing

## [0.5.0] - 2026-04-12

### Added

- Added `--version` CLI flag to print the installed application version and exit
- Added `utils.py` with `load_pyproject()` helper for reading project metadata from `pyproject.toml`
- Added unit tests for `utils.py`
- Added README note that ECB euro foreign exchange reference rates are published for information purposes only and should not be used for transaction purposes

### Changed

- Changed CLI option `--specificDate` to `--specific-date` to follow common CLI naming conventions
- Changed CLI argument parser to load project metadata such as version and description from `pyproject.toml`
- Improved CLI help texts for all command-line arguments
- Updated CLI tests to use `--specific-date`
- Updated README usage examples to include `--version` and the revised date option naming

### Removed

- Removed legacy camelCase CLI option style for the specific date flag (`--specificDate`)

## [0.4.1] - 2026-04-10

### Changed

- Fixed: handle missing ECB observation values (`None`) before `Decimal` conversion and raise a proper `EcbApiError` instead of `decimal.InvalidOperation`
- Added: regression test for missing ECB observation values in parser handling

## [0.4.0] - 2026-04-10

### Changed

- Refactored: improved and extended unit test coverage across client, CLI, service, models, and custom types
- Refactored: added dedicated client tests again via `test_client.py`
- Refactored: consolidated and simplified multiple tests using parametrization where appropriate
- Refactored: improved service and parser test coverage for invalid payload structures and error propagation
- Fixed: use string-based `Decimal` conversion in ECB rate parsing to avoid float precision artifacts

## [0.3.1] - 2026-04-10
### Changed
- Fixed: removed startPeriod param and uss lastNObservations=1 instead to get the last valid ecb rate for a specific date

## [0.3.0] - 2026-04-10

## Changed
- Refactored: all classes, fetch and paring logic
- Refactored: tests
- Performance improvements: reduce API traffic by limiting data response (params: detail=dataonly)


## [0.2.0] - 2026-04-05

### Added

- Support for all ECB reference currencies
- Extended `CurrencyType` StrEnum to include full ECB currency set


## [0.1.0] - 2026-04-05

### Added

- Initial CLI implementation
- Async ECB API client using aiohttp
- Support for EUR → target currency conversion
- Support for:
  - current rate (default: today)
  - historical date via --specificDate
- Pretty output via --pretty
- Pydantic models for validation
- Custom StrEnum for currencies
- JSON parsing of ECB SDMX format
- Unit tests:
  - CLI
  - Service
  - Parser
  - API client
  - Models
- Pretty output via --pretty
- Pydantic models for validation
- Custom StrEnum for currencies
- JSON parsing of ECB SDMX format
- Unit tests:
  - CLI
  - Service
  - Parser
  - API client
  - Models