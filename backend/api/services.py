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

# ---------------------------------------------------------------------------
# URLs de Open-Meteo (sin API key)
# ---------------------------------------------------------------------------
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


# ---------------------------------------------------------------------------
# 1. OBTENCIÓN DE DATOS METEOROLÓGICOS Y MARINOS
# ---------------------------------------------------------------------------

def get_weather(lat: float, lon: float) -> dict | None:
    """
    Obtiene condiciones actuales combinando datos atmosféricos + marinos.
    Añade precipitación reciente (para estimar claridad del agua).
    Devuelve None si falla alguna petición.
    """
    params_weather = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "wind_speed_10m", "weather_code", "precipitation"],
        "timezone": "Europe/Madrid",
        "forecast_days": 1,
    }
    params_marine = {
        "latitude": lat,
        "longitude": lon,
        "current": ["sea_surface_temperature", "wave_height", "wave_period"],
        "timezone": "Europe/Madrid",
    }

    try:
        r_w = requests.get(OPEN_METEO_URL, params=params_weather, timeout=5)
        r_w.raise_for_status()
        wd = r_w.json()["current"]

        r_m = requests.get(MARINE_URL, params=params_marine, timeout=5)
        r_m.raise_for_status()
        md = r_m.json()["current"]

        return {
            "temperatura_agua":  md.get("sea_surface_temperature"),
            "altura_olas":       md.get("wave_height"),
            "periodo_olas":      md.get("wave_period"),
            "velocidad_viento":  wd.get("wind_speed_10m"),
            "temperatura_aire":  wd.get("temperature_2m"),
            "precipitacion":     wd.get("precipitation", 0),
            "codigo_tiempo":     wd.get("weather_code"),
        }

    except requests.RequestException:
        return None


# ---------------------------------------------------------------------------
# 2. FASE LUNAR  (fórmula astronómica, sin API)
# ---------------------------------------------------------------------------

