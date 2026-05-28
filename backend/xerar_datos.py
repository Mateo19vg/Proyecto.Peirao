import json

# Especies principales de Galicia (incluye Choco y Calamar)
especies = [
    {"pk": 1, "nombre": "Lubina",   "t_min": 12, "t_max": 19, "v_max": 25},
    {"pk": 2, "nombre": "Sargo",    "t_min": 13, "t_max": 21, "v_max": 35},
    {"pk": 3, "nombre": "Dorada",   "t_min": 16, "t_max": 24, "v_max": 15},
    {"pk": 4, "nombre": "Maragota", "t_min": 11, "t_max": 20, "v_max": 40},
    {"pk": 5, "nombre": "Choco",    "t_min": 10, "t_max": 18, "v_max": 30},
    {"pk": 6, "nombre": "Calamar",  "t_min": 12, "t_max": 20, "v_max": 25},
]

data = []

# Procesar únicamente las especies
for e in especies:
    data.append({
        "model": "api.especie",
        "pk": e["pk"],
        "fields": {
            "nombre":       e["nombre"],
            "temp_agua_min": e["t_min"],
            "temp_agua_max": e["t_max"],
            "viento_max":   e["v_max"],
            "descripcion":  "Galicia",
        }
    })

# Guardar en el archivo JSON listo para Django
with open('api/fixtures/initial_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Hecho: Generadas {len(especies)} especies en api/fixtures/initial_data.json.")