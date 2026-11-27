# Bike Rental Demand Analysis

This project analyzes and predicts hourly bike rental demand using the UCI Bike Sharing Dataset for the Capital Bikeshare system in Washington, DC. The complete exploratory analysis, preprocessing, feature engineering, modeling, and evaluation workflow is documented in `bike_rentals_analysis.ipynb`.

## Objectives

- Explore patterns in hourly bike rental demand.
- Compare weekday and working-day rental behavior.
- Identify the influence of weather, temperature, season, and time of day.
- Engineer features that capture nonlinear and cyclical demand patterns.
- Compare a baseline model with linear and ensemble machine learning models.
- Evaluate models using chronological validation to avoid future-data leakage.

## Dataset

The project uses the UCI Bike Sharing Dataset, covering 2011–2012 and containing 17,379 hourly observations.

The target variable is `cnt`, representing the total number of bike rentals during an hour:

- `casual`: rentals by non-registered users
- `registered`: rentals by registered users
- `cnt = casual + registered`

The analysis uses the following categories of features:

- Time: hour, month, year, weekday, season, and holiday
- Calendar status: working day
- Weather: temperature, apparent temperature, humidity, and wind speed
- Weather conditions: clear, mist, light rain/snow, or heavy weather

## Project Workflow

### 1. Data loading

The notebook downloads the data from the UCI repository with `ucimlrepo`. If internet access is unavailable, `hour.csv` can be downloaded manually and placed in the same folder as the notebook.

### 2. Data preprocessing

- Removed `casual` and `registered` from the modeling features because both directly determine `cnt`, which would cause target leakage.
- Removed `instant`, a row identifier with no predictive value.
- Converted normalized temperature, humidity, and wind-speed values to their documented real-world scales.
- Created a datetime field to support chronological splitting and time-based analysis.

### 3. Exploratory data analysis

The notebook examines:

- The distribution of hourly rental counts
- Demand differences between working and non-working days
- Commuter rush-hour peaks
- Temperature and rental-demand relationships
- The effects of weather conditions
- Growth in rentals between 2011 and 2012
- Correlations among numeric features

The analysis also identifies strong correlation between `temp` and `atemp`, so only temperature is retained for modeling.

### 4. Feature engineering

The model dataset contains 20 features, including:

- Cyclical representations of hour using sine and cosine
- A rush-hour indicator for commuter periods on working days
- Hour × working-day interaction
- Squared temperature to model nonlinear temperature effects
- One-hot encoded season and weather categories
- A log-transformed target, `log(cnt + 1)`

### 5. Modeling

The data is split chronologically:

- Training period: before October 1, 2012
- Test period: October–December 2012

This prevents the model from seeing future observations. The models compared are:

| Model | Purpose |
|---|---|
| Hourly average baseline | Predicts demand using the training-period average for each hour and working-day combination |
| Linear Regression | Establishes a simple linear benchmark |
| Random Forest | Captures nonlinear feature interactions |
| HistGradientBoosting | Provides an efficient nonlinear boosting baseline |

Predictions are converted from the log scale back to rental counts before evaluation.

## Evaluation

The primary test metrics are:

- **RMSE:** penalizes large prediction errors
- **MAE:** measures average absolute prediction error
- **R²:** measures the proportion of target variance explained by the model

The training period is also evaluated with five-fold time-series cross-validation. Additional analyses compare predicted and actual rentals for a test week, measure error by hour, and calculate permutation feature importance.

## Tools and Libraries

- Python
- pandas and NumPy
- Matplotlib
- scikit-learn
- ucimlrepo

## Setup

Install the required packages:

```bash
pip install ucimlrepo pandas numpy matplotlib scikit-learn
```

Open and run the notebook from the project directory:

```bash
jupyter notebook bike_rentals_analysis.ipynb
```

Run all cells from top to bottom. The notebook creates a `figures/` directory containing generated charts and a results table.

## Generated Outputs

The notebook saves the following analysis artifacts:

- Target and feature distributions
- Working-day versus non-working-day demand charts
- Temperature and weather plots
- Time trends and correlations
- Predicted versus actual rentals
- Mean absolute error by hour
- Permutation feature importance
- `figures/results_table.csv`

## Limitations

- Recorded rentals do not represent unmet demand when stations are empty or full.
- The dataset represents one bike-sharing system and may not generalize directly to another city.
- Two years of data limits the ability to model long-term growth and rare events.
- Heavy-rain observations are relatively limited.
- The model excludes special events and external event data that may affect demand.

## Possible Extensions

- Model casual and registered rentals separately
- Include weather forecasts, events, and public-holiday information
- Test the approach on another city's bike-sharing data
- Improve peak-hour performance with segment-specific models
- Compare seasonal or geographically aware validation strategies

## Dataset Reference

Fanaee-T, Hadi, and Gama, Joao. *Bike Sharing Dataset*. UCI Machine Learning Repository.

https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
