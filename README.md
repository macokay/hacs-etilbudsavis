# eTilbudsavis for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration that fetches weekly offers from [eTilbudsavis.dk](https://etilbudsavis.dk) for items you care about.

Creates one sensor per search term showing the number of active offers nearby, with full offer details (store, price, dates) as attributes.

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

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations** → three-dot menu → **Custom repositories**
3. Add `https://github.com/macokay/hacs-etilbudsavis` as type **Integration**
4. Search for **eTilbudsavis** and install
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration** → search for **eTilbudsavis**

---

## Configuration

### Step 1 – Search terms
Enter comma-separated product names:
```
pepsi max, faxe kondi, tuborg classic
```

### Step 2 – Options

| Option | Description | Default |
|---|---|---|
| Stores | Comma-separated list of stores to include. Empty = all. | All stores |
| Radius | Search radius in meters from your home location | 25000 |
| Cans only | Only include offers where "dåse/can" appears in the offer text | Off |
| Price per liter | Calculate and expose price per liter where quantity data is available | Off |
| Price per kg | Calculate and expose price per kg where weight data is available | Off |
| Max offers per item | Maximum number of offers to return per search term | 5 |

**Supported stores (Danish):** Bilka, Coop 365, Fakta, Føtex, Kvickly, Lidl, Meny, Netto, Rema1000, Spar, SuperBrugsen

---

## Sensors

Each search term creates a sensor:
- **State:** number of active offers found
- **Unit:** `tilbud`

### Attributes

| Attribute | Description |
|---|---|
| `search_term` | The search term used |
| `offers` | List of all offers found (store, heading, price, dates, etc.) |
| `best_offer` | The offer with the lowest price (or price/liter or price/kg if enabled) |

### Example: offers attribute
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

---

## Example automation

```yaml
alias: "Husholdning - Tilbudsavis - Notifikation ved nye tilbud"
description: "Notifikation mandag morgen ved aktive tilbud"
trigger:
  - platform: time
    at: "08:00:00"
condition:
  - condition: time
    weekday: [mon]
  - condition: template
    value_template: >
      {{ states('sensor.tilbud_pepsi_max') | int(0) > 0
         or states('sensor.tilbud_faxe_kondi_lemonade') | int(0) > 0 }}
variables:
  best_pepsi: "{{ state_attr('sensor.tilbud_pepsi_max', 'best_offer') }}"
  best_faxe: "{{ state_attr('sensor.tilbud_faxe_kondi_lemonade', 'best_offer') }}"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "Tilbud denne uge 🛒"
      message: >
        {% if best_pepsi %}🥤 Pepsi Max: {{ best_pepsi.store }} {{ best_pepsi.price_per_liter }} kr/l{% endif %}
        {% if best_faxe %}
        🍋 Faxe Kondi: {{ best_faxe.store }} {{ best_faxe.price_per_liter }} kr/l{% endif %}
```

---

## Notes

- Data updates every 6 hours
- The eTilbudsavis API is unofficial and undocumented — it may change without notice
- Location is taken from Home Assistant's configured home location
- Offers are only shown if they are currently active in your area

---

## Credits

Based on the unofficial `api.etilbudsavis.dk/v2` API.

---

## License

© 2026 Mac O Kay
Free to use and modify for personal, non-commercial use.
Credit appreciated if you share or build upon this work.
Commercial use is not permitted.
