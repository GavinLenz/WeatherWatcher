import time
import os
from datetime import datetime
import aiohttp
import asyncio
import logging
import pandas as pd
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
CITIES = {
    "California": "San Francisco",
    "Colorado": "Denver",
    "Florida": "Miami",
    "Illinois": "Chicago",
    "Massachusetts": "Boston",
    "North Carolina": "Raleigh",
    "North Dakota": "Bismarck",
    "New York": "New York",
    "Texas": "Austin",
    "Washington": "Seattle"
}
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
CSV_FILE_PATH = 'LocationScriptData/cities_weather_data.csv'
MAX_RETRIES = 3
RETRY_DELAY = 5
FULL_CYCLE_DELAY = 15 * 60

# Load environment variables
load_dotenv()
API_KEY = os.getenv('WEATHER_API_KEY')

if not API_KEY:
    raise ValueError("API key not found. Make sure the 'WEATHER_API_KEY' environment variable is set.")

# Ensure the directory exists
os.makedirs('LocationScriptData', exist_ok=True)

# Initialize CSV file with columns if it doesn't exist
if not os.path.exists(CSV_FILE_PATH):
    columns = ['City', 'State', 'Description', 'Temperature (°F)', 'Humidity (%)', 'Wind Speed (mph)', 'Timestamp']
    df = pd.DataFrame(columns=columns)
    df.to_csv(CSV_FILE_PATH, index=False)

async def fetch_weather_data_async(session, city, state):
    """Fetch weather data for a given city and state asynchronously."""
    url = f'{BASE_URL}q={city},{state}&appid={API_KEY}&units=imperial'
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    'City': data['name'],
                    'State': state,
                    'Description': data['weather'][0]['description'],
                    'Temperature (°F)': data['main']['temp'],
                    'Humidity (%)': data['main']['humidity'],
                    'Wind Speed (mph)': round(data['wind']['speed'] * 2.23694, 1), # mph conversion
                    'Timestamp': datetime.fromtimestamp(data['dt']).astimezone().isoformat()
                }
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.warning(f"Attempt {attempt + 1} failed for {city}, {state}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                logging.error(f"Failed to retrieve data for {city}, {state} after {MAX_RETRIES} attempts.")
                return None

async def update_weather_data_async():
    """Fetch and update weather data for all cities asynchronously."""
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for state, city in CITIES.items():
                # Await the result of the async call and append to the list
                tasks.append(asyncio.create_task(fetch_weather_data_async(session, city, state)))
                await asyncio.sleep(5)

            results = await asyncio.gather(*tasks)

            new_data = [result for result in results if result is not None]
            df = pd.DataFrame(new_data)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.tz_localize(None)
            df.dropna(subset=['Timestamp'], inplace=True)
            df = df.dropna(how='all')

            if os.path.exists(CSV_FILE_PATH):
                existing_df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Timestamp'])
                existing_df['Timestamp'] = pd.to_datetime(existing_df['Timestamp'], errors='coerce').dt.tz_localize(
                    None)
                existing_df.dropna(subset=['Timestamp'], inplace=True)
                existing_df = existing_df.dropna(how='all')
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['City', 'Timestamp'], keep='last')

            df.sort_values('Timestamp', inplace=True)
            df.to_csv(CSV_FILE_PATH, index=False)

            logging.info("Completed one cycle. Waiting 15 minutes for the next round.")
            time.sleep(FULL_CYCLE_DELAY)


# To run the function, you'd need to wrap it in an asyncio event loop like so:
def update_weather_data():
    """Wrapper function to run the asynchronous update_weather_data_async function."""
    try:
        asyncio.run(update_weather_data_async())
    except Exception as e:
        logging.error(f"Error in update_weather_data: {str(e)}")


update_weather_data()