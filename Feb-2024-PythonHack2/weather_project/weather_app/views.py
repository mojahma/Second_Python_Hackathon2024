import datetime
import requests
from django.shortcuts import render

# Function to fetch weather and forecast data for a given city
def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    
    # Check if 'coord' key exists in the response
    if 'coord' not in response:
        # If 'coord' key is missing, return None for weather data and daily forecasts
        return None, None
    
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(city, api_key)).json()
    
    print(forecast_response)  # Print the forecast response JSON
    
    # Extract current weather data
    weather_data = {
        "city": city,
        "temperature": round(response['main']['temp'] - 273.15, 2),  # Convert temperature to Celsius
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon'],
    }
    
    # Extract daily forecasts if the response structure is different
    if 'daily' not in forecast_response and 'list' in forecast_response:
        daily_forecasts = []
        for forecast_data in forecast_response['list']:
            # Extract only the forecast data for the next five days
            if len(daily_forecasts) < 5:
                daily_forecasts.append({
                    "day": datetime.datetime.fromtimestamp(forecast_data['dt']).strftime("%A"),
                    "min_temp": round(forecast_data['main']['temp_min'] - 273.15, 2),  # Convert temperature to Celsius
                    "max_temp": round(forecast_data['main']['temp_max'] - 273.15, 2),  # Convert temperature to Celsius
                    "description": forecast_data['weather'][0]['description'],
                    "icon": forecast_data['weather'][0]['icon'],
                })
    else:
        # Extract daily forecasts for the next 5 days if 'daily' key exists
        daily_forecasts = []
        for daily_data in forecast_response['daily'][:5]:
            daily_forecasts.append({
                "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
                "min_temp": round(daily_data['temp']['min'] - 273.15, 2),  # Convert temperature to Celsius
                "max_temp": round(daily_data['temp']['max'] - 273.15, 2),  # Convert temperature to Celsius
                "description": daily_data['weather'][0]['description'],
                "icon": daily_data['weather'][0]['icon'],
            })

    return weather_data, daily_forecasts

# View function for rendering index page
def index(request):
    API_KEY = '8768cfc7e60a030a92dcd51edfc606a8'
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}"
    
    if request.method == "POST":
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)
        
        # Fetch weather data and forecast for the first city
        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)
        
        # Fetch weather data and forecast for the second city if provided
        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_url)
        else:
            weather_data2, daily_forecasts2 = None, None
            
        context = {
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
            "weather_data2": weather_data2,
            "daily_forecasts2": daily_forecasts2
        }
        return render(request, "weather_app/index.html", context)
             
    else: 
        return render(request, "weather_app/index.html")
