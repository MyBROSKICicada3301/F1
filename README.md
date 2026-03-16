# 🏎️ F1 Interactive Dashboard - Pit Wall Tool

A web-based dashboard for exploring historical F1 race data, telemetry, and driver comparisons using **FastF1**, **Streamlit**, and **Pandas**.

## Features

### 🏁 **Race Results**
- View top 10 finishers with points
- Visual bar chart of podium finishers
- Race statistics summary

### 📊 **Driver Analysis**
- Select any driver and view their race statistics
- Lap time progression throughout the race
- Sector-by-sector performance breakdown
- Tire degradation analysis

### ⚔️ **Driver Comparison**
- Compare two drivers' lap times side-by-side
- Identify relative performance gaps
- Lap-by-lap detailed comparison table

### 📈 **Lap Telemetry**
- View detailed telemetry data (speed, throttle, etc.) for any lap
- Slider to select specific laps
- Speed and throttle visualization with distance

### 🛞 **Tire Strategy**
- Analyze tire compounds used by each driver
- Tire age progression throughout the race
- Strategic pit stop patterns

## Tech Stack

- **Python 3.8+** - Core programming language
- **FastF1** - Official F1 data fetching library
- **Streamlit** - Interactive web dashboard
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations
- **Matplotlib & Seaborn** - Data visualization
- **Plotly** - Interactive charts

## Installation

### 1. Clone/Setup Project
```bash
cd d:\FUN\F1
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard
```bash
streamlit run main.py
```

The app will open at `http://localhost:8501` in your browser.

### How to Use
1. **Select Season** - Choose from recent F1 seasons (last 5 years)
2. **Select Grand Prix** - Pick your favorite race
3. **Select Session** - Choose Race (R), Qualifying (Q), or Practice (FP1/FP2/FP3)
4. **Navigate** - Use the sidebar to switch between different analysis views
5. **Explore** - Select drivers and analyze their performance

## Project Structure

```
F1/
├── main.py              # Main Streamlit app and page layouts
├── data_loader.py       # FastF1 data loading and caching
├── visualization.py     # Matplotlib/seaborn plotting functions
├── utils.py            # Helper functions (formatting, season/event fetching)
├── requirements.txt     # Python package dependencies
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Data Caching

The dashboard uses Streamlit caching to speed up repeated queries:
- Session data is cached for 1 hour
- FastF1 local cache stores all downloaded data
- First load may take 10-30 seconds; subsequent loads are instant

## Extended Features (Future Ideas)

- **Predictive Models** - Use scikit-learn to predict race outcomes
- **Season Statistics** - Compare drivers across entire seasons
- **Weather Analysis** - Correlate weather data with performance
- **Monte Carlo Simulations** - Predict championship scenarios
- **Interactive Track Maps** - Fan-animated corner speed visualization
- **Export Reports** - Generate PDF pit wall reports

## Troubleshooting

### Session won't load
- Check internet connection (FastF1 fetches live data)
- Verify the season and event are valid
- Wait a moment and refresh the page

### Slow performance
- First load is slower; subsequent views are cached
- FastF1 cache is stored in `f1_cache/` directory
- Clearing cache: delete the `f1_cache/` folder

### Missing driver data
- Some drivers may have incomplete data for certain sessions
- Practice sessions have fewer drivers than races
- Qualifying sessions may have different participants

## References

- **FastF1 Documentation**: https://docs.fastf1.dev/
- **Streamlit Docs**: https://docs.streamlit.io/
- **F1 Data Guide**: https://f1-api.readthedocs.io/

## License

This project is for educational purposes and uses publicly available F1 data through FastF1.

---

**Happy analyzing! 🏁**
