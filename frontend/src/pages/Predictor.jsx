import React, { useState, useEffect } from 'react'
import { getSpots, getEspecies, getPrediccion } from '../services/api'
import { MapContainer, TileLayer, Marker, Popup, LayersControl, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import markerIcon   from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

L.Marker.prototype.options.icon = L.icon({
  iconUrl: markerIcon, shadowUrl: markerShadow,
  iconSize: [25, 41], iconAnchor: [12, 41],
})

const IconoRojo = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: markerShadow,
  iconSize: [25, 41], iconAnchor: [12, 41],
})

const FACTOR_LABELS = {
  temperatura_agua: { label: 'Temperatura agua', max: 20 },
  viento:           { label: 'Viento',            max: 15 },
  estado_mar:       { label: 'Estado del mar',    max: 15 },
  claridad_agua:    { label: 'Claridad del agua', max: 10 },
  luna:             { label: 'Fase lunar',        max: 20 },
  mareas:           { label: 'Mareas',            max: 20 },
}

function obtenerColorHex(puntuacion) {
  if (puntuacion >= 80) return '#22c55e' // Excelente (Verde)
  if (puntuacion >= 65) return '#06b6d4' // Bueno (Cian)
  if (puntuacion >= 50) return '#f59e0b' // Regular (Naranja)
  if (puntuacion >= 35) return '#f97316' // Malo (Naranja Oscuro)
  return '#ef4444' // Muy malo (Rojo)
}

function ClickHandler({ onMapClick }) {
  useMapEvents({ click(e) { onMapClick(e.latlng.lat, e.latlng.lng) } })
  return null
}

function BarraFactor({ nombre, puntos, max, nota }) {
  const pct = Math.round((puntos / max) * 100)

  const color =
    pct >= 80 ? '#22c55e' : 
    pct >= 65 ? '#06b6d4' : 
    pct >= 50 ? '#f59e0b' : 
    pct >= 35 ? '#f97316' : '#ef4444'

  const label = FACTOR_LABELS[nombre]?.label || nombre

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <span className="text-xs font-semibold text-gray-400">{puntos}/{max}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-1.5">
        <div className="h-1.5 rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      {nota && <p className="text-xs text-gray-400 mt-0.5">{nota}</p>}
    </div>
  )
}

function ScoreRing({ puntuacion }) {
  const color = obtenerColorHex(puntuacion)
  const r = 36, circ = 2 * Math.PI * r
  const tramo = (puntuacion / 100) * circ
  return (
    <div className="flex flex-col items-center">
      <svg width="88" height="88" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" stroke="#e5e7eb" strokeWidth="7" />
        <circle cx="45" cy="45" r={r} fill="none" stroke={color} strokeWidth="7"
          strokeDasharray={`${tramo} ${circ}`} strokeLinecap="round"
          transform="rotate(-90 45 45)"
          style={{ transition: 'stroke-dasharray 0.8s ease' }} />
        <text x="45" y="50" textAnchor="middle" fontSize="20" fontWeight="700" fill={color}
          fontFamily="Arial, sans-serif">{puntuacion}</text>
      </svg>
      <span className="text-xs text-gray-400 mt-0.5">/ 100</span>
    </div>
  )
}

