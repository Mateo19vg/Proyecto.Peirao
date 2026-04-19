import React, { useState, useEffect } from 'react'
import { getSpots, getEspecies, getPrediccion } from '../services/api'
import { MapContainer, TileLayer, Marker, Popup, LayersControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix para as iconas de Leaflet
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})
L.Marker.prototype.options.icon = DefaultIcon

export default function Predictor() {
  const [spots, setSpots] = useState([])
  const [especies, setEspecies] = useState([])
  const [spotId, setSpotId] = useState('')
  const [especieId, setEspecieId] = useState('')
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading] = useState(false)

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

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-blue-900 mb-6 flex items-center gap-2">
        ⚓ O Peirao Pro <span className="text-sm bg-blue-100 px-2 py-1 rounded text-blue-600">MODO NÁUTICO</span>
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MAPA TECNICO (Ocupa 2 columnas) */}
        <div className="lg:col-span-2 bg-white p-2 rounded-3xl shadow-2xl border border-blue-100">
          <div className="h-[550px] rounded-2xl overflow-hidden relative">
            <MapContainer center={[42.43, -8.86]} zoom={10} style={{height: '100%', width: '100%'}}>
              
              <LayersControl position="topright">
                {/* CAPA SATÉLITE - Para ver as pedras e o fondo real */}
                <LayersControl.BaseLayer checked name="Visión Satélite">
                  <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='&copy; Esri'
                  />
                </LayersControl.BaseLayer>

                <LayersControl.BaseLayer name="Mapa de Estradas">
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                </LayersControl.BaseLayer>

                {/* CAPA DE PROFUNDIDADE (Batimetría) - O estilo Garmin */}
                <LayersControl.Overlay checked name="Relieve Submarino (Batimetría)">
                  <TileLayer
                    url="https://tiles.emodnet-bathymetry.eu/osm_tiles_marine/{z}/{x}/{y}.png"
                    opacity={0.7}
                    attribution='&copy; EMODnet'
                  />
                </LayersControl.Overlay>

                {/* CAPA NÁUTICA - Faros e Boias */}
                <LayersControl.Overlay name="Cartografía Náutica (Sinais)">
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
                      <p className="text-xs text-gray-500">Preme para seleccionar</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>

        {/* PANEL DE CONTROL */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-lg border border-blue-50">
            <h2 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">Configuración</h2>
            
            <label className="block text-sm font-bold text-blue-900 mb-2">Zona Seleccionada:</label>
            <div className="p-3 bg-blue-50 text-blue-800 rounded-xl font-bold border border-blue-100 mb-4 min-h-[48px]">
              {spotId ? spots.find(s => s.id === spotId)?.nombre : "Preme no mapa 📍"}
            </div>

            <label className="block text-sm font-bold text-blue-900 mb-2">Especie:</label>
            <select 
              className="w-full border-2 border-gray-100 rounded-xl p-3 mb-6 outline-none focus:border-blue-500"
              value={especieId}
              onChange={e => setEspecieId(e.target.value)}
            >
              <option value="">¿Que imos buscar?</option>
              {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
            </select>

            <button 
              onClick={handlePrediccion}
              disabled={!spotId || !especieId || loading}
              className="w-full bg-blue-600 text-white py-4 rounded-2xl font-black shadow-xl hover:bg-blue-800 disabled:opacity-40 transition-all active:scale-95"
            >
              {loading ? 'CALCULANDO...' : '🎣 VER PREDICIÓN'}
            </button>
          </div>

          {resultado && (
            <div className="bg-gradient-to-br from-blue-600 to-blue-900 p-6 rounded-3xl shadow-2xl text-white animate-in fade-in zoom-in duration-300">
              <div className="flex justify-between items-center mb-2">
                <span className="text-4xl font-black">{resultado.puntuacion}%</span>
                <span className="text-xs uppercase font-bold tracking-tighter opacity-70">Probabilidade</span>
              </div>
              <p className="text-lg leading-tight font-medium">"{resultado.resumen}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}