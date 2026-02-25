# Module 05 — Sponsor Pricing Model

> **Document type:** Module Reference  
> **Module path:** `src/pricing/pricing_model.py`  
> **Last updated:** February 2026  
> **Depends on:** [Module 04 — Exposure Analytics Engine](04_exposure_analytics.md)  
> **Feeds into:** Web Interface (Output Layer)

---

## 1. Purpose

The Pricing Model **converts exposure metrics into an estimated sponsorship value**. It uses a configurable weighted linear scoring formula to produce a dimensionless sponsorship score (0–100), which is then mapped to a USD monetary estimate. The value is interconvertible to **Nepalese Rupees (NPR)**.

---

## 2. Position in Pipeline

```
[Exposure Analytics Engine] → ▶ SPONSOR PRICING MODEL ◀ → [Web Interface Output]
```

---

## 3. Scoring Formula

### 3.1 Input Features (per sponsor)

| Feature | Symbol | Description |
|---------|--------|-------------|
| Exposure Duration | $D$ | Total seconds visible |
| Screen Coverage | $C$ | Average bbox area ratio (%) |
| Detection Confidence | $Q$ | Average confidence score (0–1) |
| Frequency | $F$ | Total detection count |

### 3.2 Normalization

Each feature is normalized against a reference maximum value (set for the video type — e.g., a 90-minute broadcast):

$$D_{norm} = \frac{D}{D_{max}}, \quad C_{norm} = \frac{C}{C_{max}}, \quad Q_{norm} = Q, \quad F_{norm} = \frac{F}{F_{max}}$$

Default reference maxima:
| Reference | Default Value | Config Key |
|-----------|--------------|------------|
| $D_{max}$ | 300 seconds | `MAX_DURATION_SEC` |
| $C_{max}$ | 10% | `MAX_COVERAGE_PCT` |
| $F_{max}$ | 600 detections | `MAX_FREQUENCY` |

All normalized values are **clipped to [0, 1]**.

### 3.3 Weighted Score

$$\text{score} = 100 \times (w_1 \cdot D_{norm} + w_2 \cdot C_{norm} + w_3 \cdot Q_{norm} + w_4 \cdot F_{norm})$$

**Default weights:**

| Weight | Symbol | Default | Meaning |
|--------|--------|---------|---------|
| Duration weight | $w_1$ | `0.40` | Exposure time is most important |
| Coverage weight | $w_2$ | `0.30` | Screen prominence is second |
| Confidence weight | $w_3$ | `0.15` | Detection quality bonus |
| Frequency weight | $w_4$ | `0.15` | Raw appearance count |

> Weights must sum to 1.0. Configurable via `.env`.

---

## 4. USD Estimate

The sponsorship score maps to a USD value via a **linear scale** calibrated to a reference broadcast:

$$\text{USD estimate} = \text{score} \times \frac{\text{BASE\_VALUE\_USD}}{100}$$

**Default:** `BASE_VALUE_USD = 5000` for a 90-minute broadcast.

This means:
- Score 100 → **$5,000**
- Score 50 → **$2,500**
- Score 10 → **$500**

The base value can be adjusted to match real-world market rates (e.g., a major international event vs. a local match).

---

## 5. USD ↔ NPR Conversion

### Static Rate (Fallback)
```
1 USD = 135.00 NPR  (default, configurable)
```

