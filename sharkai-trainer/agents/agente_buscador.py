"""
AGENTE 1 - BUSCADOR
Busca y descarga documentación sobre especies de pesca en Galicia
desde fuentes abiertas en internet.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib
from datetime import datetime

# Cabeceras para simular un navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Fuentes de información sobre pesca en Galicia/España
FUENTES = [
    {
        "nombre": "Wikipedia - Lubina europea",
        "url": "https://es.wikipedia.org/wiki/Dicentrarchus_labrax",
        "especie": "lubina"
    },
    {
        "nombre": "Wikipedia - Calamar común",
        "url": "https://es.wikipedia.org/wiki/Loligo_vulgaris",
        "especie": "calamar"
    },
    {
        "nombre": "Wikipedia - Dorada",
        "url": "https://es.wikipedia.org/wiki/Sparus_aurata",
        "especie": "dorada"
    },
    {
        "nombre": "Wikipedia - Rodaballo",
        "url": "https://es.wikipedia.org/wiki/Scophthalmus_maximus",
        "especie": "rodaballo"
    },
    {
        "nombre": "Wikipedia - Rape",
        "url": "https://es.wikipedia.org/wiki/Lophius_piscatorius",
        "especie": "rape"
    },
    {
        "nombre": "Wikipedia - Pulpo común",
        "url": "https://es.wikipedia.org/wiki/Octopus_vulgaris",
        "especie": "pulpo"
    },
    {
        "nombre": "Wikipedia - Besugo",
        "url": "https://es.wikipedia.org/wiki/Pagellus_bogaraveo",
        "especie": "besugo"
    },
    {
        "nombre": "Wikipedia - Mero",
        "url": "https://es.wikipedia.org/wiki/Epinephelus_marginatus",
        "especie": "mero"
    },
    {
        "nombre": "Wikipedia - Merluza europea",
        "url": "https://es.wikipedia.org/wiki/Merluccius_merluccius",
        "especie": "merluza"
    },
    {
        "nombre": "Wikipedia - Sargo",
        "url": "https://es.wikipedia.org/wiki/Diplodus_sargus",
        "especie": "sargo"
    },
]


def descargar_pagina(url: str) -> str | None:
    """Descarga el contenido HTML de una URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  [ERROR] No se pudo descargar {url}: {e}")
        return None


def extraer_texto_wikipedia(html: str) -> str:
    """Extrae el texto principal de una página de Wikipedia."""
    soup = BeautifulSoup(html, "html.parser")

    # Eliminar elementos que no aportan contenido útil
    for tag in soup.find_all(["table", "style", "script", "sup", "span.reference"]):
        tag.decompose()

    # Buscar el contenido principal
    contenido = soup.find("div", {"id": "mw-content-text"})
    if not contenido:
        return ""

    parrafos = []
    for p in contenido.find_all("p"):
        texto = p.get_text(separator=" ", strip=True)
        if len(texto) > 60:  # Ignorar párrafos muy cortos
            parrafos.append(texto)

    return "\n\n".join(parrafos[:30])  # Máximo 30 párrafos por página


def generar_id(url: str) -> str:
    """Genera un ID único para cada documento."""
    return hashlib.md5(url.encode()).hexdigest()[:10]


def guardar_documento(especie: str, fuente: str, url: str, texto: str, carpeta: str):
    """Guarda el documento procesado en JSON."""
    doc = {
        "id": generar_id(url),
        "especie": especie,
        "fuente": fuente,
        "url": url,
        "fecha_descarga": datetime.now().isoformat(),
        "caracteres": len(texto),
        "contenido": texto
    }

    nombre_archivo = f"{especie}_{generar_id(url)}.json"
    ruta = os.path.join(carpeta, nombre_archivo)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    return ruta


def ejecutar(carpeta_docs: str = "data/docs") -> list[dict]:
    """Ejecuta el agente buscador y devuelve resumen de resultados."""
    os.makedirs(carpeta_docs, exist_ok=True)

    print("\n" + "="*60)
    print("  🦈 AGENTE BUSCADOR - SharkAI Trainer")
    print("="*60)
    print(f"  Buscando documentación de {len(FUENTES)} especies...\n")

    resultados = []

    for fuente in FUENTES:
        print(f"  📥 Descargando: {fuente['nombre']}")
        html = descargar_pagina(fuente["url"])

        if html:
            texto = extraer_texto_wikipedia(html)

            if len(texto) > 200:
                ruta = guardar_documento(
                    especie=fuente["especie"],
                    fuente=fuente["nombre"],
                    url=fuente["url"],
                    texto=texto,
                    carpeta=carpeta_docs
                )
                resultados.append({
                    "especie": fuente["especie"],
                    "fuente": fuente["nombre"],
                    "ruta": ruta,
                    "caracteres": len(texto),
                    "ok": True
                })
                print(f"     ✅ {len(texto):,} caracteres extraídos → {os.path.basename(ruta)}")
            else:
                print(f"     ⚠️  Contenido insuficiente, ignorando.")
                resultados.append({"especie": fuente["especie"], "ok": False})
        else:
            resultados.append({"especie": fuente["especie"], "ok": False})

        time.sleep(1)  # Respetar los servidores

    exitosos = sum(1 for r in resultados if r.get("ok"))
    print(f"\n  📊 Resultado: {exitosos}/{len(FUENTES)} documentos descargados correctamente.")

    return resultados


