import React, { useState, useEffect } from 'react'
import { getSpots, getEspecies, getPrediccion } from '../services/api'
import { MapContainer, TileLayer, Marker, Popup, LayersControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})
L.Marker.prototype.options.icon = DefaultIcon

// Etiquetas legibles para cada factor del desglose
const FACTOR_LABELS = {
  temperatura_agua: { label: 'Temperatura agua', emoji: '🌡️' },
  viento:           { label: 'Viento',            emoji: '💨' },
  estado_mar:       { label: 'Estado del mar',    emoji: '🌊' },
  claridad_agua:    { label: 'Claridad',          emoji: '💧' },
  luna:             { label: 'Fase lunar',        emoji: '🌙' },
  mareas:           { label: 'Mareas',            emoji: '🔄' },
}

function BaraFactor({ nombre, puntos, max, nota }) {
  const pct = Math.round((puntos / max) * 100)
  const color =
    pct >= 75 ? 'bg-emerald-500' :
    pct >= 50 ? 'bg-sky-500' :
    pct >= 30 ? 'bg-amber-400' :
                'bg-red-400'

  const { label, emoji } = FACTOR_LABELS[nombre] || { label: nombre, emoji: '•' }

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-semibold text-gray-600">
          {emoji} {label}
        </span>
        <span className="text-xs font-bold text-gray-500">
          {puntos}/{max}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {nota && (
        <p className="text-xs text-gray-400 mt-0.5 italic">{nota}</p>
      )}
    </div>
  )
}

function ScoreRing({ puntuacion }) {
  const color =
    puntuacion >= 80 ? '#10b981' :
    puntuacion >= 65 ? '#0ea5e9' :
    puntuacion >= 50 ? '#f59e0b' :
    puntuacion >= 35 ? '#f97316' :
                       '#ef4444'

  const r = 36
  const circunferencia = 2 * Math.PI * r
  const tramo = (puntuacion / 100) * circunferencia

  return (
    <div className="flex flex-col items-center">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle
          cx="45" cy="45" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${tramo} ${circunferencia}`}
          strokeLinecap="round"
          transform="rotate(-90 45 45)"
          style={{ transition: 'stroke-dasharray 0.8s ease' }}
        />
        <text x="45" y="49" textAnchor="middle" fontSize="18" fontWeight="bold" fill={color}>
          {puntuacion}
        </text>
      </svg>
      <span className="text-xs text-gray-400 font-medium mt-1">/ 100</span>
    </div>
  )
}

export default function Predictor() {
  const [spots, setSpots]       = useState([])
  const [especies, setEspecies] = useState([])
  const [spotId, setSpotId]     = useState('')
  const [especieId, setEspecieId] = useState('')
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading]   = useState(false)

  useEffect(() => {
    getSpots().then(res => setSpots(res.results || res))
    getEspecies().then(res => setEspecies(res.results || res))
  }, [])

  const handlePrediccion = async () => {
    if (!spotId || !especieId) return
    setLoading(true)
    try {
      const data = await getPrediccion(spotId, especieId)
      setResultado(data)
    } finally {
      setLoading(false)
    }
  }

  const spotSeleccionado = spots.find(s => s.id === spotId)

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-blue-900 mb-6 flex items-center gap-2">
        ⚓ O Peirao Pro
        <span className="text-sm bg-blue-100 px-2 py-1 rounded text-blue-600">MODO NÁUTICO</span>
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* MAPA */}
        <div className="lg:col-span-2 bg-white p-2 rounded-3xl shadow-2xl border border-blue-100">
          <div className="h-[500px] rounded-2xl overflow-hidden">
            <MapContainer center={[42.43, -8.86]} zoom={10} style={{ height: '100%', width: '100%' }}>
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
                    opacity={0.7}
                    attribution="&copy; EMODnet"
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
                  eventHandlers={{ click: () => setSpotId(s.id) }}
                >
                  <Popup>
                    <div className="text-center">
                      <p className="font-bold text-blue-900">{s.nombre}</p>
                      <p className="text-xs text-gray-500">Pulsa para seleccionar</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>

        {/* PANEL DERECHO */}
        <div className="space-y-4">

          {/* Configuración */}
          <div className="bg-white p-5 rounded-3xl shadow-lg border border-blue-50">
            <h2 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">Configuración</h2>

            <label className="block text-sm font-bold text-blue-900 mb-1">Zona:</label>
            <div className="p-3 bg-blue-50 text-blue-800 rounded-xl font-bold border border-blue-100 mb-4 min-h-[44px] text-sm">
              {spotSeleccionado ? spotSeleccionado.nombre : 'Pulsa un punto en el mapa 📍'}
            </div>

            <label className="block text-sm font-bold text-blue-900 mb-1">Especie:</label>
            <select
              className="w-full border-2 border-gray-100 rounded-xl p-3 mb-5 outline-none focus:border-blue-500 text-sm"
              value={especieId}
              onChange={e => setEspecieId(e.target.value)}
            >
              <option value="">¿Qué buscamos?</option>
              {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
            </select>

            <button
              onClick={handlePrediccion}
              disabled={!spotId || !especieId || loading}
              className="w-full bg-blue-600 text-white py-4 rounded-2xl font-black shadow-xl hover:bg-blue-800 disabled:opacity-40 transition-all active:scale-95"
            >
              {loading ? 'CALCULANDO...' : '🎣 VER PREDICCIÓN'}
            </button>
          </div>

          {/* Resultado */}
          {resultado && (
            <div className="bg-white rounded-3xl shadow-lg border border-blue-50 overflow-hidden">

              {/* Cabecera con score */}
              <div className="bg-gradient-to-br from-blue-700 to-blue-900 p-5">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium leading-snug opacity-90">
                      {resultado.resumen}
                    </p>
                    {resultado.mareas && (
                      <p className="text-blue-200 text-xs mt-1">
                        🔄 {resultado.mareas.momento}
                      </p>
                    )}
                    {resultado.luna && (
                      <p className="text-blue-200 text-xs mt-0.5">
                        {resultado.luna.emoji} {resultado.luna.nombre}
                      </p>
                    )}
                  </div>
                  <ScoreRing puntuacion={resultado.puntuacion} />
                </div>
              </div>

              {/* Desglose por factor */}
              {resultado.desglose && (
                <div className="p-5">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
                    Desglose de factores
                  </h3>
                  {Object.entries(resultado.desglose).map(([nombre, datos]) => (
                    <BaraFactor
                      key={nombre}
                      nombre={nombre}
                      puntos={datos.puntos}
                      max={datos.max}
                      nota={datos.nota}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}