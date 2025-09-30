# Pokemon Data Analysis Dashboard

## Project Overview
This project demonstrates a complete data analysis workflow:
- Fetching raw data from an external API
- Cleaning and transforming the data into an analysis-ready format
- Building an interactive dashboard to explore insights

Although the dataset is based on Pokemon, the process reflects real-world data analytics tasks such as handling raw API data, preparing clean datasets, and developing visualizations to support decision-making.

## Tools and Technologies
- Python (pandas, requests, plotly, dash)
- JSON and CSV data formats
- Data cleaning and transformation
- Interactive dashboard development

## Data Pipeline
1. **Data Collection**
   - `fetch_data1.py` retrieves data from the PokeAPI.
   - Raw JSON files are stored (`raw_pokemon.json`, `raw_species.json`, `raw_evolutions.json`).

2. **Data Cleaning**
   - `clean_data1.py` processes raw JSON data into `cleaned_pokemon.csv`.
   - Cleaning steps include:
     - Flattening nested JSON
     - Handling missing values
     - Converting data types
     - Normalizing attributes and statistics

3. **Analysis and Dashboard**
   - `app.py` (dashboard application) loads the cleaned dataset.
   - Interactive visualizations are created using Dash and Plotly.

## Features
- Browse Pokemon data by image and name
- View individual details such as stats, type distribution, and evolutions
- Compare two Pokemon side by side
- Explore global insights such as distributions, correlations, and type frequencies

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pokemon-dashboard.git
   cd pokemon-dashboard