if __name__ == "__main__":
    ejecutar()
"""
AGENTE 1 - BUSCADOR INTELIGENTE v2
- Búsqueda automática con DuckDuckGo
- Rotación de términos para no repetir búsquedas
- Historial de URLs visitadas (nunca repite fuentes)
- Extrae descripciones de videos de YouTube
- Busca PDFs, foros, webs científicas, blogs de pesca
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib
import random
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DOMINIOS_BLOQUEADOS = [
    "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
    "amazon.com", "ebay.com", "google.com", "pinterest.com",
    "linkedin.com", "reddit.com"
]

HISTORIAL_FILE = "data/urls_visitadas.json"

# Banco amplio de términos de búsqueda por especie
# Cada ciclo usa términos distintos rotando por el banco
BANCO_BUSQUEDAS = {
    "lubina": [
        "lubina pesca Galicia técnicas temporada",
        "lubina europea biología habitat Atlántico",
        "pesca lubina surfcasting spinning Galicia",
        "lubina ría Galicia señuelos artificiales",
        "Dicentrarchus labrax pesca deportiva España",
        "lubina nocturna pesca técnicas avanzadas",
        "lubina talla mínima normativa España 2024",
        "mejores zonas pesca lubina costa gallega",
    ],
    "calamar": [
        "calamar pesca Galicia jigging egi técnicas",
        "calamar común Loligo vulgaris biología",
        "eging calamar Galicia mejor época",
        "pesca calamar puerto ría Galicia noche",
        "calamar señuelo egi talla tamaño Galicia",
        "técnica jigging calamar Atlántico norte",
        "calamar pesca desde embarcación Galicia",
        "calamar gallego temporada otoño invierno",
    ],
    "dorada": [
        "dorada pesca Galicia ría técnicas cebo",
        "Sparus aurata biología habitat Galicia",
        "dorada surfcasting Galicia mejores puntos",
        "pesca dorada cebo natural gusano mejillón",
        "dorada ría Vigo Arousa Pontevedra pesca",
        "dorada talla mínima legal España normativa",
        "dorada pesca fondo costa atlántica",
        "dorada temporada verano otoño Galicia",
    ],
    "rodaballo": [
        "rodaballo pesca Galicia fondo temporada",
        "Scophthalmus maximus biología pesca",
        "rodaballo pesca embarcación fondo arena",
        "rodaballo Galicia profundidad hábitat",
        "pesca rodaballo cebo natural vivo Galicia",
        "rodaballo talla mínima normativa pesca",
        "rodaballo primavera verano Galicia pesca",
        "rodaballo fondos arenosos costa gallega",
    ],
    "rape": [
        "rape pesca Galicia técnicas biología marina",
        "Lophius piscatorius hábitat Atlántico",
        "rape pesca fondo embarcación Galicia",
        "rape profundidad fondos rocosos Galicia",
        "pesca rape cebo carnada natural",
        "rape talla mínima legal pesca España",
        "rape costa gallega temporada pesca",
        "rape biología reproducción Atlántico norte",
    ],
    "pulpo": [
        "pulpo pesca Galicia potera nasa técnicas",
        "Octopus vulgaris biología Galicia",
        "pesca pulpo costa rocosa Galicia técnicas",
        "pulpo nasa potera diferencias técnicas",
        "pulpo Galicia temporada veda normativa",
        "pulpo fondos rocosos ría gallega hábitat",
        "pesca pulpo embarcación Galicia",
        "pulpo carnada cebo artificial Galicia",
    ],
    "besugo": [
        "besugo pesca Galicia profundidad temporada",
        "Pagellus bogaraveo biología Atlántico",
        "besugo pesca nocturna aguas profundas",
        "besugo Galicia embarcación curricán fondo",
        "besugo talla mínima normativa España",
        "besugo invierno Galicia mejor temporada",
        "besugo costa gallega distribución hábitat",
        "besugo cebo anzuelo técnica pesca",
    ],
    "mero": [
        "mero pesca Galicia rocas técnicas",
        "Epinephelus marginatus biología Atlántico",
        "mero fondos rocosos Galicia pesca submarina",
        "mero protegido normativa pesca España",
        "mero hábitat costa gallega profundidad",
        "mero pesca deportiva Galicia técnicas",
        "mero distribución Atlántico norte biología",
        "mero talla mínima veda normativa pesca",
    ],
    "merluza": [
        "merluza pesca Galicia curricán técnicas",
        "Merluccius merluccius biología hábitat",
        "merluza arrastre pesca Galicia profundidad",
        "merluza pesca deportiva Galicia técnicas",
        "merluza talla mínima legal normativa",
        "merluza Galicia temporada mejor época",
        "merluza fondos Atlántico norte distribución",
        "merluza cebo natural pesca embarcación",
    ],
    "sargo": [
        "sargo pesca Galicia costa técnicas cebo",
        "Diplodus sargus biología hábitat Atlántico",
        "sargo spinning pesca costa Galicia",
        "sargo fondos rocosos costa gallega",
        "sargo cebo cangrejo berberecho pesca",
        "sargo talla mínima normativa España",
        "sargo temporada pesca Galicia verano",
        "sargo pesca surfcasting costa gallega",
    ],
}

# Términos extra para buscar en YouTube
BUSQUEDAS_YOUTUBE = {
    "lubina":    "pesca lubina Galicia spinning tutorial",
    "calamar":   "pesca calamar eging Galicia tutorial",
    "dorada":    "pesca dorada Galicia surfcasting",
    "rodaballo": "pesca rodaballo Galicia embarcación",
    "pulpo":     "pesca pulpo Galicia potera técnica",
    "merluza":   "pesca merluza Galicia curricán tutorial",
}


def cargar_historial() -> set:
    """Carga las URLs ya visitadas para no repetirlas."""
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def guardar_historial(urls: set):
    """Guarda el historial actualizado de URLs visitadas."""
    os.makedirs(os.path.dirname(HISTORIAL_FILE), exist_ok=True)
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(list(urls), f)


def cargar_ciclo_actual() -> int:
    """Lleva la cuenta del ciclo para rotar los términos de búsqueda."""
    archivo = "data/ciclo_actual.json"
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f).get("ciclo", 0)
    return 0


def guardar_ciclo(ciclo: int):
    archivo = "data/ciclo_actual.json"
    os.makedirs("data", exist_ok=True)
    with open(archivo, "w") as f:
        json.dump({"ciclo": ciclo}, f)


def buscar_duckduckgo(query: str, max_resultados: int = 4) -> list[dict]:
    """Busca en DuckDuckGo y devuelve lista de {titulo, url}."""
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query, "kl": "es-es"}
        resp = requests.post(url, data=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        resultados = []

        for result in soup.select(".result__body")[:max_resultados * 3]:
            enlace = result.select_one(".result__url")
            titulo = result.select_one(".result__title")
            if not enlace or not titulo:
                continue

            url_texto = enlace.get_text(strip=True)
            if not url_texto.startswith("http"):
                url_texto = "https://" + url_texto

            if any(bloq in url_texto for bloq in DOMINIOS_BLOQUEADOS):
                continue

            resultados.append({
                "titulo": titulo.get_text(strip=True),
                "url": url_texto
            })

            if len(resultados) >= max_resultados:
                break

        return resultados
    except Exception as e:
        print(f"  [ERROR] DuckDuckGo: {e}")
        return []


def extraer_youtube(url: str) -> str | None:
    """Extrae título, descripción y metadatos de un video de YouTube."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        titulo = soup.find("meta", {"name": "title"})
        descripcion = soup.find("meta", {"name": "description"})
        keywords = soup.find("meta", {"name": "keywords"})

        partes = []
        if titulo:
            partes.append(f"TÍTULO DEL VIDEO: {titulo.get('content', '')}")
        if descripcion:
            partes.append(f"DESCRIPCIÓN: {descripcion.get('content', '')}")
        if keywords:
            partes.append(f"TEMAS: {keywords.get('content', '')}")

        texto = "\n\n".join(partes)
        return texto if len(texto) > 100 else None
    except Exception:
        return None


