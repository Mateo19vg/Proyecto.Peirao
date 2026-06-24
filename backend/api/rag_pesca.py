import chromadb
from chromadb.utils import embedding_functions
import os

# Cliente ChromaDB persistente
chroma_client = chromadb.PersistentClient(path="./chroma_pesca_db")

# Embeddings en español (modelo pequeño, funciona offline)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

collection = chroma_client.get_or_create_collection(
    name="conocimiento_pesca",
    embedding_function=embedding_fn
)

def indexar_conocimiento():
    """Ejecutar una sola vez para poblar la base de datos."""
    documentos = [
        {
            "id": "eging_001",
            "texto": "El eging nocturno en Galicia funciona mejor en el repunte de pleamar. El calamar (llión) sube a superficie atraído por la luz artificial de los muelles. Usar egi 2.5 fluorescente o con tira UV. Movimiento: 3 tirones cortos y pausa larga de 5 segundos. La picada llega en la pausa, se nota como un peso muerto en el sedal.",
            "zona": "galicia_general", "especie": "calamar"
        },
        {
            "id": "portonovo_001", 
            "texto": "Portonovo: El muelle viejo (peirao vello) es el punto de referencia para calamar y choco. Con viento Nordés el puerto queda completamente abrigado. Las farolas del muelle atraen zooplancton y tras él al calamar. Profundidad útil 4-8 metros junto a la escollera. Caneliñas funciona bien en llenante con fondo limpio de arena.",
            "zona": "portonovo", "especie": "calamar"
        },
        {
            "id": "lubina_galicia_001",
            "texto": "Lubina en Galicia: Los mejores puntos son desembocaduras de ríos (Ulla, Umia, Miño), rompeolas con marejada y canales entre bateas. Con viento SW y agua turbia la lubina se acerca a la orilla a cazar. Señuelos: slug de 14-18cm en colores oscuros de noche, popper en superficie al amanecer. Talla mínima 36cm obligatoria.",
            "zona": "galicia_general", "especie": "lubina"
        },
        {
            "id": "mareas_coeficiente_001",
            "texto": "Coeficientes de marea en Galicia: Coeficiente 95-120 son mareas vivas extremas, corrientes muy fuertes, evitar zonas expuestas. Coeficiente 70-90 mareas vivas normales, buen movimiento de agua, activa la pesca. Coeficiente 45-70 mareas medias, ideales para eging y surfcasting. Coeficiente 20-45 aguas muertas, poca actividad de corriente, los peces están menos activos.",
            "zona": "galicia_general", "especie": "general"
        },
        {
            "id": "viento_nordeste_001",
            "texto": "Viento Nordés en Rías Baixas: Es el mejor viento para pescar en las rías. Al soplar de tierra, aclara el agua, baja la temperatura superficial y genera surgencia de agua rica en nutrientes. Las zonas abrigadas de la ría (orilla sur en Ría de Pontevedra) quedan en calma total. Para calamar es excepcional: agua cristalina y sin oleaje.",
            "zona": "rias_baixas", "especie": "general"
        },
        {
            "id": "baiona_001",
            "texto": "Baiona (Ría de Vigo): El castillo de Monte Real y el muelle deportivo son los mejores puntos para calamar nocturno. La Playa de Ladeira funciona para lubina y dorada en surf. Con viento norte, la Playa América queda completamente abrigada. El canal de entrada a la ría concentra corriente y peces en los cambios de marea.",
            "zona": "baiona", "especie": "calamar"
        },
    ]
    
    texts = [d["texto"] for d in documentos]
    ids = [d["id"] for d in documentos]
    metadatas = [{"zona": d["zona"], "especie": d["especie"]} for d in documentos]
    
    collection.add(documents=texts, ids=ids, metadatas=metadatas)
    print(f"✅ {len(documentos)} documentos indexados en ChromaDB")

def buscar_contexto_rag(consulta: str, zona: str = None, n_results: int = 3) -> str:
    """Busca el conocimiento más relevante para la consulta del pescador."""
    where = {"zona": zona} if zona else None
    
    results = collection.query(
        query_texts=[consulta],
        n_results=n_results,
        where=where
    )
    
    if not results["documents"][0]:
        return ""
    
    contexto = "\n\n".join(results["documents"][0])
    return contexto