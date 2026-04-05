# ecb-rate

Simple CLI tool to fetch EUR-based exchange rates from the European Central Bank (ECB) API.

---

## Installation

Using `uv` (recommended):

    uv sync

Or with pip:

    pip install .

---

## Usage

### Basic

    ecb_rate TRY

Output:

    51.2795

---

### With specific date

    ecb_rate TRY --specificDate 2025-06-06

---

### Pretty output

    ecb_rate TRY --pretty

Output:

    Base currency:   EUR
    Target currency: TRY

    2025-06-06: 1 EUR = 43.1234 TRY

---

## Supported currencies

Currently:

- EUR (base)
- TRY

Extending support is straightforward via the `Currency` enum.

---

## API

Uses the official ECB Data Portal:

    https://data-api.ecb.europa.eu/service/data/EXR

Format:

- jsondata (SDMX JSON)

---

## Project structure

    ecb_rate/
    ├─ cli.py
    ├─ service.py
    ├─ models.py
    ├─ custom_types.py
    └─ api/
       └─ json_api.py

---

## Development

Install dev dependencies:

    uv sync --dev

Run tests:

    pytest