### Live Rate (Optional)
- Fetch from [ExchangeRate-API](https://www.exchangerate-api.com/) or [Open Exchange Rates](https://openexchangerates.org/)
- Endpoint: `GET https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD`
- Key: `rates.NPR`
- Cached for 24 hours to avoid excessive API calls
- Falls back to static rate if request fails

### Conversion Function
```python
def usd_to_npr(usd_value, rate=None):
    if rate is None:
        rate = get_live_rate() or STATIC_NPR_RATE
    return round(usd_value * rate, 2)

def npr_to_usd(npr_value, rate=None):
    if rate is None:
        rate = get_live_rate() or STATIC_NPR_RATE
    return round(npr_value / rate, 2)
```

---

## 6. Input / Output Contract

### Input
| Item | Type | Description |
|------|------|-------------|
| `exposure_report` | `list[dict]` | Output from Module 04 |
| `weights` | `dict` | `{w1, w2, w3, w4}` |
| `base_value_usd` | `float` | Max USD value for score=100 |
| `exchange_rate` | `float` | USD → NPR rate (optional) |

### Output

```json
{
  "sponsor": "NikeLogo",
  "sponsorship_score": 74.3,
  "score_breakdown": {
    "duration_component": 28.0,
    "coverage_component": 22.2,
    "confidence_component": 13.2,
    "frequency_component": 10.9
  },
  "estimated_value_usd": 3715.00,
  "estimated_value_npr": 501525.00,
  "exchange_rate_used": 135.00,
  "currency_note": "NPR value converted at 135.00 NPR/USD"
}
```

---

## 7. Pseudocode

```python
def compute_pricing(exposure_report, weights, base_value_usd=5000,
                    max_duration=300, max_coverage=10.0, max_frequency=600,
                    exchange_rate=None):
    
    w1, w2, w3, w4 = weights["duration"], weights["coverage"], \
                      weights["confidence"], weights["frequency"]
    
    if exchange_rate is None:
        exchange_rate = get_exchange_rate()  # live or static
    
    pricing_results = []
    
    for record in exposure_report:
        # Normalize
        d_norm = min(record["total_exposure_sec"] / max_duration, 1.0)
        c_norm = min((record["avg_screen_coverage_pct"]) / max_coverage, 1.0)
        q_norm = min(record["avg_confidence"], 1.0)
        f_norm = min(record["total_detections"] / max_frequency, 1.0)
        
        # Score
        score = 100 * (w1 * d_norm + w2 * c_norm + w3 * q_norm + w4 * f_norm)
        score = round(score, 2)
        
        usd_value = round(score * base_value_usd / 100, 2)
        npr_value = round(usd_value * exchange_rate, 2)
        
        pricing_results.append({
            "sponsor": record["sponsor"],
            "sponsorship_score": score,
            "score_breakdown": {
                "duration_component": round(w1 * d_norm * 100, 2),
                "coverage_component": round(w2 * c_norm * 100, 2),
                "confidence_component": round(w3 * q_norm * 100, 2),
                "frequency_component": round(w4 * f_norm * 100, 2)
            },
            "estimated_value_usd": usd_value,
            "estimated_value_npr": npr_value,
            "exchange_rate_used": exchange_rate
        })
    
    return sorted(pricing_results, key=lambda x: x["sponsorship_score"], reverse=True)
```

---

## 8. Configuration Parameters

| Parameter | Default | Config Key |
|-----------|---------|-----------|
| Duration weight | `0.40` | `WEIGHT_DURATION` |
| Coverage weight | `0.30` | `WEIGHT_COVERAGE` |
| Confidence weight | `0.15` | `WEIGHT_CONFIDENCE` |
| Frequency weight | `0.15` | `WEIGHT_FREQUENCY` |
| Base USD value | `5000` | `BASE_VALUE_USD` |
| Max duration (s) | `300` | `MAX_DURATION_SEC` |
| Max coverage (%) | `10.0` | `MAX_COVERAGE_PCT` |
| Max frequency | `600` | `MAX_FREQUENCY` |
| Static NPR rate | `135.00` | `STATIC_NPR_RATE` |
| ExchangeRate API key | `""` | `EXCHANGE_RATE_API_KEY` |

All stored in `.env` / `config.py`.

---

## 9. File Outputs

```
data/
└── outputs/
    ├── exposure_report.json     ← from Module 04
    ├── pricing_report.json      ← from this module
    └── pricing_report.csv       ← flat CSV version
```

---

## 10. Limitations & Future Extensions

| Current Limitation | Future Extension |
|--------------------|-----------------|
| Static base USD value | Market-calibrated value by event type/tier |
| Linear model only | ML regression trained on real sponsorship deals |
| No temporal weighting | Prime-time slots could carry higher value multiplier |
| Single currency pair (USD/NPR) | Multi-currency support |
| No audience reach factor | Integrate viewership data for CPM-based pricing |

---

## 11. Dependencies

```
requests (for live exchange rate)
pandas
numpy
json (stdlib)
python-dotenv (for .env config)
```

---

## 12. Next Steps

- [ ] Implement `compute_pricing()` function
- [ ] Implement `get_exchange_rate()` with fallback
- [ ] Unit test: verify weights sum to 1.0 enforcement
- [ ] Unit test: edge case — zero-score sponsor (no detections passed through)
- [ ] Expose weights as adjustable sliders in web UI (advanced mode)

---

*Previous: [04_exposure_analytics.md](04_exposure_analytics.md)*  
*Pipeline end — output feeds into Web Interface.*
