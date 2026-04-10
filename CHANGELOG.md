## [Unreleased]

### Added

### Changed

### Removed

---
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