def descargar_pagina(url: str) -> str | None:
    """Descarga HTML de una URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        if "text/html" not in resp.headers.get("Content-Type", ""):
            return None
        return resp.text
    except Exception as e:
        print(f"     [ERROR] {e}")
        return None


def extraer_texto(html: str) -> str:
    """Extrae el texto principal de cualquier página web."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["script", "style", "nav", "footer",
                               "header", "aside", "form", "iframe"]):
        tag.decompose()

    contenido = None
    for selector in ["article", "main", ".content", ".post",
                     ".entry-content", "#content", ".article-body"]:
        contenido = soup.select_one(selector)
        if contenido:
            break

    if not contenido:
        contenido = soup.find("body") or soup

    parrafos = []
    for p in contenido.find_all(["p", "li", "h2", "h3"]):
        texto = p.get_text(separator=" ", strip=True)
        if len(texto) > 50:
            parrafos.append(texto)

    return "\n\n".join(parrafos[:40])


def generar_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]


def guardar_documento(especie: str, titulo: str, url: str,
                      texto: str, tipo: str, carpeta: str) -> str:
    doc = {
        "id": generar_id(url),
        "especie": especie,
        "fuente": titulo,
        "tipo": tipo,  # "web", "youtube", "foro", etc.
        "url": url,
        "fecha_descarga": datetime.now().isoformat(),
        "caracteres": len(texto),
        "contenido": texto
    }
    nombre = f"{especie}_{generar_id(url)}.json"
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return ruta