def calcular_fase_lunar(dt: datetime = None) -> dict:
    """
    Calcula la fase lunar actual mediante fórmula astronómica simplificada.

    Retorna:
        fase_norm   — valor 0.0–1.0  (0 = luna nueva, 0.5 = llena)
        nombre      — nombre de la fase en español
        puntuacion  — 0–20 pts (máximo en luna nueva y llena)
        emoji       — representación visual
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Referencia: luna nueva conocida el 6 enero 2000 18:14 UTC
    # Ciclo lunar sinódico = 29.53058867 días
    LUNA_NUEVA_REF = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    CICLO = 29.53058867

    dias_desde_ref = (dt - LUNA_NUEVA_REF).total_seconds() / 86400
    fase_norm = (dias_desde_ref % CICLO) / CICLO  # 0.0 a 1.0

    # Nombre e icono de la fase
    if fase_norm < 0.063 or fase_norm >= 0.937:
        nombre, emoji = "Luna nueva", "🌑"
    elif fase_norm < 0.188:
        nombre, emoji = "Cuarto creciente", "🌒"
    elif fase_norm < 0.312:
        nombre, emoji = "Cuarto creciente", "🌓"
    elif fase_norm < 0.437:
        nombre, emoji = "Gibosa creciente", "🌔"
    elif fase_norm < 0.563:
        nombre, emoji = "Luna llena", "🌕"
    elif fase_norm < 0.688:
        nombre, emoji = "Gibosa menguante", "🌖"
    elif fase_norm < 0.812:
        nombre, emoji = "Cuarto menguante", "🌗"
    else:
        nombre, emoji = "Cuarto menguante", "🌘"

    # Puntuación: coseno doble → máximo en luna nueva (0) y llena (0.5)
    # cos(2π * 2 * fase) da 1.0 en 0 y 0.5, y -1.0 en 0.25 y 0.75
    puntuacion = round(10 + 10 * math.cos(2 * math.pi * 2 * fase_norm))  # 0–20

    return {
        "fase_norm":   round(fase_norm, 3),
        "nombre":      nombre,
        "emoji":       emoji,
        "puntuacion":  puntuacion,
    }


# ---------------------------------------------------------------------------
# 3. MAREAS  (modelo armónico simplificado, sin API)
# ---------------------------------------------------------------------------

def calcular_mareas(lat: float, lon: float, dt: datetime = None) -> dict:
    """
    Estima el estado de la marea y puntúa el momento para pescar.

    Modelo: combinación de las dos componentes principales del ciclo lunar
    (M2 semidiurno + S2 solar), ajustadas por latitud y longitud para
    introducir variabilidad geográfica realista en la costa gallega.

    Los cambios de marea (pleamar → bajamar y viceversa) son los momentos
    de mayor actividad de los peces, por eso reciben la máxima puntuación.

    Retorna:
        nivel_norm  — nivel relativo 0.0 (bajamar) a 1.0 (pleamar)
        estado      — "Pleamar", "Bajamar", "Marea bajando", "Marea subiendo"
        momento     — descripción del momento para pescar
        puntuacion  — 0–20 pts
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Segundos desde época J2000 (1 enero 2000 12:00 UTC)
    J2000 = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    t_dias = (dt - J2000).total_seconds() / 86400

    # Componente M2: período 12.4206 h (principal lunar semidiurna)
    # Componente S2: período 12.0000 h (principal solar semidiurna)
    # La diferencia entre ambas genera el ciclo de mareas vivas/muertas (~15 días)
    T_M2 = 12.4206 / 24  # en días
    T_S2 = 12.0000 / 24

    # Desfase geográfico: cada punto de la costa tiene su propia fase
    # Usamos lon y lat para crear un desfase único por ubicación
    fase_geo = (lon * 0.13 + lat * 0.07) % 1.0  # 0–1

    angulo_M2 = 2 * math.pi * (t_dias / T_M2 + fase_geo)
    angulo_S2 = 2 * math.pi * (t_dias / T_S2 + fase_geo * 0.8)

    # Amplitud M2 domina (1.0), S2 secundaria (0.35)
    nivel_raw = math.cos(angulo_M2) + 0.35 * math.cos(angulo_S2)

    # Normalizar a 0–1
    max_posible = 1.35
    nivel_norm = round((nivel_raw + max_posible) / (2 * max_posible), 3)

    # Calcular velocidad (derivada numérica, 15 min adelante)
    dt_future = datetime.fromtimestamp(dt.timestamp() + 900, tz=timezone.utc)
    t_fut = (dt_future - J2000).total_seconds() / 86400
    nivel_fut = math.cos(2 * math.pi * (t_fut / T_M2 + fase_geo)) + \
                0.35 * math.cos(2 * math.pi * (t_fut / T_S2 + fase_geo * 0.8))
    nivel_fut_norm = (nivel_fut + max_posible) / (2 * max_posible)

    velocidad = nivel_fut_norm - nivel_norm  # positivo = subiendo

    # Clasificar estado
    if nivel_norm > 0.80:
        estado = "Pleamar"
    elif nivel_norm < 0.20:
        estado = "Bajamar"
    elif velocidad > 0:
        estado = "Marea subiendo"
    else:
        estado = "Marea bajando"

    # Puntuación: el cambio de marea es el momento de oro (peces más activos)
    # La zona de "cambio" es cuando la velocidad es alta (0.25–0.75 del nivel)
    cambio_intensidad = abs(velocidad) * 40  # normalizado
    if 0.25 < nivel_norm < 0.75:
        # En zona de cambio activo
        puntuacion = round(min(20, 10 + cambio_intensidad * 20))
    elif nivel_norm > 0.80 or nivel_norm < 0.20:
        # En pleamar o bajamar (aguas quietas, peor momento)
        puntuacion = round(max(5, 12 - abs(nivel_norm - 0.5) * 20))
    else:
        puntuacion = 13

    # Descripción del momento para el pescador
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


# ---------------------------------------------------------------------------
# 4. TEMPERATURA DEL AGUA  (0–20 pts)
# ---------------------------------------------------------------------------

