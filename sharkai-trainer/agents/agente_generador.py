"""
AGENTE 4 - GENERADOR DE MODELFILE
Toma el conocimiento acumulado y genera un Modelfile mejorado
para crear una nueva versión especializada del modelo.

INTEGRACIÓN CON O PEIRAO:
  El modelo base es el que usa O Peirao: llama3.
  El modelo mejorado se llamará sharkai-galicia:vN y puede configurarse
  en el backend Django cambiando MODELO en api/views.py o services.py.
"""

import json
import os
import subprocess
from datetime import datetime

MODELO_BASE = "llama3.2:3b" # <- Modelo base que usa O Peirao


def cargar_todo_el_conocimiento(carpeta: str = "data/knowledge") -> list[dict]:
    conocimientos = []
    if not os.path.exists(carpeta):
        return conocimientos
    for f in os.listdir(carpeta):
        if f.startswith("conocimiento_") and f.endswith(".json"):
            with open(os.path.join(carpeta, f), "r", encoding="utf-8") as fh:
                conocimientos.append(json.load(fh))
    return conocimientos


def cargar_ultimo_informe(carpeta: str = "logs") -> dict | None:
    if not os.path.exists(carpeta):
        return None
    informes = sorted([f for f in os.listdir(carpeta) if f.startswith("evaluacion_")])
    if not informes:
        return None
    with open(os.path.join(carpeta, informes[-1]), "r", encoding="utf-8") as f:
        return json.load(f)


def construir_system_prompt(conocimientos: list[dict], informe: dict | None) -> str:
    prompt = """Eres SharkAI, el asistente experto en pesca deportiva y biología marina de Galicia integrado en O Peirao.
Tu especialidad son las especies del Atlántico norte ibérico y las rías gallegas: Ría de Arousa, Ría de Vigo,
Ría de Pontevedra, Costa da Morte y Rías Altas.

Tienes acceso a datos meteorológicos en tiempo real (Open-Meteo) y conoces las condiciones típicas
del mar gallego: temperatura del agua, mareas, corrientes y estaciones del año.

Hablas con retranca gallega, de forma práctica y concisa. Cuando no estás seguro de algo,
lo dices claramente y recomiendas consultar la Consellería do Mar de Galicia.

CONOCIMIENTO ESPECIALIZADO SOBRE ESPECIES DE GALICIA:
"""
    for k in conocimientos:
        especie = k.get("especie", "desconocida").upper()
        prompt += f"\n## {especie}\n"
        prompt += f"- Hábitat: {k.get('habitat', 'N/A')}\n"
        prompt += f"- En Galicia: {k.get('distribucion_galicia', 'N/A')}\n"
        prompt += f"- Mejor temporada: {k.get('temporada_pesca', 'N/A')}\n"
        prompt += f"- Técnicas: {', '.join(k.get('tecnicas_recomendadas', []))}\n"
        prompt += f"- Cebos: {', '.join(k.get('cebos_efectivos', []))}\n"
        prompt += f"- Talla mínima legal: {k.get('talla_minima_legal', 'N/A')}\n"
        prompt += f"- Consejo Galicia: {k.get('consejos_galicia', 'N/A')}\n"

    if informe and informe.get("por_mejorar"):
        prompt += "\n## ÁREAS A REFORZAR (detectadas en autoevaluación):\n"
        for mejora in informe["por_mejorar"][:5]:
            if mejora:
                prompt += f"- {mejora}\n"

    prompt += """
REGLAS:
1. Si no sabes algo con certeza, dilo. Nunca inventes datos de tallas, cupos o normativas.
2. Para normativas, remite a la Consellería do Mar: https://www.xunta.gal/mar
3. Sé conciso y práctico. Respuestas cortas salvo que pidan detalle.
4. Cuando sea relevante, menciona condiciones de marea o meteorología.
5. Rechaza educadamente preguntas que no sean sobre pesca, naturaleza marina o el tiempo.
"""
    return prompt


def generar_modelfile(version: int, system_prompt: str, carpeta_reports: str = "reports") -> str:
    os.makedirs(carpeta_reports, exist_ok=True)
    contenido = f"""# SharkAI v{version} para O Peirao — Especialista en Pesca Gallega
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Para usarlo en O Peirao: cambia MODELO = "sharkai-galicia:v{version}" en api/views.py

FROM {MODELO_BASE}

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

SYSTEM \"\"\"{system_prompt}\"\"\"
"""
    ruta = os.path.join(carpeta_reports, f"Modelfile_v{version}")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def ejecutar(carpeta_knowledge: str = "data/knowledge",
             carpeta_logs: str = "logs",
             carpeta_reports: str = "reports",
             crear_modelo: bool = True) -> dict:

    print("\n" + "="*60)
    print("  🔧 AGENTE GENERADOR - SharkAI Trainer")
    print("="*60)

    conocimientos = cargar_todo_el_conocimiento(carpeta_knowledge)
    informe = cargar_ultimo_informe(carpeta_logs)

    print(f"  📚 Especies en base de conocimiento: {len(conocimientos)}")
    if informe:
        print(f"  📊 Última evaluación: {informe.get('puntuacion_media', 'N/A')}/10")

    if not conocimientos:
        print("  ❌ Sin conocimiento acumulado. Ejecuta primero Buscador y Procesador.")
        return {}

    versiones = [f for f in os.listdir(carpeta_reports) if f.startswith("Modelfile_v")] if os.path.exists(carpeta_reports) else []
    version = len(versiones) + 1

    print(f"\n  🏗️  Construyendo Modelfile v{version}...")
    system_prompt = construir_system_prompt(conocimientos, informe)
    ruta_modelfile = generar_modelfile(version, system_prompt, carpeta_reports)

    print(f"  ✅ Modelfile generado: {ruta_modelfile}")

    nombre_modelo = "sharkai:latest"
    resultado = {
        "version": version,
        "modelfile": ruta_modelfile,
        "nombre_modelo": nombre_modelo,
        "especies_incluidas": [k.get("especie") for k in conocimientos],
        "creado_en_ollama": False
    }

    if crear_modelo:
        print(f"\n  🚀 Creando modelo '{nombre_modelo}' en Ollama...")
        try:
            proc = subprocess.run(
                ["ollama", "create", nombre_modelo, "-f", os.path.abspath(ruta_modelfile)],
                capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore'
            )
            if proc.returncode == 0:
                print(f"  ✅ Modelo '{nombre_modelo}' creado.")
                print(f"  💡 Para usarlo en O Peirao: cambia MODELO='llama3' por MODELO='{nombre_modelo}' en api/views.py")
                resultado["creado_en_ollama"] = True
            else:
                print(f"  ⚠️  Error: {proc.stderr}")
                print(f"  💡 Crea manualmente: ollama create {nombre_modelo} -f {os.path.abspath(ruta_modelfile)}")
        except FileNotFoundError:
            print(f"  ⚠️  Ollama no encontrado en PATH.")
    return resultado


if __name__ == "__main__":
    ejecutar()
