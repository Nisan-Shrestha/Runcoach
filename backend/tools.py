from datetime import datetime
from langchain_core.tools import tool
from typing import Optional
import requests


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the running knowledge base for information about training, nutrition, 
    injury prevention, form, and race preparation.
    
    Use this tool when you need specific information about running topics.
    
    Args:
        query: The search query about running topics
    
    Returns:
        Relevant information from the knowledge base
    """
    from rag import rag  # Import here to avoid circular imports
    try:
        context, sources = rag.search(query, k=3)
        return context
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


@tool
def get_weather(location: str) -> str:
    """
    Get current weather and forecast for a location to help plan runs.
    Use this tool when the user asks about weather, whether they should run today,
    or wants to plan runs around weather conditions.
    
    Args:
        location: City name (e.g., "London" or "Kathmandu")
    """
    try:
        # Get detailed weather data from wttr.in
        response = requests.get(
            f"https://wttr.in/{location}?format=j1",
            timeout=10
        )
        
        if response.status_code != 200:
            return f"Could not get weather for {location}. Check the city name."
        
        data = response.json()
        current = data["current_condition"][0]
        
        # Parse current conditions
        temp = int(current["temp_C"])
        feels_like = int(current["FeelsLikeC"])
        humidity = int(current["humidity"])
        wind = int(current["windspeedKmph"])
        description = current["weatherDesc"][0]["value"]
        
        # Build current weather section
        result = f"""🌤️ WEATHER FOR {location.upper()}

CURRENT CONDITIONS:
• Conditions: {description}
• Temperature: {temp}°C (feels like {feels_like}°C)
• Humidity: {humidity}%
• Wind: {wind} km/h

{get_running_recommendation(temp, humidity, wind, description)}
"""
        
        # Get 3-day forecast
        if "weather" in data and len(data["weather"]) > 0:
            result += "\n📅 FORECAST FOR PLANNING:\n"
            
            for i, day in enumerate(data["weather"][:3]):
                date = day["date"]
                
                # Parse date for nice formatting
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A, %b %d")
                
                # Get midday conditions (index 4 = noon)
                if len(day["hourly"]) > 4:
                    noon = day["hourly"][4]
                else:
                    noon = day["hourly"][0]
                
                f_temp = int(noon["tempC"])
                f_feels = int(noon["FeelsLikeC"])
                f_humidity = int(noon["humidity"])
                f_wind = int(noon["windspeedKmph"])
                f_desc = noon["weatherDesc"][0]["value"]
                f_rain = noon.get("chanceofrain", "0")
                
                best_time = get_best_run_time(f_temp, f_humidity)
                
                rain_str = f" | Rain chance: {f_rain}%" if int(f_rain) > 20 else ""
                
                result += f"\n{day_name}:\n"
                result += f"  • {f_desc}, {f_temp}°C (feels {f_feels}°C)\n"
                result += f"  • Humidity: {f_humidity}% | Wind: {f_wind} km/h{rain_str}\n"
                result += f"  • Best time to run: {best_time}\n"
        
        return result
    
    except Exception as e:
        return f"Weather service error: {str(e)}"


def get_running_recommendation(temp: float, humidity: float, wind: float, description: str) -> str:
    """Generate running-specific recommendations based on weather"""
    recommendations = []
    warnings = []
    
    # Temperature analysis
    if temp < 0:
        warnings.append("⚠️ Very cold - risk of hypothermia")
        recommendations.append("Wear multiple layers, cover extremities")
    elif temp < 10:
        recommendations.append("Cool weather - good for performance, wear layers")
    elif 10 <= temp <= 15:
        recommendations.append("✅ Ideal running temperature!")
    elif 15 < temp <= 20:
        recommendations.append("✅ Great conditions for running")
    elif 20 < temp <= 25:
        recommendations.append("Warm - stay hydrated, consider early morning run")
    elif 25 < temp <= 30:
        warnings.append("⚠️ Hot conditions - reduce intensity")
        recommendations.append("Run early morning or evening, bring water")
    else:
        warnings.append("🛑 Dangerous heat - consider indoor workout")
        recommendations.append("If you must run: dawn only, hydrate heavily")
    
    # Humidity analysis
    if humidity > 80:
        warnings.append("⚠️ High humidity - sweat won't evaporate well")
        recommendations.append("Reduce pace, hydrate extra")
    elif humidity < 30:
        recommendations.append("Low humidity - hydrate well")
    
    # Wind analysis  
    if wind > 30:
        warnings.append("⚠️ Strong winds - running will be harder")
        recommendations.append("Start into the wind, return with it at your back")
    elif wind > 20:
        recommendations.append("Moderate wind - factor into your route planning")
    
    # Rain/conditions
    desc_lower = description.lower()
    if "rain" in desc_lower or "drizzle" in desc_lower:
        recommendations.append("Wet conditions - wear visibility gear, avoid slippery surfaces")
    if "thunder" in desc_lower or "storm" in desc_lower:
        warnings.append("🛑 Storm conditions - DO NOT run outdoors")
    if "snow" in desc_lower:
        warnings.append("⚠️ Snow - watch for ice, shorten stride")
    
    # Build output
    output = "🏃 RUNNING RECOMMENDATION:\n"
    
    if warnings:
        output += "\n".join(warnings) + "\n"
    
    if recommendations:
        output += "\n".join(f"• {r}" for r in recommendations)
    
    return output


def get_best_run_time(temp: float, humidity: float) -> str:
    """Suggest best time to run based on conditions"""
    if temp > 25:
        return "Early morning (5-7 AM) or evening (after 6 PM)"
    elif temp > 20:
        return "Morning (6-9 AM) or evening (5-7 PM)"
    elif temp < 5:
        return "Midday (11 AM - 2 PM) when warmest"
    else:
        return "Anytime - conditions are favorable"


@tool
def calculate_nutrition(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str = "male",
    activity_level: str = "moderate"
) -> str:
    """
    Calculate BMR, TDEE, and macro recommendations for a runner.
    
    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: "male" or "female"
        activity_level: "sedentary", "light", "moderate", "active", or "very_active"
    """
    # Mifflin-St Jeor BMR formula
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multipliers
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    
    # Runner-specific macros (higher carbs for endurance)
    protein_g = weight_kg * 1.6  # 1.6g per kg for runners
    carbs_g = (tdee * 0.55) / 4  # 55% from carbs
    fat_g = (tdee * 0.25) / 9    # 25% from fat
    
    return f"""Nutrition Calculator Results:

