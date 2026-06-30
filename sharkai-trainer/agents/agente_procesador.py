"""
AGENTE 2 - PROCESADOR DE CONOCIMIENTO
Lee los documentos descargados y los convierte en bloques de
conocimiento estructurado sobre pesca, listos para entrenar a SharkAI.
"""

import json
import os
import requests
from datetime import datetime


OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "sharkai:latest"


PROMPT_EXTRACCION = """Eres un experto en biología marina y pesca deportiva en Galicia, España.

Analiza el siguiente texto científico sobre una especie marina y extrae información PRÁCTICA para pescadores.
Responde SOLO con un objeto JSON válido con exactamente esta estructura, sin texto adicional:

{{
  "especie": "{especie}",
  "nombre_comun": "nombre más usado por pescadores gallegos",
  "nombre_cientifico": "nombre científico",
  "descripcion_breve": "descripción en 2 frases para un pescador",
  "habitat": "dónde vive y a qué profundidad",
  "distribucion_galicia": "zonas de Galicia donde se encuentra",
  "temporada_pesca": "mejores meses para pescarla en Galicia",
  "tecnicas_recomendadas": ["técnica1", "técnica2", "técnica3"],
  "cebos_efectivos": ["cebo1", "cebo2", "cebo3"],
  "talla_minima_legal": "talla mínima legal en España (en cm) o 'Consultar normativa'",
  "record_talla": "talla máxima conocida",
  "curiosidades_pescador": "dato curioso útil para el pescador",
  "consejos_galicia": "consejo específico para pescarla en las rías gallegas"
}}

TEXTO A ANALIZAR:
{texto}

Responde SOLO con el JSON, sin explicaciones, sin ```json, sin texto antes o después."""


def llamar_ollama(prompt: str) -> str | None:
    """Llama a Ollama con el modelo SharkAI."""
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Baja temperatura = respuestas más precisas
                "num_predict": 800
            }
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"  [ERROR] Ollama no responde: {e}")
        print(f"  Asegúrate de que Ollama está ejecutándose con: ollama serve")
        return None


def limpiar_json(texto: str) -> str:
    """Intenta extraer JSON válido de la respuesta del modelo."""
    # Buscar el primer { y el último }
    inicio = texto.find("{")
    fin = texto.rfind("}") + 1
    if inicio >= 0 and fin > inicio:
        return texto[inicio:fin]
    return texto


def procesar_documento(ruta_doc: str, carpeta_salida: str) -> dict | None:
    """Procesa un documento y extrae conocimiento estructurado."""
    with open(ruta_doc, "r", encoding="utf-8") as f:
        doc = json.load(f)

    especie = doc["especie"]
    texto = doc["contenido"]

    # Usar solo los primeros 3000 caracteres para no saturar el modelo
    texto_recortado = texto[:3000]

    prompt = PROMPT_EXTRACCION.format(
        especie=especie,
        texto=texto_recortado
    )

    print(f"  🧠 Procesando: {especie} ({doc['fuente']})")
    respuesta = llamar_ollama(prompt)

    if not respuesta:
        return None

    # Intentar parsear el JSON
    json_limpio = limpiar_json(respuesta)
    try:
        conocimiento = json.loads(json_limpio)

        # Añadir metadatos
        conocimiento["_fuente"] = doc["fuente"]
        conocimiento["_url"] = doc["url"]
        conocimiento["_fecha_procesado"] = datetime.now().isoformat()
        conocimiento["_doc_id"] = doc["id"]

        # Guardar
        nombre_salida = f"conocimiento_{especie}.json"
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(conocimiento, f, ensure_ascii=False, indent=2)

        print(f"     ✅ Conocimiento extraído → {nombre_salida}")
        return conocimiento

    except json.JSONDecodeError:
        print(f"     ⚠️  El modelo no devolvió JSON válido, guardando respuesta raw...")
        # Guardar la respuesta raw para debugging
        ruta_raw = os.path.join(carpeta_salida, f"raw_{especie}.txt")
        with open(ruta_raw, "w", encoding="utf-8") as f:
            f.write(respuesta)
        return None


def ejecutar(carpeta_docs: str = "data/docs", carpeta_knowledge: str = "data/knowledge") -> list:
    """Ejecuta el agente procesador sobre todos los documentos disponibles."""
    os.makedirs(carpeta_knowledge, exist_ok=True)

    print("\n" + "="*60)
    print("  🧠 AGENTE PROCESADOR - SharkAI Trainer")
    print("="*60)

    # Buscar todos los documentos descargados
    docs = [f for f in os.listdir(carpeta_docs) if f.endswith(".json")]
    print(f"  Encontrados {len(docs)} documentos para procesar...\n")

    if not docs:
        print("  ❌ No hay documentos. Ejecuta primero el Agente Buscador.")
        return []

    conocimientos = []
    for nombre_doc in docs:
        ruta = os.path.join(carpeta_docs, nombre_doc)
        resultado = procesar_documento(ruta, carpeta_knowledge)
        if resultado:
            conocimientos.append(resultado)

    print(f"\n  📊 Resultado: {len(conocimientos)}/{len(docs)} especies procesadas correctamente.")
    return conocimientos


if __name__ == "__main__":
    ejecutar()
