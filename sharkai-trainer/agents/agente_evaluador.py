"""
AGENTE 3 - EVALUADOR / CRÍTICO
Genera preguntas de pesca, las hace a SharkAI, evalúa las respuestas
y detecta qué áreas necesitan mejorar.

INTEGRACIÓN CON O PEIRAO:
  El modelo que se evalúa es el mismo que usa el backend Django:
  Ollama corriendo en http://127.0.0.1:11434 con el modelo llama3 (o sharkai).
  Cambia MODELO abajo si usas otro nombre de modelo.
"""

import json
import os
import requests
from datetime import datetime


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODELO = "sharkai:latest"   # <- Cámbialo a "sharkai:latest" si usas ese modelo

PREGUNTAS_EVALUACION = {
    "lubina": [
        "¿En qué época del año es mejor pescar lubina en las rías gallegas?",
        "¿Qué señuelos son más efectivos para la lubina de surf?",
        "¿Cuál es la talla mínima legal para la lubina en España?",
    ],
    "calamar": [
        "¿Cómo se pesca el calamar con técnica de jigging?",
        "¿A qué horas del día tiene más actividad el calamar?",
        "¿Qué tamaño de egi es mejor para el calamar gallego?",
    ],
    "dorada": [
        "¿Cuál es el mejor cebo natural para pescar dorada?",
        "¿En qué zonas de las rías gallegas abunda la dorada?",
        "¿Qué técnica de pesca es más efectiva para la dorada desde costa?",
    ],
    "rodaballo": [
        "¿A qué profundidad vive el rodaballo en las costas gallegas?",
        "¿Qué carnadas naturales prefiere el rodaballo?",
        "¿Cuál es la mejor época para pescar rodaballo en Galicia?",
    ],
    "general": [
        "¿Cómo afectan las mareas a la pesca en las rías gallegas?",
        "¿Qué diferencia hay entre pescar en marea viva y marea muerta?",
        "¿Cuáles son las 3 mejores especies para pescar desde costa en Galicia?",
    ]
}

PROMPT_EVALUACION = """Eres un juez experto en pesca en Galicia, España. Tienes este conocimiento de referencia sobre la especie:

CONOCIMIENTO DE REFERENCIA:
{conocimiento_referencia}

Evalúa la siguiente respuesta de un asistente de IA a la pregunta de pesca:

PREGUNTA: {pregunta}
RESPUESTA DEL ASISTENTE: {respuesta}

Responde SOLO con un JSON válido con esta estructura exacta:
{{
  "puntuacion": 0-10,
  "precision_tecnica": "alta/media/baja",
  "menciona_galicia": true/false,
  "errores_detectados": ["error1", "error2"],
  "aciertos_destacados": ["acierto1"],
  "sugerencia_mejora": "cómo mejorar esta respuesta en 1 frase"
}}"""


def llamar_ollama(prompt: str, max_tokens: int = 500) -> str | None:
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens}
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"  [ERROR] Ollama: {e}")
        print(f"  Asegúrate de que Ollama está corriendo (ollama serve) y de que el modelo '{MODELO}' está instalado.")
        return None


def cargar_conocimiento(especie: str, carpeta: str = "data/knowledge") -> str:
    ruta = os.path.join(carpeta, f"conocimiento_{especie}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    return "No hay conocimiento de referencia disponible para esta especie."


def evaluar_respuesta(pregunta: str, respuesta: str, especie: str) -> dict | None:
    conocimiento = cargar_conocimiento(especie)
    prompt = PROMPT_EVALUACION.format(
        conocimiento_referencia=conocimiento[:2000],
        pregunta=pregunta,
        respuesta=respuesta
    )
    eval_raw = llamar_ollama(prompt, max_tokens=400)
    if not eval_raw:
        return None
    inicio = eval_raw.find("{")
    fin = eval_raw.rfind("}") + 1
    if inicio >= 0 and fin > inicio:
        try:
            return json.loads(eval_raw[inicio:fin])
        except json.JSONDecodeError:
            pass
    return None


def ejecutar_evaluacion(carpeta_knowledge: str = "data/knowledge",
                        carpeta_logs: str = "logs") -> dict:
    os.makedirs(carpeta_logs, exist_ok=True)

    print("\n" + "="*60)
    print("  🎯 AGENTE EVALUADOR - SharkAI Trainer")
    print("="*60)

    especies_disponibles = []
    if os.path.exists(carpeta_knowledge):
        for f in os.listdir(carpeta_knowledge):
            if f.startswith("conocimiento_") and f.endswith(".json"):
                especie = f.replace("conocimiento_", "").replace(".json", "")
                especies_disponibles.append(especie)

    print(f"  Especies con conocimiento: {especies_disponibles or ['ninguna (modo básico)']}\n")

    resultados = []
    puntuaciones = []
    categorias = ["general"] + [e for e in especies_disponibles if e in PREGUNTAS_EVALUACION]

    for categoria in categorias:
        preguntas = PREGUNTAS_EVALUACION.get(categoria, [])
        for pregunta in preguntas:
            print(f"  ❓ {pregunta[:65]}...")
            respuesta_raw = llamar_ollama(pregunta, max_tokens=300)
            if not respuesta_raw:
                continue
            print(f"     💬 Respuesta obtenida ({len(respuesta_raw)} chars)")
            evaluacion = evaluar_respuesta(pregunta, respuesta_raw, categoria)
            if evaluacion:
                puntuacion = evaluacion.get("puntuacion", 0)
                puntuaciones.append(puntuacion)
                emoji = "✅" if puntuacion >= 7 else "⚠️" if puntuacion >= 4 else "❌"
                print(f"     {emoji} Puntuación: {puntuacion}/10")
                resultados.append({
                    "especie": categoria,
                    "pregunta": pregunta,
                    "respuesta": respuesta_raw,
                    "evaluacion": evaluacion
                })

    media = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
    nivel = "Experto 🏆" if media >= 8 else "Avanzado 📈" if media >= 6 else "Básico 📚" if media >= 4 else "Principiante 🌱"

    resumen = {
        "fecha": datetime.now().isoformat(),
        "modelo_evaluado": MODELO,
        "total_preguntas": len(resultados),
        "puntuacion_media": round(media, 2),
        "nivel_actual": nivel,
        "por_mejorar": [
            r["evaluacion"].get("sugerencia_mejora", "")
            for r in resultados
            if r.get("evaluacion", {}).get("puntuacion", 10) < 6
        ],
        "resultados": resultados
    }

    nombre_log = f"evaluacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(carpeta_logs, nombre_log), "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print(f"\n  📊 RESULTADO FINAL:")
    print(f"     Puntuación media: {media:.1f}/10")
    print(f"     Nivel actual: {nivel}")
    print(f"     Informe guardado: logs/{nombre_log}")

    return resumen


if __name__ == "__main__":
    ejecutar_evaluacion()
