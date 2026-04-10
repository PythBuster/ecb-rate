## [Unreleased]

### Added

### Changed

### Removed

---
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