import os
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Especie, Spot, Captura, Perfil
from .serializers import EspecieSerializer, SpotSerializer, CapturaSerializer, PerfilSerializer
from .services import get_weather_range, calcular_puntuacion_rango


class EspecieViewSet(viewsets.ModelViewSet):
    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SpotViewSet(viewsets.ModelViewSet):
    serializer_class = SpotSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user

        if user.is_authenticated:
            try:
                perfil_propio = user.perfil
                es_publico_propio = perfil_propio.es_publico
            except Perfil.DoesNotExist:
                es_publico_propio = True

            if es_publico_propio:
                # Ve: spots globales (sin creador) + los suyos propios + los de perfiles públicos
                return Spot.objects.select_related('creador', 'creador__perfil').filter(
                    Q(creador__isnull=True) |          # spots globales
                    Q(creador=user) |                   # los suyos
                    Q(creador__perfil__es_publico=True)  # de usuarios públicos
                ).distinct()
            else:
                # Perfil privado: solo puede ver sus propios spots
                return Spot.objects.select_related('creador', 'creador__perfil').filter(
                    Q(creador=user)
                ).distinct()
        else:
            # Anónimo: no tiene perfil público, no puede ver spots de otros.
            # Solo ve spots globales (sin creador).
            return Spot.objects.select_related('creador', 'creador__perfil').filter(
                creador__isnull=True
            ).distinct()

    def perform_create(self, serializer):
        # Guarda quién creó el spot para aplicar la privacidad después
        serializer.save(creador=self.request.user)


