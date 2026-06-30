"""
services.py — O Peirao
Sistema de puntuación multifactor para condiciones de pesca.

Factores y pesos:
  - Temperatura del agua   20 pts
  - Viento                 15 pts
  - Estado del mar         15 pts  (altura de olas)
  - Fase lunar             20 pts
  - Mareas                 20 pts  (momento del ciclo)
  - Claridad del agua      10 pts  (aproximada por lluvia + olas)
  Total máximo:           100 pts
"""

import math
import requests
from datetime import datetime, timezone

# URLs de Open-Meteo 

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


# OBTENCIÓN DE DATOS METEOROLÓGICOS Y MARINOS

def get_weather_range(lat: float, lon: float) -> dict | None:
    """
    Obtiene las condiciones por horas para un rango de 15 días:
    7 días al pasado, el día actual y 7 días al futuro.
    """
    params_weather = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "wind_speed_10m", "weather_code", "precipitation"],
        "timezone": "Europe/Madrid",
        "past_days": 7,
        "forecast_days": 8,  
    }
    params_marine = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["sea_surface_temperature", "wave_height", "wave_period"],
        "timezone": "Europe/Madrid",
        "past_days": 7,
        "forecast_days": 8,
    }

    try:
        r_w = requests.get(OPEN_METEO_URL, params=params_weather, timeout=5)
        r_w.raise_for_status()
        wd_hourly = r_w.json()["hourly"]

        r_m = requests.get(MARINE_URL, params=params_marine, timeout=5)
        r_m.raise_for_status()
        md_hourly = r_m.json()["hourly"]

        return {
            "timestamps":        wd_hourly.get("time", []),
            "temperatura_aire":  wd_hourly.get("temperature_2m", []),
            "velocidad_viento":  wd_hourly.get("wind_speed_10m", []),
            "codigo_tiempo":     wd_hourly.get("weather_code", []),
            "precipitacion":     wd_hourly.get("precipitation", []),
            "temperatura_agua":  md_hourly.get("sea_surface_temperature", []),
            "altura_olas":       md_hourly.get("wave_height", []),
            "periodo_olas":      md_hourly.get("wave_period", []),
        }

    except requests.RequestException:
        return None


# FASE LUNAR

def calcular_fase_lunar(dt: datetime = None) -> dict:
    """
    Calcula la fase lunar actual mediante fórmula astronómica simplificada.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    LUNA_NUEVA_REF = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    CICLO = 29.53058867

    dias_desde_ref = (dt - LUNA_NUEVA_REF).total_seconds() / 86400
    fase_norm = (dias_desde_ref % CICLO) / CICLO

    if fase_norm < 0.063 or fase_norm >= 0.937:
        nombre = "Luna nueva"
    elif fase_norm < 0.188:
        nombre = "Luna creciente"
    elif fase_norm < 0.312:
        nombre = "Cuarto creciente"
    elif fase_norm < 0.437:
        nombre = "Luna creciente"
    elif fase_norm < 0.563:
        nombre = "Luna llena"
    elif fase_norm < 0.688:
        nombre = "Luna menguante"
    elif fase_norm < 0.812:
        nombre = "Cuarto menguante"
    else:
        nombre = "Luna menguante"

    puntuacion = round(10 + 10 * math.cos(2 * math.pi * 2 * fase_norm))

    return {
        "fase_norm":   round(fase_norm, 3),
        "nombre":      nombre,
        "puntuacion":  puntuacion,
    }


# MAREAS  

def calcular_mareas(lat: float, lon: float, dt: datetime = None) -> dict:
    """
    Estima el estado de la marea y puntúa el momento para pescar.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    J2000 = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    t_dias = (dt - J2000).total_seconds() / 86400

    T_M2 = 12.4206 / 24
    T_S2 = 12.0000 / 24

    fase_geo = (lon * 0.13 + lat * 0.07) % 1.0

    angulo_M2 = 2 * math.pi * (t_dias / T_M2 + fase_geo)
    angulo_S2 = 2 * math.pi * (t_dias / T_S2 + fase_geo * 0.8)

    nivel_raw = math.cos(angulo_M2) + 0.35 * math.cos(angulo_S2)

    max_posible = 1.35
    nivel_norm = round((nivel_raw + max_posible) / (2 * max_posible), 3)

    dt_future = datetime.fromtimestamp(dt.timestamp() + 900, tz=timezone.utc)
    t_fut = (dt_future - J2000).total_seconds() / 86400
    nivel_fut = math.cos(2 * math.pi * (t_fut / T_M2 + fase_geo)) + \
                0.35 * math.cos(2 * math.pi * (t_fut / T_S2 + fase_geo * 0.8))
    nivel_fut_norm = (nivel_fut + max_posible) / (2 * max_posible)

    velocidad = nivel_fut_norm - nivel_norm

    if nivel_norm > 0.80:
        estado = "Pleamar"
    elif nivel_norm < 0.20:
        estado = "Bajamar"
    elif velocidad > 0:
        estado = "Marea subiendo"
    else:
        estado = "Marea bajando"

    cambio_intensidad = abs(velocidad) * 40
    if 0.25 < nivel_norm < 0.75:
        puntuacion = round(min(20, 10 + cambio_intensidad * 20))
    elif nivel_norm > 0.80 or nivel_norm < 0.20:
        puntuacion = round(max(5, 12 - abs(nivel_norm - 0.5) * 20))
    else:
        puntuacion = 13

    if estado == "Marea subiendo" and 0.3 < nivel_norm < 0.7:
        momento = "Momento ideal: marea subiendo activamente"
    elif estado == "Marea bajando" and 0.3 < nivel_norm < 0.7:
        momento = "Buen momento: marea bajando, peces activos"
    elif estado == "Pleamar":
        momento = "Pleamar: aguas quietas, actividad reducida"
    elif estado == "Bajamar":
        momento = "Bajamar: aguas bajas, esperar cambio de marea"
    else:
        momento = f"Marea {'subiendo' if velocidad > 0 else 'bajando'}"

    return {
        "nivel_norm":  nivel_norm,
        "estado":      estado,
        "momento":     momento,
        "puntuacion":  max(0, min(20, puntuacion)),
    }


