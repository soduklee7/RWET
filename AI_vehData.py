# Prompt: "Write a Python class EmissionComplianceChecker.
# The __init__ method should accept a DataFrame and a dictionary of regulatory thresholds (e.g., {'NOx': 0.08, 'CO2': 150}).
# Include a method to check which vehicles pass/fail compliance.
# Include a method to generate a report summarizing the percentage of passing vehicles by manufacturer."
# - Provide a method to filter data based on driving conditions (e.g., urban vs. highway speeds).
# Focus on accuracy for time-series data using numpy and pandas."
# - Include a method to predict emissions for a new vehicle input.
# - Use train_test_split to create validation data.

class EmissionComplianceChecker:
    def __init__(self, df, thresholds):
        """
        df: DataFrame with vehicle data
        thresholds: dict, e.g., {'NOx': 0.08, 'CO2': 150}
        """
        self.df = df
        self.thresholds = thresholds

    def check_compliance(self):
        """Adds a 'Pass' column to the dataframe"""
        self.df['Pass'] = True
        for param, limit in self.thresholds.items():
            if param in self.df.columns:
                self.df['Pass'] &= (self.df[param] <= limit)
        return self.df

    def generate_report(self):
        if 'Pass' not in self.df.columns:
            self.check_compliance()
            
        report = self.df.groupby('Manufacturer')['Pass'].agg(
            Total_Vehicles='count',
            Passing_Count='sum',
            Pass_Percentage=lambda x: (x.sum() / x.count()) * 100)
        return report


# Write a Python class named EmissionPredictor using scikit-learn. The class should:
# - Accept a pandas DataFrame.
# - Preprocess data (handle categorical variables, feature scaling).
# - Train a Linear Regression or Random Forest model to predict 'CO2_Emissions', 'NOx', 'NMHC', 'CO', and "PM" based on features like 'Engine_Size', 'Cylinders', and 'Fuel_Consumption'.
# - Include a method to evaluate the model using Moving Average Window, R-squared and Mean Absolute Error (MAE).

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score

class EmissionPredictor:
    def __init__(self, model_type='rf'):
        self.targets = ['CO2_Emissions', 'NOx', 'NMHC', 'CO', 'PM']
        self.features = ['Engine_Size', 'Cylinders', 'Fuel_Consumption']
        
        # Define the model pipeline
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.features)
            ], remainder='drop')
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.pipeline = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('regressor', MultiOutputRegressor(model))
        ])

    def train(self, df):
        X = df[self.features]
        y = df[self.targets]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.pipeline.fit(X_train, y_train)
        return X_test, y_test

    def predict(self, input_data):
        """Predict emissions for a new vehicle input (DataFrame or dict)"""
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        return self.pipeline.predict(input_data)

    def evaluate(self, X_test, y_test, window=5):
        predictions = self.pipeline.predict(X_test)
        
        # Standard Metrics
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # Moving Average Window of Residuals (Smoothing error over samples)
        residuals = np.abs(y_test.values - predictions)
        ma_residuals = pd.DataFrame(residuals).rolling(window=window).mean().dropna()
        
        print(f"Overall MAE: {mae:.4f}")
        print(f"Overall R-squared: {r2:.4f}")
        return {"MAE": mae, "R2": r2, "Moving_Avg_Residuals": ma_residuals}

# "Generate a Python class OBDEmissionProcessor for analyzing second-by-second vehicular emission data. It should:
# - Parse timestamped data (CO2, NOx, Speed, RPM).
# - Calculate the total mass of emissions emitted over a trip (integration of instantaneous emission rates).
# - Calculate average speed and emission factors (grams per mile).

class OBDEmissionProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        self.df = self.df.sort_values('Timestamp')

    def filter_conditions(self, mode='urban'):
        """Filters data: Urban (< 45 mph) or Highway (>= 45 mph)"""
        if mode == 'urban':
            return self.df[self.df['Speed'] < 45]
        return self.df[self.df['Speed'] >= 45]

    def calculate_trip_metrics(self):
        # Calculate time delta in seconds
        dt = self.df['Timestamp'].diff().dt.total_seconds().fillna(0)
        
        # Total Mass (Integration: Rate * Time)
        # Assuming emission columns are in grams/sec
        results = {}
        for gas in ['CO2', 'NOx']:
            results[f'Total_{gas}_g'] = np.trapz(self.df[gas], dx=dt.mean() if dt.mean() > 0 else 1)
            
        # Distance calculation (Speed is in mph, convert to miles per second)
        dist_miles = (self.df['Speed'] / 3600 * dt).sum()
        
        results['Avg_Speed'] = self.df['Speed'].mean()
        results['Distance_Miles'] = dist_miles
        
        # Emission Factors (g/mile)
        if dist_miles > 0:
            results['CO2_g_per_mile'] = results['Total_CO2_g'] / dist_miles
            results['NOx_g_per_mile'] = results['Total_NOx_g'] / dist_miles
            
        return results
How to use it:

# Initialize
analyzer = VehicleEmissionAnalyzer('fuel_consumption_data.csv')

# Process
analyzer.clean_data()

# Analyze
stats = analyzer.calculate_summary_statistics()
high_emitters = analyzer.identify_outliers(threshold_std=2.5)

# Visualize
analyzer.plot_engine_vs_co2()



