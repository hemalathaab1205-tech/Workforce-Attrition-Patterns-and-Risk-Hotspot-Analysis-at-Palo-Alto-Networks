# Palo Alto Networks — Workforce Attrition Dashboard

## Project Files

| File | Description |
|------|-------------|
| `paloalto_attrition_dashboard.py` | Streamlit dashboard (main app) |
| `Palo_Alto_Networks.csv` | Employee dataset (place in same folder) |
| `PaloAlto_Attrition_Report.docx` | Full research paper / EDA report |
| `requirements.txt` | Python dependencies |

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your CSV in the same folder as the .py file

# 3. Run the dashboard
streamlit run paloalto_attrition_dashboard.py
```

The app opens at http://localhost:8501

## Dashboard Modules

- **Overview** — Overall attrition KPIs + department heatmap
- **Dept & Role** — Attrition by department and all 9 job roles
- **Demographics** — Age, gender, marital status, education field
- **Tenure & Career** — Tenure buckets, promotion stagnation, job level
- **Workload** — Overtime impact, travel frequency, satisfaction scores

## Sidebar Filters

All charts respond to these sidebar controls:
- Department selector
- Job role filter
- Tenure range slider
- Overtime toggle
- Business travel filter

## Key Findings

| Risk | Segment | Rate |
|------|---------|------|
| CRITICAL | Sales Representatives | 39.8% |
| HIGH | Lab Technicians | 23.9% |
| HIGH | 0-1 year tenure | 34.9% |
| HIGH | Overtime workers | 30.5% |
| HIGH | 18-25 age group | 34.8% |
| HIGH | Frequent travelers | 24.9% |