# TEMPERATURA DEL AGUA

def puntuar_temperatura(temp_agua: float, especie) -> tuple[int, str | None]:
    if temp_agua is None:
        return 10, None

    t_min = especie.temp_agua_min
    t_max = especie.temp_agua_max
    rango = t_max - t_min

    if t_min <= temp_agua <= t_max:
        centro = (t_min + t_max) / 2
        distancia_centro = abs(temp_agua - centro) / (rango / 2)
        pts = round(20 - distancia_centro * 3)
    elif temp_agua < t_min:
        diff = t_min - temp_agua
        pts = max(0, round(20 - diff * 3))
    else:
        diff = temp_agua - t_max
        pts = max(0, round(20 - diff * 3))

    nota = None
    if pts < 14:
        if temp_agua < t_min:
            nota = f"Agua fría ({temp_agua:.1f}°C, óptimo {t_min}–{t_max}°C)"
        else:
            nota = f"Agua caliente ({temp_agua:.1f}°C, óptimo {t_min}–{t_max}°C)"

    return min(20, pts), nota


# VIENTO


def puntuar_viento(viento: float, especie) -> tuple[int, str | None]:
    if viento is None:
        return 8, None

    v_max = especie.viento_max

    if viento < 5:
        pts = 10
        nota = None
    elif viento <= v_max * 0.6:
        pts = 15
        nota = None
    elif viento <= v_max:
        fraccion = (viento - v_max * 0.6) / (v_max * 0.4)
        pts = round(15 - fraccion * 5)
        nota = None
    else:
        exceso = viento - v_max
        pts = max(0, round(10 - exceso * 1.5))
        nota = f"Viento fuerte ({viento:.0f} km/h, máx {v_max:.0f})"

    return pts, nota


# ESTADO DEL MAR


def puntuar_olas(altura_olas: float, periodo: float = None) -> tuple[int, str | None]:
    if altura_olas is None:
        return 8, None

    if altura_olas < 0.1:
        pts, nota = 10, None
    elif altura_olas <= 0.5:
        pts, nota = 15, None
    elif altura_olas <= 1.0:
        pts, nota = 13, None
    elif altura_olas <= 1.5:
        pts, nota = 10, None
    elif altura_olas <= 2.0:
        pts, nota = 6, f"Mar agitado ({altura_olas:.1f} m)"
    elif altura_olas <= 2.5:
        pts, nota = 3, f"Mar muy agitado ({altura_olas:.1f} m)"
    else:
        pts, nota = 0, f"Mar peligroso ({altura_olas:.1f} m)"

    return pts, nota



# CLARIDAD DEL AGUA


def puntuar_claridad(precipitacion: float, altura_olas: float) -> tuple[int, str | None]:
    precipitacion = precipitacion or 0
    altura_olas = altura_olas or 0

    pts = 10

    if precipitacion > 5:
        pts -= 6
    elif precipitacion > 2:
        pts -= 4
    elif precipitacion > 0.5:
        pts -= 2

    if altura_olas > 2.0:
        pts -= 4
    elif altura_olas > 1.0:
        pts -= 2
    elif altura_olas > 0.5:
        pts -= 1

    pts = max(0, pts)

    nota = None
    if pts <= 4:
        nota = "Agua probablemente turbia"
    elif pts <= 7:
        nota = "Claridad del agua moderada"

    return pts, nota


# PUNTUACIÓN TOTAL

