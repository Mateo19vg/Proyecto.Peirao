import requests

# Open-Meteo es gratuita y no requiere API key
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


def get_weather(lat: float, lon: float) -> dict:
    """
    Obtiene el tiempo actual y próximas horas para unas coordenadas.
    Combina datos atmosféricos + datos marinos (temperatura del agua).
    """
    # Parámetros atmosféricos (viento, temperatura aire)
    params_weather = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "wind_speed_10m", "weather_code"],
        "timezone": "Europe/Madrid",
        "forecast_days": 1,
    }

    # Parámetros marinos (temperatura superficie del mar)
    params_marine = {
        "latitude": lat,
        "longitude": lon,
        "current": ["sea_surface_temperature", "wave_height"],
        "timezone": "Europe/Madrid",
    }

    try:
        r_weather = requests.get(OPEN_METEO_URL, params=params_weather, timeout=5)
        r_weather.raise_for_status()
        weather_data = r_weather.json()["current"]

        r_marine = requests.get(MARINE_URL, params=params_marine, timeout=5)
        r_marine.raise_for_status()
        marine_data = r_marine.json()["current"]

        return {
            "temperatura_agua": marine_data.get("sea_surface_temperature"),
            "altura_olas": marine_data.get("wave_height"),
            "velocidad_viento": weather_data.get("wind_speed_10m"),
            "temperatura_aire": weather_data.get("temperature_2m"),
            "codigo_tiempo": weather_data.get("weather_code"),
        }

    except requests.RequestException as e:
        # Devolvemos None para que la vista maneje el error
        return None


def calcular_puntuacion(condiciones: dict, especie) -> dict:
    """
    Compara las condiciones actuales con las óptimas de la especie.
    Devuelve una puntuación de 0 a 100 y un resumen textual.
    """
    if not condiciones:
        return {"puntuacion": 0, "resumen": "No se pudieron obtener datos meteorológicos."}

    puntos = 100
    problemas = []

    temp_agua = condiciones.get("temperatura_agua") or 0
    viento = condiciones.get("velocidad_viento") or 0

    # Penalizar si la temperatura del agua está fuera del rango óptimo
    if temp_agua < especie.temp_agua_min:
        diff = especie.temp_agua_min - temp_agua
        puntos -= min(40, int(diff * 5))
        problemas.append(f"Agua fría ({temp_agua:.1f}°C, óptimo >{especie.temp_agua_min}°C)")

    elif temp_agua > especie.temp_agua_max:
        diff = temp_agua - especie.temp_agua_max
        puntos -= min(40, int(diff * 5))
        problemas.append(f"Agua caliente ({temp_agua:.1f}°C, óptimo <{especie.temp_agua_max}°C)")

    # Penalizar si hay demasiado viento
    if viento > especie.viento_max:
        exceso = viento - especie.viento_max
        puntos -= min(40, int(exceso * 2))
        problemas.append(f"Viento fuerte ({viento:.1f} km/h, máx {especie.viento_max} km/h)")

    puntos = max(0, puntos)

    if puntos >= 75:
        resumen = "✅ Buenas condiciones para pescar"
    elif puntos >= 45:
        resumen = "⚠️ Condiciones aceptables"
    else:
        resumen = "❌ Condiciones desfavorables"

    if problemas:
        resumen += ": " + ", ".join(problemas)

    return {"puntuacion": puntos, "resumen": resumen}


# Mapa simplificado de códigos WMO a texto legible
WMO_CODES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 51: "Llovizna ligera", 61: "Lluvia ligera",
    71: "Nieve ligera", 80: "Chubascos", 95: "Tormenta",
}


def describir_tiempo(codigo: int) -> str:
    return WMO_CODES.get(codigo, f"Código {codigo}")
