# TN-Election-Data-Analysis-and-Visualization-2026



## Overview
This repository contains the comprehensive data analysis and visualization suite for the 2026 Tamil Nadu Legislative Assembly Elections. The project aims to provide a neutral, data-driven narrative surrounding the political shift, centered on the debut of the TVK and the subsequent restructuring of the state's electoral landscape.

## The Narrative
The 2026 election marked a pivot from a two-party dominance to a tripartite system. By analyzing 234 constituencies, this project visualizes how 163 seats changed hands, how winning margins compressed, and the statistical impact of the new political entrants.

## Project Deliverables
- **`tn_election_analysis.py`**: Reproducible Python script used for data cleaning, statistical modeling, and chart generation.
- **`dashboard.html`**: A standalone, dark-themed interactive dashboard featuring live-ticker stats and responsive visualizations.
- **`TN_Election_2026_Methodology.docx`**: Technical log detailing code logic, library choices, and data handling decisions.
- **`TN_Election_2026_AtliQ.pptx`**: Editorial presentation deck for stakeholder communication.

## Tech Stack
- **Data Manipulation**: `pandas`, `numpy`
- **Visualization**: `matplotlib`, `seaborn` (for static generation), `Chart.js` (for dashboard interactivity)
- **Design**: CSS3 (Flexbox/Grid), HTML5

## How to Run
1. Ensure you have Python installed.
2. Install requirements: `pip install pandas matplotlib seaborn`.
3. Run the analysis: `python tn_election_analysis.py`.
4. Open `dashboard.html` in any modern web browser to view the interactive insights.

## Methodology
For detailed explanations on data joining, join-keys (using `ac_number`), and our neutrality framework, please refer to the `TN_Election_2026_Methodology.docx` file.