def calcular_puntuacion(condiciones: dict, especie, lat: float = 43.0, lon: float = -8.5, dt: datetime = None) -> dict:
    if not condiciones:
        return {
            "puntuacion": 0,
            "resumen": "No se pudieron obtener datos meteorológicos.",
            "desglose": {},
            "luna": {},
            "mareas": {},
        }

    ahora = dt if dt is not None else datetime.now(timezone.utc)

    luna   = calcular_fase_lunar(ahora)
    mareas = calcular_mareas(lat, lon, ahora)

    temp_pts,     temp_nota     = puntuar_temperatura(condiciones.get("temperatura_agua"), especie)
    viento_pts,   viento_nota   = puntuar_viento(condiciones.get("velocidad_viento"), especie)
    olas_pts,     olas_nota     = puntuar_olas(condiciones.get("altura_olas"), condiciones.get("periodo_olas"))
    claridad_pts, claridad_nota = puntuar_claridad(condiciones.get("precipitacion", 0), condiciones.get("altura_olas", 0))

    luna_pts   = luna["puntuacion"]
    mareas_pts = mareas["puntuacion"]

    total = temp_pts + viento_pts + olas_pts + claridad_pts + luna_pts + mareas_pts
    total = max(0, min(100, total))

    if total >= 80:
        texto = "Condiciones excelentes para pescar"
    elif total >= 65:
        texto = "Buenas condiciones"
    elif total >= 50:
        texto = "Condiciones aceptables"
    elif total >= 35:
        texto = "Condiciones mediocres"
    else:
        texto = "Condiciones desfavorables"

    problemas = [n for n in [temp_nota, viento_nota, olas_nota, claridad_nota] if n]
    resumen = texto
    if problemas:
        resumen += ": " + problemas[0]

    desglose = {
        "temperatura_agua": {"puntos": temp_pts, "max": 20, "nota": temp_nota or f"{condiciones.get('temperatura_agua', '—'):.1f}°C" if condiciones.get('temperatura_agua') else "Sin datos"},
        "viento": {"puntos": viento_pts, "max": 15, "nota": viento_nota or f"{condiciones.get('velocidad_viento', 0):.0f} km/h"},
        "estado_mar": {"puntos": olas_pts, "max": 15, "nota": olas_nota or f"Olas {condiciones.get('altura_olas', 0):.1f} m"},
        "claridad_agua": {"puntos": claridad_pts, "max": 10, "nota": claridad_nota or "Agua clara"},
        "luna": {"puntos": luna_pts, "max": 20, "nota": luna['nombre']},
        "mareas": {"puntos": mareas_pts, "max": 20, "nota": mareas["momento"]},
    }

    return {
        "puntuacion": total,
        "resumen":    resumen,
        "desglose":   desglose,
        "luna":       luna,
        "mareas":     mareas,
    }


def calcular_puntuacion_rango(datos_viento_mar: dict, especie, lat: float, lon: float) -> list:
    """
    Recibe los arrays de Open-Meteo y genera el timeline completo llamando
    a calcular_puntuacion() para cada una de las horas.
    """
    if not datos_viento_mar or "timestamps" not in datos_viento_mar:
        return []

    resultados_timeline = []
    total_horas = len(datos_viento_mar["timestamps"])

    for i in range(total_horas):
        timestamp_str = datos_viento_mar["timestamps"][i]
        dt_hora = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)

        condiciones_hora = {
            "temperatura_agua": datos_viento_mar["temperatura_agua"][i] if i < len(datos_viento_mar["temperatura_agua"]) else None,
            "altura_olas":      datos_viento_mar["altura_olas"][i] if i < len(datos_viento_mar["altura_olas"]) else None,
            "periodo_olas":     datos_viento_mar["periodo_olas"][i] if i < len(datos_viento_mar["periodo_olas"]) else None,
            "velocidad_viento": datos_viento_mar["velocidad_viento"][i] if i < len(datos_viento_mar["velocidad_viento"]) else None,
            "temperatura_aire": datos_viento_mar["temperatura_aire"][i] if i < len(datos_viento_mar["temperatura_aire"]) else None,
            "precipitacion":    datos_viento_mar["precipitacion"][i] if i < len(datos_viento_mar["precipitacion"]) else 0,
            "codigo_tiempo":    datos_viento_mar["codigo_tiempo"][i] if i < len(datos_viento_mar["codigo_tiempo"]) else 0,
        }

        analisis_hora = calcular_puntuacion(condiciones_hora, especie, lat, lon, dt=dt_hora)

        # para que React pueda leer las variables físicas de forma directa.
        resultados_timeline.append({
            "fecha_hora":     timestamp_str,
            "puntuacion":     analisis_hora["puntuacion"],
            "resumen":        analisis_hora["resumen"],
            "desglose":       analisis_hora["desglose"],
            "luna":           analisis_hora["luna"],
            "mareas":         analisis_hora["mareas"],
            "estado_tiempo":  describir_tiempo(condiciones_hora["codigo_tiempo"]),
            "condiciones":    condiciones_hora  # <-- ¡Sincronizado con React!
        })

    return resultados_timeline



# UTILIDADES


WMO_CODES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 51: "Llovizna ligera", 61: "Lluvia ligera",
    71: "Nieve ligera", 80: "Chubascos", 95: "Tormenta",
}

def describir_tiempo(codigo: int) -> str:
    return WMO_CODES.get(codigo, f"Código {codigo}")