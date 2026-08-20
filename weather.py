import python_weather
import asyncio


async def get_current_weather(city):
    """Get only current weather for a city"""
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city)

        print(f"\n{'='*45}")
        print(f"  🌍 Current Weather in {city}")
        print(f"{'='*45}")
        print(f"  🌡  Temperature  : {weather.temperature}°C")
        print(f"  🤔 Feels Like   : {weather.feels_like}°C")
        print(f"  🌤  Condition    : {weather.description}")
        print(f"  💧 Humidity     : {weather.humidity}%")
        print(f"  💨 Wind Speed   : {weather.wind_speed} km/h")
        print(f"  🌬  Wind Dir     : {weather.wind_direction}")
        print(f"  👁  Visibility   : {weather.visibility} km")
        print(f"  🔵 Pressure     : {weather.pressure} hPa")
        print(f"  ☁  Cloud Cover  : {weather.cloud_cover}%")
        print(f"  🌧  Precipitation: {weather.precipitation} mm")
        print(f"{'='*45}\n")

        return f"Current weather in {city}: {weather.temperature}°C and {weather.description}. Feels like {weather.feels_like}°C with {weather.humidity}% humidity."


async def get_weather_forecast(city, days=3):
    """Get weather forecast for next 'n' days"""
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city)

        print(f"\n{'='*45}")
        print(f"  📅 {days}-Day Forecast for {city}")
        print(f"{'='*45}")

        forecast_data = []
        for i, forecast in enumerate(weather):
            if i >= days:
                break

            hourly_temps = [hourly.temperature for hourly in forecast]
            low_temp = min(hourly_temps) if hourly_temps else "N/A"
            high_temp = max(hourly_temps) if hourly_temps else "N/A"

            print(f"\n📆 {forecast.date}  |  Avg: {forecast.temperature}°C  |  🔽 Low: {low_temp}°C  |  🔼 High: {high_temp}°C")
            print("-" * 45)
            print("      Hourly time | Temperature |  Humidity  |  Wind Speed  | Description")

            for hourly in forecast:
                print(f"      {str(hourly.time):<8}    |  {hourly.temperature}°C       |   {hourly.humidity}%      |  {hourly.wind_speed:2} km/h     | {hourly.description}")

            forecast_data.append(f"{forecast.date}: Low {low_temp}°C, High {high_temp}°C, {forecast.description}")

        print(f"{'='*45}\n")
        return forecast_data


async def full_weather_report(city):
    """Get both current weather and 3-day forecast"""
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city)

        # Current weather
        print(f"\n{'='*45}")
        print(f"  🌍 Weather Report for {city}")
        print(f"{'='*45}")
        print(f"  🌡  Temperature  : {weather.temperature}°C")
        print(f"  🤔 Feels Like   : {weather.feels_like}°C")
        print(f"  🌤  Condition    : {weather.description}")
        print(f"  💧 Humidity     : {weather.humidity}%")
        print(f"  💨 Wind Speed   : {weather.wind_speed} km/h")
        print(f"  🌬  Wind Dir     : {weather.wind_direction}")
        print(f"  👁  Visibility   : {weather.visibility} km")
        print(f"  🔵 Pressure     : {weather.pressure} hPa")
        print(f"  ☁  Cloud Cover  : {weather.cloud_cover}%")
        print(f"  🌧  Precipitation: {weather.precipitation} mm")

        # 3-day + hourly forecast
        print(f"\n{'='*45}")
        print("  📅 3-Day Hourly Forecast")
        print(f"{'='*45}")

        for forecast in weather:
            # Calculate lowest and highest temp from hourly data
            hourly_temps = [hourly.temperature for hourly in forecast]
            low_temp  = min(hourly_temps) if hourly_temps else "N/A"
            high_temp = max(hourly_temps) if hourly_temps else "N/A"

            print(f"\n📆 {forecast.date}  |  Avg: {forecast.temperature}°C  |  🔽 Low: {low_temp}°C  |  🔼 High: {high_temp}°C")
            print("-" * 45)
            print("      Hourly time | Temperature |  Humidity  |  Wind Speed  | Description")

            for hourly in forecast:
                print(f"      {str(hourly.time):<8}    |  {hourly.temperature}°C       |   {hourly.humidity}%      |  {hourly.wind_speed:2} km/h     | {hourly.description}")


