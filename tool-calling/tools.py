from langchain.tools import BaseTool
from typing import Optional, Type
import requests
import math
import os
from dotenv import load_dotenv

load_dotenv()

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """
    Useful for performing mathematical calculations.
    The input should be a mathematical expression like "2 + 2", "5 * 3", "sin(30)", "sqrt(16)", etc.
    """
    
    def _run(self, query: str) -> str:
        """Execute the calculator functionality."""
        try:
            # Create a safe namespace for eval
            safe_dict = {
                'abs': abs, 'max': max, 'min': min, 'pow': pow, 
                'round': round, 'sum': sum,
                # Math functions
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
                'log': math.log, 'log10': math.log10, 'exp': math.exp
            }
            
            # Replace '^' with '**' for exponentiation
            query = query.replace('^', '**')
            
            # Evaluate the expression using the safe namespace
            result = eval(query, {"__builtins__": {}}, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async implementation of the calculator."""
        return self._run(query)


class WeatherTool(BaseTool):
    name: str = "weather_info"
    description: str = """
    Useful for getting current weather information for a specific location.
    The input should be a city name, optionally followed by a country code.
    Example: "London,UK" or "Tokyo" or "New York,US"
    """
    
    def _run(self, location: str) -> str:
        """Get current weather for the specified location."""
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                return "Error: OpenWeather API key not found. Please set OPENWEATHER_API_KEY environment variable."
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code != 200:
                return f"Error: Could not retrieve weather data. Status code: {response.status_code}"
            
            data = response.json()
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            
            return f"""
            Weather in {location}:
            - Condition: {weather_desc}
            - Temperature: {temp}°C
            - Humidity: {humidity}%
            - Wind Speed: {wind_speed} m/s
            """
        except Exception as e:
            return f"Error retrieving weather data: {str(e)}"
    
    async def _arun(self, location: str) -> str:
        """Async implementation of the weather tool."""
        return self._run(location)