class CapturaViewSet(viewsets.ModelViewSet):
    """
    Todas las capturas son públicas: cualquiera (logueado o no) puede verlas.
    Crear, editar o borrar requiere estar autenticado, y solo sobre las propias.
    """
    serializer_class = CapturaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        from django.db.models import Q
        # Feed público: todas las capturas de todos los usuarios
        qs = Captura.objects.select_related('usuario', 'usuario__perfil', 'especie', 'spot').all()
        user = self.request.user

        if user.is_authenticated:
            try:
                perfil_propio = user.perfil
                es_publico_propio = perfil_propio.es_publico
            except Perfil.DoesNotExist:
                es_publico_propio = True

            if es_publico_propio:
                # Ve las suyas propias y las de otros usuarios con perfil público
                qs = qs.filter(
                    Q(usuario=user) |
                    Q(usuario__perfil__es_publico=True)
                )
            else:
                # Perfil privado: solo puede ver las suyas propias
                qs = qs.filter(usuario=user)
        else:
            # Anónimo: no tiene perfil público, no puede ver de otros.
            # Y no tiene suyas propias, así que no ve nada.
            qs = qs.none()

        especie_id = self.request.query_params.get('especie')
        spot_id    = self.request.query_params.get('spot')
        search     = self.request.query_params.get('search')
        usuario_id = self.request.query_params.get('usuario')
        mias       = self.request.query_params.get('mias')  # "1" para ver solo las propias

        if especie_id:
            qs = qs.filter(especie_id=especie_id)
        if spot_id:
            qs = qs.filter(spot_id=spot_id)
        if search:
            qs = qs.filter(notas__icontains=search)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if mias == '1' and user.is_authenticated:
            qs = qs.filter(usuario=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.usuario_id != request.user.id:
            return Response({"error": "No puedes editar capturas de otro pescador."},
                             status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.usuario_id != request.user.id:
            return Response({"error": "No puedes borrar capturas de otro pescador."},
                             status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(APIView):
    """
    GET  /api/perfil/        -> perfil propio
    GET  /api/perfil/<id>/   -> perfil público de cualquier usuario
    PUT  /api/perfil/        -> editar el propio perfil (avatar, bio, mostrar_nombre, es_publico)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, usuario_id=None):
        if usuario_id:
            perfil = get_object_or_404(Perfil, usuario_id=usuario_id)
            # Si el perfil consultado no es el propio del usuario autenticado
            if not request.user.is_authenticated or request.user.id != int(usuario_id):
                # 1. Comprobar si el perfil consultado es público
                if not perfil.es_publico:
                    return Response({"error": "Este perfil es privado."}, status=status.HTTP_403_FORBIDDEN)
                
                # 2. Comprobar si el solicitante está autenticado
                if not request.user.is_authenticated:
                    return Response({"error": "Debes iniciar sesión y tener perfil público para ver a otros pescadores."}, status=status.HTTP_403_FORBIDDEN)
                
                # 3. Comprobar si el solicitante tiene perfil público
                try:
                    perfil_solicitante = request.user.perfil
                    es_publico_solicitante = perfil_solicitante.es_publico
                except Perfil.DoesNotExist:
                    es_publico_solicitante = False

                if not es_publico_solicitante:
                    return Response({"error": "Debes tener tu perfil público para ver los de los demás."}, status=status.HTTP_403_FORBIDDEN)
        else:
            if not request.user.is_authenticated:
                return Response({"error": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
            perfil = request.user.perfil
        return Response(PerfilSerializer(perfil, context={'request': request}).data)

    def put(self, request, usuario_id=None):
        if not request.user.is_authenticated:
            return Response({"error": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
        perfil = request.user.perfil
        serializer = PerfilSerializer(perfil, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def prediccion(request):
    especie_id = request.query_params.get('especie_id')
    spot_id    = request.query_params.get('spot_id')
    lat_param  = request.query_params.get('lat')
    lon_param  = request.query_params.get('lon')

    if not especie_id:
        return Response({"error": "Falta el parámetro especie_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        especie = Especie.objects.get(pk=especie_id)
    except Especie.DoesNotExist:
        return Response({"error": "Especie no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if spot_id:
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Spot.DoesNotExist:
            return Response({"error": "Spot no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        lat, lon = spot.latitud, spot.longitud
        spot_data = SpotSerializer(spot).data
        nombre_ubicacion = spot.nombre

    elif lat_param and lon_param:
        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except ValueError:
            return Response({"error": "lat y lon deben ser números"}, status=status.HTTP_400_BAD_REQUEST)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response({"error": "Coordenadas fuera de rango"}, status=status.HTTP_400_BAD_REQUEST)
        spot_data = None
        nombre_ubicacion = f"Punto personalizado ({lat:.4f}, {lon:.4f})"

    else:
        return Response(
            {"error": "Indica spot_id o las coordenadas lat y lon"},
            status=status.HTTP_400_BAD_REQUEST
        )

    condiciones_raw = get_weather_range(lat, lon)
    if not condiciones_raw:
        return Response(
            {"error": "No se pudieron obtener datos meteorológicos de Open-Meteo en este momento."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    timeline = calcular_puntuacion_rango(condiciones_raw, especie, lat=lat, lon=lon)

    return Response({
        "spot":             spot_data,
        "nombre_ubicacion": nombre_ubicacion,
        "lat":              lat,
        "lon":              lon,
        "especie":          EspecieSerializer(especie).data,
        "total_horas":      len(timeline),
        "timeline":         timeline
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response(
            {"error": "El nombre de usuario y la contraseña son campos obligatorios."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Este nombre de usuario ya está registrado en O Peirao."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # El Perfil se crea automáticamente vía signal post_save en models.py
    User.objects.create_user(username=username, password=password, email=email)

    return Response(
        {"message": "¡Pescador registrado con éxito!"},
        status=status.HTTP_201_CREATED
    )


def motor_intuicion_galicia_avanzado(especie, presion, viento_velocidad, viento_direccion, marea_momento, coeficiente_marea, nubosidad):
    score = 50  # Puntuación base neutral (sobre 100)
    alertas = []
    recomendaciones = []
    
    especie = especie.lower() if especie else ""
    viento_direccion = viento_direccion.upper() if viento_direccion else ""
    marea_momento = marea_momento.lower() if marea_momento else ""
    
    # --- LÓGICA ULTRA-ESPECÍFICA PARA EGING (CALAMAR / CHOCO) ---
    if especie in ["calamar", "eging", "choco"]:
        if viento_velocidad < 12:
            score += 15
            recomendaciones.append("Excelente control de línea: el viento flojo permite sentir toques sutiles.")
        elif viento_velocidad > 22:
            score -= 30
            alertas.append("Viento excesivo: el Egi no profundizará correctamente y hará mucha bolsa en el sedal.")
            
        if viento_direccion in ["NE", "N", "E"]:
            score += 10
            recomendaciones.append("Viento de componente Norte/Este (Nordés): Enfría y aclara el agua de las rías. Cefalópodos más activos.")
        elif viento_direccion in ["SW", "S", "W"]:
            score -= 15
            alertas.append("Viento del Suroeste/Oeste: Suele meter mar de leva y enturbiar el agua con algas y arena.")

        if marea_momento in ["repunte_pleamar", "repunte_bajamar"]:
            score += 20
            recomendaciones.append("Momento cumbre: Los 30 minutos del repunte de marea son letales.")
        
        if 50 <= coeficiente_marea <= 75:
            score += 10
            recomendaciones.append("Coeficiente medio-óptimo: Corriente perfecta en la ría para dar acción al egi.")
        elif coeficiente_marea > 85:
            score -= 20
            alertas.append("Mareas vivas muy fuertes: Demasiada corriente en los canales. Necesitarás Egis plomados.")

        if nubosidad > 70:
            recomendaciones.append("Estrategia de color: Cielo cubierto / agua tomada. Usa Egis Glow (reactivos) o colores Rosa/Púrpura.")
        else:
            recomendaciones.append("Estrategia de color: Alta luminosidad. Usa Egis con libreas naturales (imitación de xarda o peón).")

    # --- LÓGICA ULTRA-ESPECÍFICA PARA LUBINA (RÓBALO) ---
    elif especie in ["lubina", "robalo"]:
        if 18 <= viento_velocidad <= 35:
            score += 20
            recomendaciones.append("Viento activo idóneo: Levanta la rompiente perfecta para el camuflaje de la lubina.")
        elif viento_velocidad < 8:
            score -= 15
            alertas.append("Mar plato / Sin viento: Aguas demasiado paradas. La lubina detectará el engaño fácilmente.")

        if viento_direccion in ["W", "SW", "NW"]:
            score += 15
            recomendaciones.append("Vientos marinos: Empujan el pasto (lanzones y xardas) hacia las piedras de la costa.")
            
        if presion < 1012:
            score += 15
            recomendaciones.append("Borrasca aproximándose: La caída de presión estimula un frenesí alimenticio.")

    nota_final = max(1, min(100, score))
    return round(nota_final / 10, 1), alertas, recomendaciones


def validar_contenido_pesca(texto):
    if not texto:
        return False
    # Corteza de seguridad anti-pizza e información no relevante
    palabras_prohibidas = ["pizza", "masa", "queixo", "queixo mozzarella", "queso", "horno", "forno", "ingredientes", "salsa", "pepperoni", "tomate frito"]
    texto_lower = texto.lower()
    for palabra in palabras_prohibidas:
        if palabra in texto_lower:
            return False
    return True


FALLBACK_KNOWLEDGE = [
    {
        "texto": "No inverno galego, os peiraos iluminados de Galicia concentran o calamar grande (llión) que se achega a cazar o bolo baixo a luz artificial.",
        "fuente": "Manual de Eging en Galicia (Pág. 12)"
    },
    {
        "texto": "Para a lubina (róbalo) na rompente e escuma, as mellores xornadas son aquelas con vento forte de compoñente Oeste/Suroeste que bate con forza nas pedras.",
        "fuente": "Guía Práctica do Pescador Galego (Sección Lubina)"
    },
    {
        "texto": "A pesca do choco na ría faise sobre todo en fondos de area ou pradeiras de zostera usando egis con cores moi rechamantes como rosa ou laranxa en días escuros.",
        "fuente": "Cadernos de Pesca Rías Baixas"
    },
    {
        "texto": "Ingredientes da pizza: masa de trigo, queixo mozzarella, tona, touciño e forno a 220 graos.",
        "fuente": "Revista Cociña Italiana (Documento Filtrado)"
    }
]


def obtener_contexto_rag(query, persist_directory="chroma_db"):
    # 1. Intentar usar Chroma DB si está disponible y existe el directorio
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        
        # Validar si existe el directorio
        if os.path.exists(persist_directory):
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            base_datos = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
            documentos = base_datos.similarity_search(query, k=3)
            
            for doc in documentos:
                contenido = doc.page_content
                if validar_contenido_pesca(contenido):
                    fuente = doc.metadata.get("fuente", "Manual Local")
                    return contenido, fuente
    except Exception:
        # Fallback silencioso ante cualquier fallo de importación o carga
        pass

    # 2. Motor de búsqueda por palabra clave (Fallback inteligente en gallego/español)
    query_lower = query.lower()
    mejor_doc = None
    max_coincidencias = 0
    
    for doc in FALLBACK_KNOWLEDGE:
        if not validar_contenido_pesca(doc["texto"]):
            continue
            
        palabras = [w for w in query_lower.split() if len(w) > 3]
        coincidencias = sum(1 for w in palabras if w in doc["texto"].lower())
        
        if coincidencias > max_coincidencias:
            max_coincidencias = coincidencias
            mejor_doc = doc

    if mejor_doc:
        return mejor_doc["texto"], mejor_doc["fuente"]
        
    return FALLBACK_KNOWLEDGE[0]["texto"], FALLBACK_KNOWLEDGE[0]["fuente"]


class ChatAsistenteView(APIView):
    """
    POST /api/chat/ -> Asistente de chat de pesca con IA (SharkAI) utilizando Ollama local (Opción B)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import requests
        texto_usuario = request.data.get('texto_usuario', '')
        especie_objetivo = request.data.get('especie_objetivo', 'calamar')
        historial = request.data.get('historial', [])
        
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        if lat is None:
            lat = request.data.get('latitude')
        if lon is None:
            lon = request.data.get('longitude')

        try:
            presion = float(request.data.get('presion', 1013))
            viento_velocidad = float(request.data.get('viento_velocidad', 12))
            nubosidad = int(request.data.get('nubosidad', 50))
        except (ValueError, TypeError):
            presion = 1013.0
            viento_velocidad = 12.0
            nubosidad = 50

        viento_direccion = request.data.get('viento_direccion', 'NE')
        
        # Valores por defecto para la marea
        marea_momento = "repunte_pleamar"
        coeficiente_marea = 60

        # Si tenemos coordenadas, calculamos la marea dinámicamente usando las fórmulas de Galicia
        if lat is not None and lon is not None:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                import math
                from .services import calcular_mareas, calcular_fase_lunar
                luna = calcular_fase_lunar()
                mareas = calcular_mareas(lat_f, lon_f)
                
                nivel = mareas.get("nivel_norm", 0.5)
                estado = mareas.get("estado", "")
                
                if nivel > 0.8:
                    marea_momento = "repunte_pleamar"
                elif nivel < 0.2:
                    marea_momento = "repunte_bajamar"
                elif "subiendo" in estado.lower():
                    marea_momento = "llenante"
                else:
                    marea_momento = "vaciante"
                
                fase_norm = luna.get("fase_norm", 0.5)
                coeficiente_marea = int(70 + 35 * math.cos(2 * math.pi * 2 * fase_norm))
            except Exception:
                # Si falla la conversión o cálculo, mantenemos valores por defecto
                pass

        try:
            # A) Cálculo de la puntuación meteorológica
            nota, alertas, recomendaciones = motor_intuicion_galicia_avanzado(
                especie=especie_objetivo,
                presion=presion,
                viento_velocidad=viento_velocidad,
                viento_direccion=viento_direccion,
                marea_momento=marea_momento,
                coeficiente_marea=coeficiente_marea,
                nubosidad=nubosidad
            )

            # B) Obtener conocimiento RAG de manuales reales (con filtro anti-pizza integrado)
            contexto_manual, fuente_manual = obtener_contexto_rag(texto_usuario)

            # C) Intentar llamar a Ollama localmente (llama3)
            prompt_sistema = (
                "Eres SharkAI, un asistente de pesca experto de Galicia. Hablas con retranca, "
                "estilo marinero y mezclas gallego y castellano con naturalidad (retranca galega). Tu objetivo es responder "
                "la pregunta del usuario usando las condiciones climáticas del mapa, las recomendaciones matemáticas "
                "y el contexto de los manuales aportados. Sé muy específico con las zonas, vientos y trucos."
            )
            
            prompt_usuario = (
                f"Pregunta del pescador: {texto_usuario}\n\n"
                f"Condiciones actuales del mar y viento para {especie_objetivo}:\n"
                f"- Eficiencia calculada: {nota}/10\n"
                f"- Alertas del sistema: {', '.join(alertas) if alertas else 'Ninguna'}\n"
                f"- Recomendaciones del sistema: {', '.join(recomendaciones) if recomendaciones else 'Ninguna'}\n"
                f"- Momento de la marea: {marea_momento}\n"
                f"- Coeficiente de marea: {coeficiente_marea}\n\n"
                f"Datos extraídos del manual de pesca RAG:\n"
                f"'{contexto_manual}' (Fuente: {fuente_manual})\n\n"
                f"Por favor, responde de manera natural, conversacional y experta, abordando directamente la pregunta del pescador."
            )

            # Mapear historial completo para la memoria del modelo
            messages = [{"role": "system", "content": prompt_sistema}]
            for msg in historial:
                # Omitir el primer mensaje de bienvenida de la IA si es genérico para no sesgar
                if msg.get('id') == 'welcome':
                    continue
                role = "assistant" if msg.get("sender") == "ai" else "user"
                messages.append({"role": role, "content": msg.get("text", "")})
            
            messages.append({"role": "user", "content": prompt_usuario})

            ollama_url = "http://127.0.0.1:11434/api/chat"
            payload = {
                "model": "sharkai",
                "messages": messages,
                "stream": False
            }

            try:
                # Timeout de 120 segundos para permitir a inferencia en CPU sen interrumpir
                response = requests.post(ollama_url, json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    respuesta_final = data.get("message", {}).get("content", "")
                else:
                    raise Exception(f"Ollama devolvió código {response.status_code}")
            except Exception as e:
                # Fallback en caso de que Ollama no esté iniciado o no tenga sharkai
                print(f"[SHARKAI] Falló la llamada a Ollama: {e}")
                referencia_historial = ""
                if historial:
                    preguntas_previas = [m.get('text', '') for m in historial if m.get('sender') == 'user']
                    if preguntas_previas:
                        referencia_historial = f"*(Tendo en conta o que falamos antes sobre '{preguntas_previas[-1][:35]}...'*)\n\n"

                saludo = f"⚠️ *[Modo Simulación - Ollama apagado ou sen modelo sharkai]*\n\n¡Ola, patrón! Analizando as condicións actuais para a pesca de {especie_objetivo}...\n\n"

                if nota >= 7.0:
                    analisis_clima = f"🟢 ¡Día moi prometedor! Doulle un {nota}/10 ao estado do mar. " + " ".join(recomendaciones)
                else:
                    analisis_clima = f"🔴 As condicións están complicadas para esa modalidade (Nota: {nota}/10).\n"
                    if alertas:
                        analisis_clima += "\n".join([f"⚠️ {a}" for a in alertas])
                    else:
                        analisis_clima += "Recoméndase precaución ou cambiar de estratexia."

                consejos_extra = ""
                if recomendaciones:
                    consejos_extra = f"\n\n💡 Truco do asistente: " + " ".join(recomendaciones[-1:])
                contexto_manuales = f"\n\n📚 **Consello extraído de: {fuente_manual}**\n{contexto_manual}"

                respuesta_final = f"{referencia_historial}{saludo}{analisis_clima}{consejos_extra}{contexto_manuales}"

            return Response({
                "status": "success",
                "respuesta_chat": respuesta_final,
                "eficiencia_pesca": nota
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)