export default function Predictor() {
  const [spots, setSpots]         = useState([])
  const [especies, setEspecies]   = useState([])
  const [especieId, setEspecieId] = useState('')
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading]     = useState(false)
  const [modoLibre, setModoLibre] = useState(false)
  const [spotId, setSpotId]       = useState('')
  const [puntoLibre, setPuntoLibre] = useState(null)

  useEffect(() => {
    getSpots().then(res => setSpots(res.results || res))
    getEspecies().then(res => setEspecies(res.results || res))
  }, [])

  const handleMapClick = (lat, lon) => {
    setPuntoLibre({ lat, lon })
    setSpotId('')
    setModoLibre(true)
    setResultado(null)
  }

  const handleSpotClick = (id) => {
    setSpotId(id)
    setPuntoLibre(null)
    setModoLibre(false)
    setResultado(null)
  }

  const handlePrediccion = async () => {
    if (!especieId || (!spotId && !puntoLibre)) return
    setLoading(true)
    try {
      const data = modoLibre && puntoLibre
        ? await getPrediccion(null, especieId, puntoLibre.lat, puntoLibre.lon)
        : await getPrediccion(spotId, especieId)
      setResultado(data)
    } catch (error) {
      console.error("Error al obtener la predicción:", error)
    } finally {
      setLoading(false)
    }
  }

  const spotSeleccionado  = spots.find(s => s.id === spotId)
  const ubicacionActiva   = modoLibre && puntoLibre
    ? `${puntoLibre.lat.toFixed(4)}, ${puntoLibre.lon.toFixed(4)}`
    : spotSeleccionado?.nombre || null

  const puedeConsultar = especieId && (spotId || puntoLibre)

  return (
    /* 🔥 CAMBIO: Quitamos px y py; dejamos solo pt-6 (Padding Top) */
    <div className="max-w-6xl mx-auto pt-6">
      
      {/* 🔥 CAMBIO: Ajustamos la altura exacta restando 144px de la pantalla */}
      <div className="flex h-[calc(100vh-144px)] gap-0 rounded-t-2xl overflow-hidden shadow-xl border-t border-x border-gray-200">

        {/* MAPA */}
        <div className="flex-1 relative">
          <MapContainer
            center={[42.43, -8.86]} zoom={10}
            style={{ height: '100%', width: '100%' }}
          >
            <ClickHandler onMapClick={handleMapClick} />

            <LayersControl position="topright">
              <LayersControl.BaseLayer checked name="Satélite">
                <TileLayer
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                  attribution="&copy; Esri"
                />
              </LayersControl.BaseLayer>
              <LayersControl.BaseLayer name="Mapa">
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              </LayersControl.BaseLayer>
              <LayersControl.Overlay checked name="Batimetría">
                <TileLayer
                  url="https://tiles.emodnet-bathymetry.eu/osm_tiles_marine/{z}/{x}/{y}.png"
                  opacity={0.6} attribution="&copy; EMODnet"
                />
              </LayersControl.Overlay>
              <LayersControl.Overlay name="Náutica">
                <TileLayer url="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png" />
              </LayersControl.Overlay>
            </LayersControl>

            {spots.map(s => (
              <Marker
                key={s.id}
                position={[s.latitud, s.longitud]}
                eventHandlers={{ click: () => handleSpotClick(s.id) }}
              >
                <Popup>
                  <p className="font-semibold text-sm">{s.nombre}</p>
                  <p className="text-xs text-gray-500">Pulsa para seleccionar</p>
                </Popup>
              </Marker>
            ))}

            {puntoLibre && (
              <Marker position={[puntoLibre.lat, puntoLibre.lon]} icon={IconoRojo}>
                <Popup>
                  <p className="font-semibold text-sm">Punto personalizado</p>
                  <p className="text-xs font-mono text-gray-500">
                    {puntoLibre.lat.toFixed(5)}, {puntoLibre.lon.toFixed(5)}
                  </p>
                </Popup>
              </Marker>
            )}
          </MapContainer>

          <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm text-xs text-gray-500 px-3 py-1.5 rounded-lg shadow pointer-events-none">
            Selecciona un punto del mapa o haz clic en cualquier lugar
          </div>
        </div>

        {/* PANEL DERECHO */}
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col overflow-y-auto">

          {/* Cabecera del panel */}
          <div className="px-6 py-5 border-b border-gray-100">
            <h1 className="text-base font-bold text-blue-900 tracking-tight">Predictor</h1>
            <p className="text-xs text-gray-400 mt-0.5">Condiciones en tiempo real</p>
          </div>

          {/* Configuración */}
          <div className="px-6 py-5 space-y-4 border-b border-gray-100">

            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Ubicación</p>
              <div className={`text-sm px-3 py-2.5 rounded-lg border font-medium min-h-[40px] ${
                modoLibre
                  ? 'bg-red-50 text-red-700 border-red-200'
                  : ubicacionActiva
                    ? 'bg-blue-50 text-blue-900 border-blue-100'
                    : 'bg-gray-50 text-gray-400 border-gray-200'
              }`}>
                {ubicacionActiva || 'Sin seleccionar'}
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Especie</p>
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-200 bg-white"
                value={especieId}
                onChange={e => setEspecieId(e.target.value)}
              >
                <option value="">Selecciona una especie</option>
                {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
              </select>
            </div>

            <button
              onClick={handlePrediccion}
              disabled={!puedeConsultar || loading}
              className="w-full bg-blue-700 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-900 disabled:opacity-40 transition-all"
            >
              {loading ? 'Calculando...' : 'Ver predicción'}
            </button>
          </div>

          {/* Resultado */}
          {resultado && (
            <div className="px-6 py-5 space-y-5">

              {/* Score + resumen */}
              <div className="flex items-center gap-4">
                <ScoreRing puntuacion={resultado.puntuacion} />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-800 leading-snug">
                    {resultado.resumen}
                  </p>
                  {resultado.luna && (
                    <p className="text-xs text-gray-400 mt-1">
                      {resultado.luna.nombre}
                    </p>
                  )}
                  {resultado.mareas && (
                    <p className="text-xs text-gray-400">
                      {resultado.mareas.estado}
                    </p>
                  )}
                </div>
              </div>

              <div className="border-t border-gray-100" />

              {/* Desglose */}
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                  Desglose
                </p>
                {resultado.desglose && (
                  <div className="bg-gray-50 p-4 rounded-xl space-y-1">
                    {Object.entries(resultado.desglose).map(([nombre, datos]) => (
                      <BarraFactor
                        key={nombre}
                        nombre={nombre}
                        puntos={datos.puntos}
                        max={datos.max}
                        nota={datos.nota}
                      />
                    ))}
                  </div>
                )}
                
                {/* Condiciones raw */}
                {resultado.condiciones && (
                  <>
                    <div className="border-t border-gray-100 my-4" />
                    <div>
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                        Condiciones actuales
                      </p>
                      <div className="grid grid-cols-2 gap-2">
                        {[
                          ['Agua', `${resultado.condiciones.temperatura_agua?.toFixed(1) ?? '—'} °C`],
                          ['Viento', `${resultado.condiciones.velocidad_viento?.toFixed(0) ?? '—'} km/h`],
                          ['Olas', `${resultado.condiciones.altura_olas?.toFixed(1) ?? '—'} m`],
                          ['Aire', `${resultado.condiciones.temperatura_aire?.toFixed(1) ?? '—'} °C`],
                        ].map(([lbl, val]) => (
                          <div key={lbl} className="bg-gray-50 rounded-lg px-3 py-2">
                            <p className="text-xs text-gray-400">{lbl}</p>
                            <p className="text-sm font-semibold text-gray-700 tabular-nums">{val}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div> 
            </div>
          )}
        </div>
      </div>
    </div>
  )
}