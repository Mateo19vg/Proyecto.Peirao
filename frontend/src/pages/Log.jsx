import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getCapturas, deleteCaptura, getEspecies, getSpots } from '../services/api'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
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

export default function Log() {
  // Mantener el estado estructurado
  const [data, setData] = useState({ count: 0, next: null, previous: null, results: [] })
  const [especies, setEspecies] = useState([])
  const [spots, setSpots] = useState([])

  const [filtroEspecie, setFiltroEspecie] = useState('')
  const [filtroSpot, setFiltroSpot] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [soloMias, setSoloMias] = useState(false)
  const [pagina, setPagina] = useState(1)

  useEffect(() => {
    getEspecies().then(res => setEspecies(res.results || res || []))
    getSpots().then(res => setSpots(res.results || res || []))
  }, [])

  const cargar = useCallback(() => {
    const filters = { page: pagina }
    if (filtroEspecie) filters.especie = filtroEspecie
    if (filtroSpot) filters.spot = filtroSpot
    if (busqueda) filters.search = busqueda
    if (soloMias) filters.mias = 1
    
    getCapturas(filters).then(res => {
      // Asegurarse de que data siempre tenga la propiedad 'results'
      if (Array.isArray(res)) {
        setData({ count: res.length, next: null, previous: null, results: res })
      } else if (res && res.results) {
        setData(res)
      } else {
        setData({ count: 0, next: null, previous: null, results: [] })
      }
    }).catch(err => {
      console.error("Error cargando capturas:", err)
    })
  }, [filtroEspecie, filtroSpot, busqueda, soloMias, pagina])

  useEffect(() => { cargar() }, [cargar])

  const handleFiltro = (setter) => (e) => {
    setter(e.target.value)
    setPagina(1)
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Seguro que queres borrar esta captura do teu diario?')) return
    await deleteCaptura(id)
    cargar()
    // Refresca la lista de spots para que desaparezcan los puntos libres borrados
    getSpots().then(res => setSpots(res.results || res || []))
  }

  // Asegura que listado sea siempre un array para evitar errores de .length o .map
  const listaCapturas = data?.results || []
  const totalPaginas = Math.ceil((data?.count || 0) / 10)

  return (
    <div className="max-w-5xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-blue-900 mb-6">Capturas dos pescadores</h1>

      {/* 1. Mapa de Actividad */}
      <div className="bg-white rounded-3xl shadow-lg border border-blue-50 p-4 mb-8">
        <h2 className="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider ml-1">Mapa de capturas en Galicia</h2>
        <div className="h-80 rounded-2xl overflow-hidden shadow-inner">
          <MapContainer center={[42.755, -7.863]} zoom={7} style={{height: '100%', width: '100%'}}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {listaCapturas.map(c => {
              //Busca dónde vienen los datos lat/lon de forma flexible
              const lat = parseFloat(c.spot_latitud || c.latitud || c.spot?.latitud)
              const lon = parseFloat(c.spot_longitud || c.longitud || c.spot?.longitud)

              // Si no son números válidos, ignora el marcador en vez de romper la app
              if (isNaN(lat) || isNaN(lon)) return null

              return (
                <Marker key={c.id} position={[lat, lon]}>
                  <Popup>
                    <div className="text-center p-1">
                      <p className="font-bold text-blue-900 border-b border-blue-100 mb-1">{c.especie_nombre || c.especie?.nombre || 'Peixe'}</p>
                      <p className="text-xs text-gray-600">{c.spot_nombre || c.spot?.nombre || 'Zona desconocida'}</p>
                      <p className="text-xs font-mono">{c.fecha}</p>
                      <p className="text-xs text-blue-500 font-semibold mt-1">🎣 {c.pescador_nombre}</p>
                    </div>
                  </Popup>
                </Marker>
              )
            })}
          </MapContainer>
        </div>
      </div>

      {/* Buscador y Filtros */}
      <div className="bg-white rounded-2xl shadow-md border border-blue-50 p-6 mb-8 space-y-4">
        <input
          type="text"
          placeholder="Buscar nas túas notas..."
          value={busqueda}
          onChange={handleFiltro(setBusqueda)}
          className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 focus:border-blue-500 outline-none transition-all"
        />
        <div className="flex flex-col sm:flex-row gap-4">
          <select 
            className="border-2 border-gray-100 rounded-xl p-3 flex-1 outline-none focus:border-blue-500" 
            value={filtroEspecie} 
            onChange={handleFiltro(setFiltroEspecie)}
          >
            <option value="">Tódolos peixes</option>
            {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
          </select>
          <select 
            className="border-2 border-gray-100 rounded-xl p-3 flex-1 outline-none focus:border-blue-500" 
            value={filtroSpot} 
            onChange={handleFiltro(setFiltroSpot)}
          >
            <option value="">Tódalas zonas</option>
            {spots.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
          <label className="flex items-center gap-2 border-2 border-gray-100 rounded-xl p-3 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={soloMias}
              onChange={e => { setSoloMias(e.target.checked); setPagina(1) }}
              className="accent-blue-600"
            />
            <span className="text-sm font-medium text-gray-600">Só as miñas</span>
          </label>
        </div>
      </div>

      {/* Listaxe de resultados */}
      {listaCapturas.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-3xl border-2 border-dashed border-gray-100">
          <p className="text-gray-400 italic">Non hai capturas rexistradas con estes criterios.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {listaCapturas.map(c => (
            <div key={c.id} className="bg-white rounded-2xl shadow-sm border border-blue-50 p-5 flex justify-between items-center gap-4 hover:shadow-md transition-shadow">
              <div className="flex-1">
                <div className="font-bold text-blue-900 text-lg">{c.especie_nombre || c.especie?.nombre || 'Peixe'}</div>
                <div className="text-sm text-gray-500 font-medium"> 
                  {c.spot_nombre || c.spot?.nombre || 'Zona personalizada'} · {c.fecha}
                </div>
                <Link
                  to={c.usuario ? `/perfil/${c.usuario}` : '#'}
                  className="text-xs text-blue-600 hover:underline font-semibold inline-block mt-1"
                >
                  🎣 {c.pescador_nombre}
                </Link>
                <div className="flex gap-4 mt-2">
                  {c.peso_kg && <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-md font-bold italic">Peso: {c.peso_kg} kg</span>}
                  {c.longitud_cm && <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-md font-bold italic">Medida: {c.longitud_cm} cm</span>}
                </div>
                {c.notas && <div className="text-sm text-gray-400 mt-3 italic border-l-2 border-blue-100 pl-3">"{c.notas}"</div>}
              </div>
              
              {c.foto_url && (
                <img
                  src={c.foto_url}
                  alt="captura"
                  className="w-24 h-24 object-cover rounded-2xl cursor-pointer ring-2 ring-transparent hover:ring-blue-300 transition-all"
                  onClick={() => window.open(c.foto_url, '_blank')}
                />
              )}
              
              {c.es_propia && (
                <button onClick={() => handleDelete(c.id)} className="p-2 text-gray-300 hover:text-red-500 transition-colors">Eliminar</button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Paxinación */}
      {totalPaginas > 1 && (
        <div className="flex items-center justify-center gap-4 mt-12">
          <button 
            disabled={pagina === 1} 
            onClick={() => setPagina(p => p - 1)} 
            className="px-6 py-2 rounded-xl border-2 border-gray-100 text-sm font-bold disabled:opacity-20 hover:bg-blue-50"
          >
            ← Anterior
          </button>
          <span className="text-sm font-bold text-blue-900 bg-blue-50 px-4 py-2 rounded-lg">{pagina} / {totalPaginas}</span>
          <button 
            disabled={pagina === totalPaginas} 
            onClick={() => setPagina(p => p + 1)} 
            className="px-6 py-2 rounded-xl border-2 border-gray-100 text-sm font-bold disabled:opacity-20 hover:bg-blue-50"
          >
            Seguinte →
          </button>
        </div>
      )}
    </div>
  )
}