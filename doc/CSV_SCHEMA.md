# CSV Schema

| Column | Type | Description |
|---|---|---|
| facility_id | text | Facility identifier |
| region | text | Facility region |
| chemical_category | text | Broad chemical category |
| inventory_volume_tons | numeric | Stored inventory |
| storage_condition_score | numeric | Storage condition score 0–100 |
| containment_score | numeric | Containment score 0–100 |
| weather_exposure_index | numeric | Local exposure indicator |
| inspection_score | numeric | Inspection score 0–100 |
| nearby_population | numeric | Nearby population indicator |
| transfer_frequency_30d | numeric | Transfer activity count |
| days_since_inspection | numeric | Days since inspection |
| container_age_years | numeric | Storage-container age |
| leak_history_24m | numeric | Historical leak signal count |
| chemical_hazard_index | numeric | Local hazard indicator |
| temperature_excursion_count | numeric | Temperature excursion count |
| longitude | numeric | Local map coordinate |
| latitude | numeric | Local map coordinate |
| record_date | date | Observation date |
