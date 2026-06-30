# 🦈 SharkAI Self-Trainer
### Sistema de Auto-Mejora para Pesca en Galicia

---

## ¿Qué hace este sistema?

Convierte tu modelo `sharkai` en un experto en pesca gallega de forma automática:

1. **Agente Buscador** → Descarga documentación científica de internet (lubina, calamar, dorada, rodaballo, etc.)
2. **Agente Procesador** → Usa la propia IA para extraer conocimiento útil para pescadores
3. **Agente Evaluador** → Pone a prueba a SharkAI con preguntas reales de pesca y le puntúa
4. **Agente Generador** → Crea una versión mejorada del modelo (`sharkai-galicia`) con todo el conocimiento

Cada ciclo, el modelo aprende más sobre las especies gallegas y mejora sus respuestas.

---

## Requisitos

- Windows 10/11
- Python 3.10 o superior
- Ollama instalado y ejecutándose con el modelo `sharkai`

---

## Instalación (solo la primera vez)

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
pip install -r requirements.txt
```

---

## Uso

### Ciclo completo de entrenamiento (recomendado)
```powershell
python main.py
```

### Múltiples ciclos para mayor especialización
```powershell
python main.py --ciclos 3
```

### Solo evaluar sin entrenar (para ver cómo va)
```powershell
python main.py --test
```

---

## ¿Cómo usar el modelo mejorado?

Después de cada ciclo, se crea un nuevo modelo en Ollama:

```powershell
# Usar el modelo mejorado
ollama run sharkai-galicia:v1

# Ver todos los modelos disponibles
ollama list
```

---

## Especies que aprende

| Especie     | Zona principal         | Técnica típica     |
|-------------|------------------------|--------------------|
| Lubina      | Rías, surf, costa      | Spinning, surfcasting |
| Calamar     | Rías Bajas, puertos    | Jigging, egi       |
| Dorada      | Rías Bajas             | Fondo, surfcasting |
| Rodaballo   | Fondos arenosos        | Fondo              |
| Rape        | Fondos rocosos         | Fondo              |
| Pulpo       | Costa rocosa           | Potera, nasa       |
| Besugo      | Aguas profundas        | Curricán, fondo    |
| Mero        | Rocas, fondos          | Fondo              |
| Merluza     | Aguas abiertas         | Curricán, fondo    |
| Sargo       | Costa rocosa           | Fondo, spinning    |

---

## Estructura de archivos

```
sharkai-trainer/
├── main.py                    ← Punto de entrada principal
├── requirements.txt           ← Dependencias Python
├── agents/
│   ├── agente_buscador.py     ← Descarga documentación de internet
│   ├── agente_procesador.py   ← Extrae conocimiento con IA
│   ├── agente_evaluador.py    ← Evalúa y puntúa respuestas
│   └── agente_generador.py    ← Genera el modelo mejorado
├── data/
│   ├── docs/                  ← Documentos descargados de internet
│   └── knowledge/             ← Conocimiento estructurado por especie
├── logs/                      ← Informes de evaluación
└── reports/                   ← Modelfiles generados
```

---

## Solución de problemas

**"Ollama no está ejecutándose"**
```powershell
ollama serve
```

**"Modelo sharkai no encontrado"**
```powershell
ollama list   # Comprueba qué modelos tienes
```

**El procesador no genera JSON válido**
→ Es normal que ocurra a veces. El sistema continúa con los documentos que sí procesa bien.

---

## Próximos pasos sugeridos

1. Ejecuta 3 ciclos seguidos: `python main.py --ciclos 3`
2. Añade tus propios PDFs o bitácoras de pesca en `data/docs/`
3. Añade nuevas fuentes en `agents/agente_buscador.py` (sección `FUENTES`)
4. Personaliza las preguntas de evaluación en `agents/agente_evaluador.py`