def puntuar_temperatura(temp_agua: float, especie) -> tuple[int, str | None]:
    """
    Máximo 20 pts. Penaliza fuera del rango óptimo de la especie.
    Gradual: -2 pts por cada grado fuera del rango (no colapsa de golpe).
    """
    if temp_agua is None:
        return 10, None  # sin datos: neutro

    t_min = especie.temp_agua_min
    t_max = especie.temp_agua_max
    rango = t_max - t_min

    if t_min <= temp_agua <= t_max:
        # Dentro del rango: máximo, con pequeño bonus si está en el centro
        centro = (t_min + t_max) / 2
        distancia_centro = abs(temp_agua - centro) / (rango / 2)
        pts = round(20 - distancia_centro * 3)  # 17–20
    elif temp_agua < t_min:
        diff = t_min - temp_agua
        pts = max(0, round(20 - diff * 3))
    else:  # temp > t_max
        diff = temp_agua - t_max
        pts = max(0, round(20 - diff * 3))

    nota = None
    if pts < 14:
        if temp_agua < t_min:
            nota = f"Agua fría ({temp_agua:.1f}°C, óptimo {t_min}–{t_max}°C)"
        else:
            nota = f"Agua caliente ({temp_agua:.1f}°C, óptimo {t_min}–{t_max}°C)"

    return min(20, pts), nota


# ---------------------------------------------------------------------------
# 5. VIENTO  (0–15 pts)
# ---------------------------------------------------------------------------

def puntuar_viento(viento: float, especie) -> tuple[int, str | None]:
    """
    Máximo 15 pts. Algo de viento es neutral; viento excesivo penaliza.
    Viento < 5 km/h (calma total): también penaliza ligeramente en mar
    porque suele indicar aguas demasiado quietas.
    """
    if viento is None:
        return 8, None

    v_max = especie.viento_max

    if viento < 5:
        pts = 10  # calma: aceptable pero no ideal
        nota = None
    elif viento <= v_max * 0.6:
        pts = 15  # viento suave: perfecto
        nota = None
    elif viento <= v_max:
        # Viento aceptable pero acercándose al límite
        fraccion = (viento - v_max * 0.6) / (v_max * 0.4)
        pts = round(15 - fraccion * 5)  # 10–15
        nota = None
    else:
        # Viento excesivo
        exceso = viento - v_max
        pts = max(0, round(10 - exceso * 1.5))
        nota = f"Viento fuerte ({viento:.0f} km/h, máx recomendado {v_max:.0f})"

    return pts, nota


# ---------------------------------------------------------------------------
# 6. ESTADO DEL MAR  (0–15 pts)
# ---------------------------------------------------------------------------

def puntuar_olas(altura_olas: float, periodo: float = None) -> tuple[int, str | None]:
    """
    Máximo 15 pts. Olas de 0.3–1.0 m son ideales para la mayoría de técnicas.
    Mar en calma total (<0.1 m) o muy agitado (>2.5 m) penaliza.
    """
    if altura_olas is None:
        return 8, None

    if altura_olas < 0.1:
        pts, nota = 10, None           # mar en calma: pescable pero poco movimiento
    elif altura_olas <= 0.5:
        pts, nota = 15, None           # ideal: mar suave
    elif altura_olas <= 1.0:
        pts, nota = 13, None           # mar rizado: bueno
    elif altura_olas <= 1.5:
        pts, nota = 10, None           # mar moderado: aceptable
    elif altura_olas <= 2.0:
        pts, nota = 6, f"Mar agitado ({altura_olas:.1f} m)"
    elif altura_olas <= 2.5:
        pts, nota = 3, f"Mar muy agitado ({altura_olas:.1f} m)"
    else:
        pts, nota = 0, f"Mar peligroso ({altura_olas:.1f} m), no recomendado"

    return pts, nota


# ---------------------------------------------------------------------------
# 7. CLARIDAD DEL AGUA  (0–10 pts, estimada)
# ---------------------------------------------------------------------------

def puntuar_claridad(precipitacion: float, altura_olas: float) -> tuple[int, str | None]:
    """
    Máximo 10 pts. Estimación indirecta:
    - Lluvia reciente → agua turbia (sedimentos en suspensión)
    - Olas altas → agua removida, más turbia
    No hay API de turbidez gratuita; esto es una aproximación razonable.
    """
    precipitacion = precipitacion or 0
    altura_olas = altura_olas or 0

    pts = 10

    # Penalizar por lluvia
    if precipitacion > 5:
        pts -= 6
    elif precipitacion > 2:
        pts -= 4
    elif precipitacion > 0.5:
        pts -= 2

    # Penalizar por olas que remueven el fondo
    if altura_olas > 2.0:
        pts -= 4
    elif altura_olas > 1.0:
        pts -= 2
    elif altura_olas > 0.5:
        pts -= 1

    pts = max(0, pts)

    nota = None
    if pts <= 4:
        nota = "Agua probablemente turbia (lluvia o mar agitado)"
    elif pts <= 7:
        nota = "Claridad del agua moderada"

    return pts, nota


