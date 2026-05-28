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

# Zonas principales de la costa gallega
zonas = [
    ("A Guarda",   41.90, -8.87), ("Baiona",     42.12, -8.84),
    ("Vigo",       42.23, -8.72), ("Cangas",     42.26, -8.78),
    ("Bueu",       42.32, -8.78), ("Marin",      42.39, -8.70),
    ("Pontevedra", 42.43, -8.64), ("Sanxenxo",   42.40, -8.81),
    ("O Grove",    42.48, -8.86), ("Ribeira",    42.55, -8.99),
    ("Muros",      42.77, -9.05), ("Fisterra",   42.90, -9.26),
    ("Camarinas",  43.13, -9.18), ("Laxe",       43.21, -9.00),
    ("Malpica",    43.32, -8.81), ("A Coruna",   43.36, -8.41),
    ("Ferrol",     43.48, -8.23), ("Cedeira",    43.66, -8.05),
    ("Viveiro",    43.66, -7.59), ("Burela",     43.65, -7.35),
    ("Ribadeo",    43.53, -7.03),
]

data = []

# Especies
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

# Spots (10 por zona)
pk_spot = 1
for z_nome, z_lat, z_lng in zonas:
    for i in range(10):
        data.append({
            "model": "api.spot",
            "pk": pk_spot,
            "fields": {
                "nombre":      f"{z_nome} - Punto {i+1}",
                "tipo":        "mar",
                "latitud":     round(z_lat + (i * 0.005), 4),
                "longitud":    round(z_lng + (i * 0.005), 4),
                "descripcion": f"Zona de pesca en {z_nome}",
            }
        })
        pk_spot += 1

with open('api/fixtures/initial_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generados {len(especies)} especies y {pk_spot-1} spots en Galicia.")