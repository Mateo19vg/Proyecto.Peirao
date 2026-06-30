"""
╔══════════════════════════════════════════════════════════════╗
║           🦈  SHARKAI SELF-TRAINER  🦈                       ║
║      Sistema de Auto-Mejora para Pesca en Galicia            ║
╚══════════════════════════════════════════════════════════════╝

MODO DE USO:
    python main.py              → Ciclo completo de entrenamiento
    python main.py --test       → Solo evaluar sin entrenar
    python main.py --ciclos 3   → Repetir el ciclo N veces

AGENTES:
    1. Buscador  → Descarga documentación de internet
    2. Procesador → Extrae conocimiento con la IA
    3. Evaluador  → Puntúa las respuestas de SharkAI
    4. Generador  → Crea una versión mejorada del modelo
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime

# Añadir la carpeta de agentes al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False


def color(texto, c=""):
    if not COLOR:
        return texto
    colores = {
        "cyan": Fore.CYAN, "green": Fore.GREEN, "yellow": Fore.YELLOW,
        "red": Fore.RED, "magenta": Fore.MAGENTA, "white": Fore.WHITE
    }
    return f"{colores.get(c, '')}{texto}{Style.RESET_ALL}"


def banner():
    print(color("""
╔══════════════════════════════════════════════════════════════╗
║           🦈  SHARKAI SELF-TRAINER  🦈                       ║
║      Sistema de Auto-Mejora para Pesca en Galicia            ║
╚══════════════════════════════════════════════════════════════╝
""", "cyan"))


def verificar_ollama():
    """Comprueba que Ollama está disponible."""
    import requests
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = resp.json()
        modelos = [m["name"] for m in data.get("models", [])]
        sharkai_disponible = any("sharkai" in m for m in modelos)

        print(color("  ✅ Ollama conectado correctamente", "green"))
        print(f"  📦 Modelos disponibles: {', '.join(modelos) or 'ninguno'}")

        if not sharkai_disponible:
            print(color("  ⚠️  Modelo 'sharkai' no encontrado.", "yellow"))
            print("  Asegúrate de que el modelo está descargado con: ollama list")
            return False
        return True
    except Exception:
        print(color("  ❌ Ollama no está ejecutándose.", "red"))
        print("  Inicia Ollama con: ollama serve")
        print("  O simplemente abre la app de Ollama en Windows.")
        return False


def guardar_historial(ciclo: int, resumen: dict, archivo: str = "logs/historial.json"):
    """Guarda el historial de mejora a lo largo de los ciclos."""
    historial = []
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            historial = json.load(f)

    historial.append({
        "ciclo": ciclo,
        "fecha": datetime.now().isoformat(),
        "puntuacion": resumen.get("puntuacion_media", 0),
        "nivel": resumen.get("nivel_actual", ""),
        "especies": resumen.get("especies_procesadas", 0)
    })

    os.makedirs("logs", exist_ok=True)
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

    return historial


def mostrar_progreso(historial: list):
    """Muestra la evolución de SharkAI a lo largo de los ciclos."""
    if len(historial) < 2:
        return

    print(color("\n  📈 EVOLUCIÓN DE SHARKAI:", "magenta"))
    for h in historial:
        barra = "█" * int(h["puntuacion"])
        espacio = "░" * (10 - int(h["puntuacion"]))
        print(f"  Ciclo {h['ciclo']}: [{barra}{espacio}] {h['puntuacion']:.1f}/10 - {h['nivel']}")


def ejecutar_ciclo(ciclo: int, solo_evaluar: bool = False) -> dict:
    """Ejecuta un ciclo completo de entrenamiento."""
    print(color(f"\n{'='*60}", "cyan"))
    print(color(f"  CICLO {ciclo} - {datetime.now().strftime('%H:%M:%S')}", "cyan"))
    print(color(f"{'='*60}", "cyan"))

    resumen = {"ciclo": ciclo}

    if not solo_evaluar:
        # FASE 1: Buscar documentación
        print(color("\n  [FASE 1/4] 🌐 Buscando documentación en internet...", "yellow"))
        import agente_buscador
        resultados_busqueda = agente_buscador.ejecutar()
        docs_ok = sum(1 for r in resultados_busqueda if r.get("ok"))
        resumen["docs_descargados"] = docs_ok
        print(color(f"  → {docs_ok} documentos descargados", "green"))

        time.sleep(2)

        # FASE 2: Procesar y extraer conocimiento
        print(color("\n  [FASE 2/4] 🧠 Extrayendo conocimiento con IA...", "yellow"))
        import agente_procesador
        conocimientos = agente_procesador.ejecutar()
        resumen["especies_procesadas"] = len(conocimientos)
        print(color(f"  → {len(conocimientos)} especies procesadas", "green"))

        time.sleep(2)
    else:
        print(color("\n  ℹ️  Modo solo-evaluación: saltando fases de búsqueda.", "yellow"))

    # FASE 3: Evaluar a SharkAI
    print(color("\n  [FASE 3/4] 🎯 Evaluando respuestas de SharkAI...", "yellow"))
    import agente_evaluador
    informe = agente_evaluador.ejecutar_evaluacion()
    resumen["puntuacion_media"] = informe.get("puntuacion_media", 0)
    resumen["nivel_actual"] = informe.get("nivel_actual", "")
    print(color(f"  → Puntuación: {informe.get('puntuacion_media', 0):.1f}/10 - {informe.get('nivel_actual', '')}", "green"))

    if not solo_evaluar:
        time.sleep(2)

        # FASE 4: Generar modelo mejorado
        print(color("\n  [FASE 4/4] 🔧 Generando modelo mejorado...", "yellow"))
        import agente_generador
        resultado_gen = agente_generador.ejecutar()
        resumen["modelo_generado"] = resultado_gen.get("nombre_modelo", "")
        resumen["creado_en_ollama"] = resultado_gen.get("creado_en_ollama", False)

        if resultado_gen.get("creado_en_ollama"):
            print(color(f"  → ✅ Nuevo modelo: {resultado_gen.get('nombre_modelo')}", "green"))
        else:
            print(color(f"  → 📄 Modelfile listo en: {resultado_gen.get('modelfile', '')}", "yellow"))

    return resumen


def main():
    parser = argparse.ArgumentParser(description="SharkAI Self-Trainer")
    parser.add_argument("--test", action="store_true", help="Solo evaluar sin entrenar")
    parser.add_argument("--ciclos", type=int, default=1, help="Número de ciclos de entrenamiento")
    args = parser.parse_args()

    banner()

    # Verificar Ollama
    print(color("  🔍 Verificando conexión con Ollama...", "white"))
    if not verificar_ollama():
        print(color("\n  ❌ No se puede continuar sin Ollama. Revisa la conexión.", "red"))
        sys.exit(1)

    print(color(f"\n  🎯 Configuración:", "white"))
    print(f"     Modo: {'Solo evaluación' if args.test else 'Entrenamiento completo'}")
    print(f"     Ciclos: {args.ciclos}")
    print(f"     Hora inicio: {datetime.now().strftime('%H:%M:%S')}")

    historial = []
    for ciclo in range(1, args.ciclos + 1):
        resumen = ejecutar_ciclo(ciclo, solo_evaluar=args.test)
        historial = guardar_historial(ciclo, resumen)

        if ciclo < args.ciclos:
            pausa = 5
            print(color(f"\n  ⏳ Pausa entre ciclos... ({pausa}s)", "yellow"))
            time.sleep(pausa)

    # Resumen final
    mostrar_progreso(historial)

    ultimo = historial[-1] if historial else {}
    print(color("\n" + "="*60, "cyan"))
    print(color("  🏁 ENTRENAMIENTO COMPLETADO", "cyan"))
    print(color("="*60, "cyan"))
    print(f"\n  Puntuación final: {ultimo.get('puntuacion', 0):.1f}/10")
    print(f"  Nivel alcanzado: {ultimo.get('nivel', 'N/A')}")

    if not args.test:
        print(color(f"\n  💡 Para usar tu SharkAI mejorado:", "green"))
        print(f"     ollama run sharkai-galicia:v{args.ciclos}")
        print(f"\n  📁 Archivos generados:")
        print(f"     data/knowledge/ → Conocimiento extraído por especie")
        print(f"     logs/           → Informes de evaluación")
        print(f"     reports/        → Modelfiles generados")

    print()


if __name__ == "__main__":
    main()