# ---------------------------------------------------------------------------
# 8. PUNTUACIÓN TOTAL
# ---------------------------------------------------------------------------

def calcular_puntuacion(condiciones: dict, especie, lat: float = 43.0, lon: float = -8.5) -> dict:
    """
    Combina los 6 factores y devuelve:
        puntuacion   — 0–100
        resumen      — texto corto para el usuario
        desglose     — dict con puntos y notas de cada factor
        luna         — datos de la fase lunar
        mareas       — datos del estado de las mareas
    """
    if not condiciones:
        return {
            "puntuacion": 0,
            "resumen": "No se pudieron obtener datos meteorológicos.",
            "desglose": {},
            "luna": {},
            "mareas": {},
        }

    ahora = datetime.now(timezone.utc)

    # -- Calcular factores independientes --
    luna   = calcular_fase_lunar(ahora)
    mareas = calcular_mareas(lat, lon, ahora)

    temp_pts,     temp_nota     = puntuar_temperatura(condiciones.get("temperatura_agua"), especie)
    viento_pts,   viento_nota   = puntuar_viento(condiciones.get("velocidad_viento"), especie)
    olas_pts,     olas_nota     = puntuar_olas(condiciones.get("altura_olas"), condiciones.get("periodo_olas"))
    claridad_pts, claridad_nota = puntuar_claridad(condiciones.get("precipitacion", 0), condiciones.get("altura_olas", 0))

    luna_pts   = luna["puntuacion"]    # 0–20
    mareas_pts = mareas["puntuacion"]  # 0–20

    total = temp_pts + viento_pts + olas_pts + claridad_pts + luna_pts + mareas_pts
    total = max(0, min(100, total))

    # -- Resumen principal --
    if total >= 80:
        icono = "🎣✅"
        texto = "Condiciones excelentes para pescar"
    elif total >= 65:
        icono = "✅"
        texto = "Buenas condiciones"
    elif total >= 50:
        icono = "⚠️"
        texto = "Condiciones aceptables"
    elif total >= 35:
        icono = "⚠️"
        texto = "Condiciones mediocres"
    else:
        icono = "❌"
        texto = "Condiciones desfavorables"

    # Añadir el problema más grave si lo hay
    problemas = [n for n in [temp_nota, viento_nota, olas_nota, claridad_nota] if n]
    resumen = f"{icono} {texto}"
    if problemas:
        resumen += ": " + problemas[0]

    # -- Desglose detallado --
    desglose = {
        "temperatura_agua": {
            "puntos": temp_pts, "max": 20,
            "nota": temp_nota or f"{condiciones.get('temperatura_agua', '—'):.1f}°C" if condiciones.get('temperatura_agua') else "Sin datos",
        },
        "viento": {
            "puntos": viento_pts, "max": 15,
            "nota": viento_nota or f"{condiciones.get('velocidad_viento', 0):.0f} km/h",
        },
        "estado_mar": {
            "puntos": olas_pts, "max": 15,
            "nota": olas_nota or f"Olas {condiciones.get('altura_olas', 0):.1f} m",
        },
        "claridad_agua": {
            "puntos": claridad_pts, "max": 10,
            "nota": claridad_nota or "Agua clara",
        },
        "luna": {
            "puntos": luna_pts, "max": 20,
            "nota": f"{luna['emoji']} {luna['nombre']}",
        },
        "mareas": {
            "puntos": mareas_pts, "max": 20,
            "nota": mareas["momento"],
        },
    }

    return {
        "puntuacion": total,
        "resumen":    resumen,
        "desglose":   desglose,
        "luna":       luna,
        "mareas":     mareas,
    }


# ---------------------------------------------------------------------------
# 9. UTILIDADES
# ---------------------------------------------------------------------------

WMO_CODES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 51: "Llovizna ligera", 61: "Lluvia ligera",
    71: "Nieve ligera", 80: "Chubascos", 95: "Tormenta",
}


def describir_tiempo(codigo: int) -> str:
    return WMO_CODES.get(codigo, f"Código {codigo}")