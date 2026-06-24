import React, { useState, useEffect, useRef } from 'react'
import { enviarMensajeChat, getEspecies } from '../services/api'
import MapPicker from '../components/MapPicker'

export default function Chat() {
  const [especies, setEspecies] = useState([])
  const [especieObjetivo, setEspecieObjetivo] = useState('calamar')
  
  // Modos de localización: 'actual' o 'mapa'
  const [modoLocalizacion, setModoLocalizacion] = useState('actual')
  const [lat, setLat] = useState(null)
  const [lng, setLng] = useState(null)
  const [weatherInfo, setWeatherInfo] = useState(null)
  const [weatherLoading, setWeatherLoading] = useState(false)

  const [mensajes, setMensajes] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text: '¡Ola, patrón! Son SharkAI, o teu asistente intelixente de pesca. Escolle a especie e activa a localización (mediante o teu GPS ou premendo no mapa) para obter un consello adaptado con datos meteorolóxicos en tiempo real de Open-Meteo.',
      eficiencia: null
    }
  ])
  const [textoUsuario, setTextoUsuario] = useState('')
  const [cargando, setCargando] = useState(false)
  const [eficienciaActual, setEficienciaActual] = useState(null)

  const chatEndRef = useRef(null)

  useEffect(() => {
    getEspecies().then(res => setEspecies(res.results || res || []))
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes])

  const getWindDirection = (deg) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    const index = Math.round(((deg % 360) / 45)) % 8
    return directions[index]
  }

  const cargarClima = async (latitude, longitude) => {
    setWeatherLoading(true)
    try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover&timezone=auto`
      const res = await fetch(url)
      const data = await res.json()
      if (data && data.current) {
        setWeatherInfo(data.current)
      }
    } catch (err) {
      console.error("Erro cargando clima de Open-Meteo:", err)
      alert("Non se puido conectar con Open-Meteo. Inténtao de novo.")
    } finally {
      setWeatherLoading(false)
    }
  }

  const obtenerClimaActual = () => {
    if (!navigator.geolocation) {
      alert("A xeolocalización non está soportada polo teu navegador.")
      return
    }
    setWeatherLoading(true)
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const latitude = position.coords.latitude
        const longitude = position.coords.longitude
        setLat(latitude)
        setLng(longitude)
        await cargarClima(latitude, longitude)
      },
      (error) => {
        console.error("Erro GPS:", error)
        alert("Non se puido obter a túa localización. Por favor, utiliza a opción do mapa.")
        setWeatherLoading(false)
      }
    )
  }

  const handleMapChange = async (latitude, longitude) => {
    setLat(latitude)
    setLng(longitude)
    await cargarClima(latitude, longitude)
  }

  const handleEnviar = async (e, textoPredefinido = null) => {
    if (e) e.preventDefault()
    const mensajeAEnviar = textoPredefinido || textoUsuario
    if (!mensajeAEnviar.trim() || cargando) return

    // Añadir mensaje del usuario
    const mensajeUser = {
      id: Date.now().toString(),
      sender: 'user',
      text: mensajeAEnviar
    }
    setMensajes(prev => [...prev, mensajeUser])
    setTextoUsuario('')
    setCargando(true)

    try {
      const payload = {
        texto_usuario: mensajeAEnviar,
        historial: mensajes.slice(-4),
        especie_objetivo: especieObjetivo,
      }

      if (lat !== null && lng !== null) {
        payload.lat = lat
        payload.lon = lng
      }
      if (weatherInfo) {
        payload.presion = weatherInfo.pressure_msl
        payload.viento_velocidad = weatherInfo.wind_speed_10m
        payload.viento_direccion = getWindDirection(weatherInfo.wind_direction_10m)
        payload.nubosidad = weatherInfo.cloud_cover
      }

      const response = await enviarMensajeChat(payload)

      if (response && response.respuesta_chat) {
        setMensajes(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: response.respuesta_chat,
          eficiencia: response.eficiencia_pesca
        }])
        if (response.eficiencia_pesca !== undefined) {
          setEficienciaActual(response.eficiencia_pesca)
        }
      }
    } catch (error) {
      setMensajes(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: '⚠️ Ocorreu un erro ao conectar con SharkAI. Por favor, volve a intentalo en uns instantes.',
        eficiencia: null
      }])
    } finally {
      setCargando(false)
    }
  }

  const sugerencias = [
    { label: '🎣 Recomendas ir pescar hoxe?', query: 'Con estas condicións actuais, cres que é un bo día para ir pescar e obter bos resultados?' },
    { label: '🦑 Que estratexia de cor uso?', query: 'Tendo en conta o estado do ceo e nubosidade, que cores de señuelo me recomendas utilizar hoxe?' },
    { label: '💨 Inflúe moito a dirección do vento?', query: 'Como afecta a dirección do vento de hoxe á actividade dos peixes e a zona onde se alimentan?' }
  ]

  return (
    <div className="max-w-6xl mx-auto pt-6 px-4">
      <div className="flex flex-col md:flex-row h-[calc(100vh-144px)] gap-0 rounded-2xl overflow-hidden shadow-xl border border-gray-200 bg-white">
        
        {/* Panel Izquierdo: Ubicación y Clima */}
        <div className="w-full md:w-96 border-b md:border-b-0 md:border-r border-gray-200 flex flex-col bg-slate-50 overflow-y-auto">
          <div className="px-6 py-5 border-b border-gray-200 bg-white">
            <div className="flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <h2 className="text-base font-bold text-ocean-900 tracking-tight">SharkAI Localización</h2>
            </div>
            <p className="text-xs text-gray-400 mt-1">Obtén datos reais de Open-Meteo mediante GPS ou Mapa.</p>
          </div>

          <div className="p-6 space-y-5">
            {/* Especie */}
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Especie Obxectivo</label>
              <select
                className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-ocean-500 bg-white shadow-sm font-semibold text-gray-700"
                value={especieObjetivo}
                onChange={e => setEspecieObjetivo(e.target.value)}
              >
                <option value="calamar">🦑 Calamar (Eging)</option>
                <option value="choco">🐙 Choco</option>
                <option value="lubina">🐟 Lubina (Róbalo)</option>
              </select>
            </div>

            {/* Selector de Modo */}
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Modo de Localización</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => { setModoLocalizacion('actual'); setLat(null); setLng(null); setWeatherInfo(null) }}
                  className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                    modoLocalizacion === 'actual'
                      ? 'bg-ocean-700 border-ocean-700 text-white shadow-sm'
                      : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  📍 Ubicación Actual
                </button>
                <button
                  type="button"
                  onClick={() => { setModoLocalizacion('mapa'); setLat(null); setLng(null); setWeatherInfo(null) }}
                  className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                    modoLocalizacion === 'mapa'
                      ? 'bg-ocean-700 border-ocean-700 text-white shadow-sm'
                      : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  🗺️ Designar en Mapa
                </button>
              </div>
            </div>

            {/* Contenido según Modo */}
            {modoLocalizacion === 'actual' ? (
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={obtenerClimaActual}
                  className="w-full bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 font-semibold py-3 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-sm transition-all"
                >
                  <span>📡 Obtener clima en mi posición GPS</span>
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Preme no mapa para pinchar o punto de pesca:</label>
                <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm relative z-0">
                  <MapPicker lat={lat} lng={lng} onChange={handleMapChange} />
                </div>
              </div>
            )}

            {/* Tarjeta de Clima Cargado */}
            {weatherLoading ? (
              <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center justify-center py-8">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-ocean-700 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-xs font-semibold text-gray-500">Cargando Open-Meteo...</span>
                </div>
              </div>
            ) : weatherInfo ? (
              <div className="bg-white rounded-2xl p-5 border border-ocean-100 shadow-sm space-y-4">
                <h3 className="text-xs font-bold text-ocean-900 uppercase tracking-wider flex items-center gap-1">
                  <span>🌦️</span> Condicións climáticas reais
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-50/70 p-2.5 rounded-xl border border-gray-100">
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">Temperatura</span>
                    <span className="font-bold text-gray-700 text-sm mt-0.5 block">{weatherInfo.temperature_2m} °C</span>
                  </div>
                  <div className="bg-slate-50/70 p-2.5 rounded-xl border border-gray-100">
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">Vel. Vento</span>
                    <span className="font-bold text-gray-700 text-sm mt-0.5 block">{weatherInfo.wind_speed_10m} km/h</span>
                  </div>
                  <div className="bg-slate-50/70 p-2.5 rounded-xl border border-gray-100">
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">Dir. Vento</span>
                    <span className="font-bold text-gray-700 text-sm mt-0.5 block">{getWindDirection(weatherInfo.wind_direction_10m)} ({weatherInfo.wind_direction_10m}°)</span>
                  </div>
                  <div className="bg-slate-50/70 p-2.5 rounded-xl border border-gray-100">
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold font-sans">Presión</span>
                    <span className="font-bold text-gray-700 text-sm mt-0.5 block">{weatherInfo.pressure_msl} hPa</span>
                  </div>
                </div>
                <div className="bg-slate-50/70 p-2.5 rounded-xl border border-gray-100 flex justify-between items-center text-xs">
                  <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">Nubosidade</span>
                    <span className="font-bold text-gray-700">{weatherInfo.cloud_cover}%</span>
                  </div>
                  <div className="w-16 bg-gray-200 h-2 rounded-full overflow-hidden">
                    <div className="bg-ocean-600 h-full" style={{ width: `${weatherInfo.cloud_cover}%` }} />
                  </div>
                </div>
                <div className="text-[9px] text-gray-400 text-center font-mono">
                  GPS: {lat?.toFixed(5)}, {lng?.toFixed(5)}
                </div>
              </div>
            ) : (
              <div className="bg-ocean-50/50 border border-ocean-100/50 rounded-2xl p-5 text-center">
                <span className="text-2xl block mb-2">📡</span>
                <p className="text-xs text-ocean-900 font-semibold">Faltan datos de localización</p>
                <p className="text-[11px] text-gray-400 mt-1">Activa a túa ubicación ou preme un punto no mapa para que o asistente poida capturar a meteoroloxía real.</p>
              </div>
            )}
          </div>

          {/* Tarjeta de eficiencia resultante */}
          {eficienciaActual !== null && (
            <div className="mt-auto p-6 border-t border-gray-200 bg-white">
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Nota de Eficiencia Calculada</p>
              <div className="flex items-center gap-3.5 bg-ocean-50 border border-ocean-100 p-4 rounded-2xl">
                <div className="text-3xl font-extrabold text-ocean-700 font-mono">{eficienciaActual}</div>
                <div>
                  <p className="text-xs font-bold text-ocean-900">Puntuación / 10</p>
                  <p className="text-[10px] text-gray-500">Estimación biolóxica-climatolóxica real.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Panel Derecho: Chat interactivo */}
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50/50">
          
          {/* Chat Messages Area */}
          <div className="flex-grow overflow-y-auto p-6 space-y-4">
            {mensajes.map((m, i) => (
              <div
                key={m.id}
                className={`flex gap-3 max-w-[85%] ${m.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold shadow-sm ${
                  m.sender === 'user' ? 'bg-ocean-700 text-white' : 'bg-white border border-gray-100 text-ocean-900'
                }`}>
                  {m.sender === 'user' ? '🎣' : '🦈'}
                </div>

                {/* Bubble */}
                <div className={`rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-ocean-700 text-white rounded-tr-none'
                    : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'
                }`}>
                  <p className="whitespace-pre-line">{m.text}</p>
                  
                  {m.eficiencia !== null && (
                    <div className="mt-3.5 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs">
                      <span className="font-semibold text-gray-500">Eficiencia estimada:</span>
                      <span className={`px-2.5 py-0.5 rounded-full font-bold font-mono text-white ${
                        m.eficiencia >= 7.0 ? 'bg-green-500' : m.eficiencia >= 5.0 ? 'bg-amber-500' : 'bg-red-500'
                      }`}>
                        {m.eficiencia}/10
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {cargando && (
              <div className="flex gap-3 max-w-[80%]">
                <div className="w-8 h-8 rounded-full bg-white border border-gray-100 flex items-center justify-center text-sm shadow-sm">
                  🦈
                </div>
                <div className="bg-white text-gray-700 border border-gray-100 rounded-2xl rounded-tl-none px-5 py-3.5 shadow-sm text-sm">
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick suggestions */}
          {mensajes.length === 1 && (
            <div className="px-6 py-3 bg-white border-t border-gray-100">
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Preguntas de exemplo</p>
              <div className="flex flex-wrap gap-2">
                {sugerencias.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleEnviar(null, s.query)}
                    className="bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-600 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all shadow-sm"
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message Input Form */}
          <div className="p-4 bg-white border-t border-gray-200">
            <form onSubmit={handleEnviar} className="flex gap-2">
              <input
                type="text"
                placeholder="Pregúntalle a SharkAI (ex: 'É un bo día para pescar lubinas?', 'que señuelo uso con Nordés?')..."
                value={textoUsuario}
                onChange={e => setTextoUsuario(e.target.value)}
                className="flex-grow border border-gray-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-ocean-500 bg-gray-50 focus:bg-white transition-all shadow-inner"
              />
              <button
                type="submit"
                disabled={!textoUsuario.trim() || cargando}
                className="bg-ocean-700 text-white rounded-xl px-5 hover:bg-ocean-900 disabled:opacity-40 transition-all font-semibold text-sm flex items-center gap-1.5 shadow-sm"
              >
                <span>Enviar</span>
                <span>✈️</span>
              </button>
            </form>
          </div>

        </div>

      </div>
    </div>
  )
}
