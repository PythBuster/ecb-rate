# ecb-rate

Simple CLI tool to fetch EUR-based exchange rates from the European Central Bank (ECB) API.

Note: ECB euro foreign exchange reference rates are published for information purposes only.
Using these rates for transaction purposes is strongly discouraged by the ECB.

Official ECB reference:
https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html

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

    ecb_rate TRY --specific-date 2025-06-06

---

### Pretty output

    ecb_rate TRY --pretty

Output:

    Base currency:   EUR
    Target currency: TRY

    2025-06-06: 1 EUR = 43.1234 TRY

---

### Version

    ecb_rate --version

Output:

    ecb_rate 0.4.1

Use this option to print the installed CLI version and exit immediately.

---

## Supported currencies

The CLI supports all currencies defined by the ECB reference exchange rate dataset (EXR).

Currently implemented currencies:

- AUD – Australian dollar (Australia)
- BRL – Brazilian real (Brazil)
- CAD – Canadian dollar (Canada)
- CHF – Swiss franc (Switzerland)
- CNY – Chinese yuan (China)
- CZK – Czech koruna (Czech Republic)
- DKK – Danish krone (Denmark)
- EUR – Euro (Eurozone)
- GBP – Pound sterling (United Kingdom)
- HKD – Hong Kong dollar (Hong Kong)
- HUF – Hungarian forint (Hungary)
- IDR – Indonesian rupiah (Indonesia)
- ILS – Israeli shekel (Israel)
- INR – Indian rupee (India)
- ISK – Icelandic krona (Iceland)
- JPY – Japanese yen (Japan)
- KRW – South Korean won (South Korea)
- MXN – Mexican peso (Mexico)
- MYR – Malaysian ringgit (Malaysia)
- NOK – Norwegian krone (Norway)
- NZD – New Zealand dollar (New Zealand)
- PHP – Philippine peso (Philippines)
- PLN – Polish zloty (Poland)
- RON – Romanian leu (Romania)
- SEK – Swedish krona (Sweden)
- SGD – Singapore dollar (Singapore)
- THB – Thai baht (Thailand)
- TRY – Turkish lira (Turkey)
- USD – US dollar (United States)
- ZAR – South African rand (South Africa)

Source:
https://data-api.ecb.europa.eu/service/data/EXR

Currency support in this tool is defined via the `CurrencyType` enum.

---

## API

Uses the official ECB Data Portal:

    https://data-api.ecb.europa.eu/service/data/EXR

Format:

- jsondata (SDMX JSON)

Reference rates are intended for informational use and should not be treated as executable market prices.

---

## Project structure

    ecb_rate/
    ├─ cli.py
    ├─ client.py
    ├─ custom_types.py
    ├─ models.py
    ├─ service.py
    └─ utils.py

---

## Development

Install dev dependencies:

    uv sync --dev

Run tests:

    pytest