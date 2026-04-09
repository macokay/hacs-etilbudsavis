<p align="center">
  <img src="custom_components/etilbudsavis/brand/icon.png" alt="eTilbudsavis" width="120" />
</p>

<h1 align="center">eTilbudsavis</h1>

<p align="center">
  Track weekly offers from eTilbudsavis.dk for products you care about — one sensor per search term, updated every 6 hours.
</p>

<p align="center">
  <a href="https://github.com/hacs/integration">
    <img src="https://img.shields.io/badge/HACS-Custom-orange.svg" alt="HACS Custom" />
  </a>
  <a href="https://github.com/macokay/hacs-etilbudsavis/releases">
    <img src="https://img.shields.io/github/v/release/macokay/hacs-etilbudsavis" alt="GitHub release" />
  </a>
  <a href="https://github.com/macokay/hacs-etilbudsavis/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Non--Commercial-blue.svg" alt="License" />
  </a>
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/macokay">
    <img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-%23FFDD00.svg?logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee" />
  </a>
</p>

---

## Features

- Search for any product — one sensor per search term
- Filter by specific stores
- Optional: filter for canned drinks only
- Optional: calculate price per liter (great for beverages)
- Optional: calculate price per kg (great for food items)
- Uses your Home Assistant home location automatically
- Configurable search radius
- All settings editable after setup via the Options flow

---

## Requirements

| Requirement | Version / Details |
|---|---|
| Home Assistant | 2023.1 or newer |
| eTilbudsavis.dk | No API key required — uses unofficial public API |

---

## Installation

### Automatic — via HACS

1. Open **HACS** in Home Assistant.
2. Go to **Integrations** → three-dot menu (⋮) → **Custom repositories**.
3. Add `https://github.com/macokay/hacs-etilbudsavis` as **Integration**.
4. Search for **eTilbudsavis** and click **Download**.
5. Restart Home Assistant.

### Manual

1. Download the latest release from [GitHub Releases](https://github.com/macokay/hacs-etilbudsavis/releases).
2. Copy the `custom_components/etilbudsavis` folder to your `config/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **eTilbudsavis**.
3. Enter the required fields:

| Field | Description |
|---|---|
| Search terms | Comma-separated product names (e.g. `pepsi max, faxe kondi, tuborg classic`) |

Post-setup options are available via **Configure** on the integration card:

| Option | Description | Default |
|---|---|---|
| Stores | Comma-separated list of stores to include. Empty = all. | All stores |
| Radius | Search radius in meters from your home location | 25000 |
| Cans only | Only include offers where "dåse/can" appears in the offer text | Off |
| Price per liter | Calculate and expose price per liter where quantity data is available | Off |
| Price per kg | Calculate and expose price per kg where weight data is available | Off |
| Max offers per item | Maximum number of offers to return per search term | 5 |

**Supported stores:** Bilka, Coop 365, Fakta, Føtex, Kvickly, Lidl, Meny, Netto, Rema1000, Spar, SuperBrugsen

---

## Data

### Entities

| Entity | Type | Description |
|---|---|---|
| `sensor.tilbud_{search_term}` | `int` | Number of active offers found for the search term |

### Attributes

| Attribute | Description |
|---|---|
| `search_term` | The search term used |
| `offers` | List of all offers found (store, heading, price, dates, etc.) |
| `best_offer` | The offer with the lowest price (or price/liter or price/kg if enabled) |

**Example `offers` attribute:**

```json
[
  {
    "store": "Netto",
    "heading": "Pepsi Max dåser 24x33 cl",
    "price": 89.0,
    "price_per_liter": 11.24,
    "total_liters": 7.92,
    "run_from": "2024-01-15T00:00:00+01:00",
    "run_till": "2024-01-21T23:59:59+01:00"
  }
]
```

### Update interval

Data is fetched every 6 hours.

---

## Updating

**Via HACS:** HACS will notify you when an update is available. Click **Update** on the integration card.

**Manual:** Replace the `custom_components/etilbudsavis` folder with the new version and restart Home Assistant.

---

## Known Limitations

- The eTilbudsavis API is unofficial and undocumented — it may change without notice
- Price per liter and price per kg require quantity data in the offer text — not always available
- Offers are only shown if currently active in your configured search area

---

## Credits

- [eTilbudsavis.dk](https://etilbudsavis.dk) — Danish offer aggregator (unofficial API)

---

## License

&copy; 2026 Mac O Kay. Free to use and modify for personal, non-commercial use. Attribution appreciated if you share or build upon this work. Commercial use is not permitted.