📊 Basic Stats:
- BMR (Basal Metabolic Rate): {bmr:.0f} calories/day
- TDEE (Total Daily Energy): {tdee:.0f} calories/day

🍽️ Recommended Daily Macros for Runners:
- Protein: {protein_g:.0f}g ({protein_g * 4:.0f} cal)
- Carbohydrates: {carbs_g:.0f}g ({carbs_g * 4:.0f} cal)  
- Fat: {fat_g:.0f}g ({fat_g * 9:.0f} cal)

💡 Tips:
- Eat carbs 2-3 hours before runs
- Protein within 30 min post-run for recovery
- Stay hydrated: aim for {weight_kg * 35:.0f}ml water daily"""


@tool
def calculate_pace(
    distance_km: float,
    time_minutes: float,
    target_distance: Optional[float] = None
) -> str:
    """
    Calculate running pace and predict race times.
    
    Args:
        distance_km: Distance run in kilometers
        time_minutes: Time taken in minutes
        target_distance: Optional target race distance in km to predict time
    """
    # Calculate pace
    pace_per_km = time_minutes / distance_km
    pace_min = int(pace_per_km)
    pace_sec = int((pace_per_km - pace_min) * 60)
    
    # Speed
    speed_kmh = (distance_km / time_minutes) * 60
    
    result = f"""Pace Analysis:

⏱️ Your Stats:
- Distance: {distance_km:.2f} km
- Time: {int(time_minutes)} min {int((time_minutes % 1) * 60)} sec
- Pace: {pace_min}:{pace_sec:02d} per km
- Speed: {speed_kmh:.1f} km/h

🏆 Race Time Predictions (based on current pace):
- 5K: {format_time(pace_per_km * 5)}
- 10K: {format_time(pace_per_km * 10)}
- Half Marathon: {format_time(pace_per_km * 21.1)}
- Marathon: {format_time(pace_per_km * 42.2)}"""
    
    if target_distance:
        predicted = pace_per_km * target_distance
        result += f"\n\n🎯 Target {target_distance}km: {format_time(predicted)}"
    
    return result


def format_time(minutes: float) -> str:
    """Format minutes to HH:MM:SS"""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    secs = int((minutes * 60) % 60)
    
    if hours > 0:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def get_all_tools():
    """Return list of all available tools"""
    return [
        search_knowledge_base,
        get_weather,
        calculate_nutrition,
        calculate_pace
    ]