def ejecutar(carpeta_docs: str = "data/docs") -> list[dict]:
    os.makedirs(carpeta_docs, exist_ok=True)

    print("\n" + "="*60)
    print("  🦈 AGENTE BUSCADOR v2 - SharkAI Trainer")
    print("="*60)

    # Cargar historial y ciclo actual
    urls_visitadas = cargar_historial()
    ciclo = cargar_ciclo_actual()
    print(f"  📋 Ciclo de búsqueda: #{ciclo + 1}")
    print(f"  🗂️  URLs ya visitadas: {len(urls_visitadas)} (no se repetirán)\n")

    resultados_totales = []
    urls_nuevas = set()

    for especie, banco in BANCO_BUSQUEDAS.items():
        # Rotar el término de búsqueda según el ciclo
        idx = ciclo % len(banco)
        query = banco[idx]

        print(f"  🔍 {especie.upper()}: \"{query}\"")

        # Búsqueda web normal
        fuentes = buscar_duckduckgo(query, max_resultados=3)

        docs_ok = 0
        for fuente in fuentes:
            url = fuente["url"]

            # Saltar si ya visitamos esta URL
            if url in urls_visitadas:
                print(f"     ⏭️  Ya visitada, saltando: {url[:50]}")
                continue

            # Detectar si es YouTube
            es_youtube = "youtube.com/watch" in url

            if es_youtube:
                print(f"     🎬 Video YouTube: {fuente['titulo'][:50]}...")
                texto = extraer_youtube(url)
                tipo = "youtube"
            else:
                print(f"     📥 Web: {fuente['titulo'][:50]}...")
                html = descargar_pagina(url)
                texto = extraer_texto(html) if html else None
                tipo = "web"

            if texto and len(texto) > 150:
                ruta = guardar_documento(especie, fuente["titulo"],
                                         url, texto, tipo, carpeta_docs)
                print(f"        ✅ {len(texto):,} chars [{tipo}] → {os.path.basename(ruta)}")
                urls_nuevas.add(url)
                resultados_totales.append({"especie": especie, "ok": True, "tipo": tipo})
                docs_ok += 1
            else:
                print(f"        ⚠️  Sin contenido suficiente")

            urls_visitadas.add(url)
            time.sleep(1)

        # Buscar también en YouTube para algunas especies
        if especie in BUSQUEDAS_YOUTUBE:
            query_yt = f"site:youtube.com {BUSQUEDAS_YOUTUBE[especie]}"
            fuentes_yt = buscar_duckduckgo(query_yt, max_resultados=2)
            for fuente in fuentes_yt:
                url = fuente["url"]
                if url in urls_visitadas or "youtube.com" not in url:
                    continue
                print(f"     🎬 YouTube: {fuente['titulo'][:50]}...")
                texto = extraer_youtube(url)
                if texto and len(texto) > 100:
                    ruta = guardar_documento(especie, fuente["titulo"],
                                             url, texto, "youtube", carpeta_docs)
                    print(f"        ✅ {len(texto):,} chars [youtube]")
                    urls_nuevas.add(url)
                    resultados_totales.append({"especie": especie, "ok": True, "tipo": "youtube"})
                urls_visitadas.add(url)
                time.sleep(1)

        if docs_ok == 0:
            resultados_totales.append({"especie": especie, "ok": False})

        time.sleep(2)

    # Guardar historial actualizado y avanzar ciclo
    guardar_historial(urls_visitadas)
    guardar_ciclo(ciclo + 1)

    exitosos = sum(1 for r in resultados_totales if r.get("ok"))
    youtubes = sum(1 for r in resultados_totales if r.get("tipo") == "youtube")
    print(f"\n  📊 {exitosos} documentos nuevos ({youtubes} de YouTube)")
    print(f"  🗂️  Total URLs en historial: {len(urls_visitadas)}")

    return resultados_totales


if __name__ == "__main__":
    ejecutar()