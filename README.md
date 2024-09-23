# Weather Data Tracker

This project is a web application that visualizes real-time weather data for multiple cities using Dash, Plotly, Flask, and asynchronous API calls to the OpenWeatherMap API. The application displays temperature and humidity trends over time for a set of cities and updates the data every 15 minutes.

## Current Status

This project is approximately 90% complete. Most of the core features are functional, but a few improvements and bug fixes are still in progress. The primary areas of focus for the final steps include:
- Optimizing the data fetching process for better error handling.
- Ensuring all weather data is properly synchronized and updated at regular intervals.

## Project Structure

- `LocationScriptData/`: Directory for storing weather data in CSV format.
  - `cities_weather_data.csv`: Stores the fetched weather data including city, state, description, temperature, humidity, wind speed, and timestamp.
- `venv/`: Virtual environment for managing project dependencies.
- `.env`: Environment file to store sensitive credentials, such as the OpenWeatherMap API key.
- `LocationScript.py`: Script responsible for fetching weather data asynchronously from the OpenWeatherMap API and saving it to the CSV file.
- `WeatherDataTracker.py`: The main file to run the Flask application with embedded Dash for visualizing the data.

## Deployment

This application is intended to be deployed on an **AWS EC2 instance** using **Gunicorn** as the WSGI server for handling requests in a production environment. 

The setup involves:
1. Launching an EC2 instance.
2. Installing required dependencies (Python, virtual environment, Gunicorn, etc.).
3. Configuring the security group to allow inbound traffic on the necessary port (e.g., 8000 for Gunicorn or 80 if using Nginx as a reverse proxy).
4. Running the application with Gunicorn on EC2.

You can start the server using Gunicorn with the following command:
```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 WeatherDataTracker:flask_app
```
## Features
### 1. Real-Time Weather Data
The application collects weather data for multiple cities from the OpenWeatherMap API and displays it in a visually interactive format.

### 2. Data Visualization
The data for temperature and humidity is visualized using line graphs, allowing users to observe trends over the past 24 hours.

### 3. Asynchronous Data Fetching
Weather data is fetched asynchronously for the cities listed in the `CITIES` dictionary in `LocationScript.py`, with retry logic to handle failed API calls.

### 4. Data Storage
All collected data is stored in a CSV file (`LocationScriptData/cities_weather_data.csv`) for easy access and to maintain historical records.

### 5. Automatic Data Updates
The data is updated every 15 minutes, and the visualizations refresh automatically every 5 seconds.
