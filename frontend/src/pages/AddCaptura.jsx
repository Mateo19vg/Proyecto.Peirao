import React, { useState, useEffect } from "react"
import { useNavigate } from 'react-router-dom'
import { createCaptura, createSpot, getEspecies, getSpots } from '../services/api'
import { MapContainer, TileLayer, Marker, Popup, LayersControl, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

L.Marker.prototype.options.icon = L.icon({
  iconUrl: markerIcon, shadowUrl: markerShadow,
  iconSize: [25, 41], iconAnchor: [12, 41],
})

const IconoRojo = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41],
})

const IconoVerde = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41],
})

const ZONAS_GALICIA = [
  { nombre: "A Guarda",   lat: 41.900, lon: -8.870 },
  { nombre: "Baiona",     lat: 42.120, lon: -8.840 },
  { nombre: "Vigo",       lat: 42.230, lon: -8.720 },
  { nombre: "Cangas",     lat: 42.260, lon: -8.780 },
  { nombre: "Bueu",       lat: 42.320, lon: -8.780 },
  { nombre: "Marín",      lat: 42.390, lon: -8.700 },
  { nombre: "Pontevedra", lat: 42.430, lon: -8.640 },
  { nombre: "Sanxenxo",  lat: 42.400, lon: -8.810 },
  { nombre: "O Grove",    lat: 42.480, lon: -8.860 },
  { nombre: "Ribeira",    lat: 42.550, lon: -8.990 },
  { nombre: "Muros",      lat: 42.770, lon: -9.050 },
  { nombre: "Fisterra",   lat: 42.900, lon: -9.260 },
  { nombre: "Camariñas",  lat: 43.130, lon: -9.180 },
  { nombre: "Laxe",       lat: 43.210, lon: -9.000 },
  { nombre: "Malpica",    lat: 43.320, lon: -8.810 },
  { nombre: "A Coruña",   lat: 43.360, lon: -8.410 },
  { nombre: "Ferrol",     lat: 43.480, lon: -8.230 },
  { nombre: "Cedeira",    lat: 43.660, lon: -8.050 },
  { nombre: "Viveiro",    lat: 43.660, lon: -7.590 },
  { nombre: "Burela",     lat: 43.650, lon: -7.350 },
  { nombre: "Ribadeo",    lat: 43.530, lon: -7.030 },
]

const MODOS = [
  { id: 'spot',  label: 'Spot guardado' },
  { id: 'zona',  label: 'Zona de Galicia' },
  { id: 'libre', label: 'Punto libre' },
]

function ClickHandler({ activo, onClic }) {
  useMapEvents({ click(e) { if (activo) onClic(e.latlng.lat, e.latlng.lng) } })
  return null
}

function CentrarMapa({ lat, lon }) {
  const map = useMapEvents({})
  useEffect(() => { if (lat && lon) map.flyTo([lat, lon], 13, { duration: 1 }) }, [lat, lon])
  return null
}

function Field({ label, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

const inputCls = "border border-gray-200 p-2.5 rounded-lg text-sm outline-none focus:border-blue-400 bg-white"

export default function AddCaptura() {
  const [form, setForm] = useState({
    especie: '', fecha: '', hora: '',
    peso_kg: '', longitud_cm: '', notas: '', foto: null,
  })
  const [especies, setEspecies] = useState([])
  const [spots, setSpots]       = useState([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const navigate = useNavigate()

  const [modo, setModo]             = useState('spot')
  const [spotId, setSpotId]         = useState('')
  const [zonaIdx, setZonaIdx]       = useState('')
  const [puntoLibre, setPuntoLibre] = useState(null)

  // Funciones auxiliares para calcular el tiempo real local de Galicia
  const getFechaHoyStr = () => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const getHoraActualStr = () => {
    const d = new Date()
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  const hoyStr = getFechaHoyStr()
  const horaActualStr = getHoraActualStr()

  useEffect(() => {
    getEspecies().then(res => {
      let lista = res.results || res || []    
      setEspecies(lista)
    })
    
    getSpots().then(res => setSpots(res.results || res || []))
  }, [])

  const coordsActivas = () => {
    if (modo === 'spot' && spotId) {
      const s = spots.find(x => x.id === parseInt(spotId))
      return s ? { lat: s.latitud, lon: s.longitud } : null
    }
    if (modo === 'zona' && zonaIdx !== '') {
      const z = ZONAS_GALICIA[parseInt(zonaIdx)]
      return { lat: z.lat, lon: z.lon }
    }
    if (modo === 'libre' && puntoLibre) return puntoLibre
    return null
  }

  const coords = coordsActivas()

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }))

  const handleModo = m => {
    setModo(m); setSpotId(''); setZonaIdx(''); setPuntoLibre(null); setError(null)
  }

  const handleSubmit = async () => {
    if (!form.especie || !form.fecha || !form.hora) {
      setError('Rellena especie, fecha y hora.')
      return
    }
    if (!coords) { setError('Selecciona una ubicación.'); return }

    if (form.fecha > hoyStr || (form.fecha === hoyStr && form.hora > horaActualStr)) {
      setError('No puedes registrar una captura en el futuro.')
      return
    }

    setLoading(true); setError(null)
    try {
      let spotFinal = spotId

      if (modo === 'zona' || modo === 'libre') {
        const nombreSpot = modo === 'zona'
          ? `${ZONAS_GALICIA[parseInt(zonaIdx)].nombre} (zona)`
          : `Punto libre (${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)})`

        const nuevoSpot = await createSpot({
          nombre: nombreSpot, tipo: 'mar',
          latitud: coords.lat, longitud: coords.lon,
          descripcion: modo === 'libre' ? 'Punto personalizado' : 'Zona general',
          es_personalizado: true,
        })
        spotFinal = nuevoSpot.id
      }

      await createCaptura({ ...form, spot: spotFinal })
      navigate('/log')
    } catch (err) {
      setError('Error al guardar: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-ocean-900 mb-6">Nueva captura</h1>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col gap-5">

        {/* Especie */}
        <Field label="Especie *">
          <select name="especie" value={form.especie} onChange={handleChange} className={inputCls}>
            <option value="">Selecciona...</option>
            {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
          </select>
        </Field>

        {/* Selector de modo */}
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Tipo de ubicación *
          </p>
          <div className="flex gap-2">
            {MODOS.map(m => (
              <button key={m.id} onClick={() => handleModo(m.id)}
                className={`flex-1 py-2 rounded-lg text-xs font-semibold border transition-all ${
                  modo === m.id
                    ? 'bg-ocean-700 text-white border-ocean-700'
                    : 'bg-white text-gray-500 border-gray-200 hover:border-blue-300'
                }`}>
                {m.label}
              </button>
            ))}
          </div>
        </div>

        {/* Panel según modo */}
        {modo === 'spot' && (
          <Field label="Spot">
            <select value={spotId} onChange={e => setSpotId(e.target.value)} className={inputCls}>
              <option value="">Selecciona un spot...</option>
              {spots.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          </Field>
        )}

        {modo === 'zona' && (
          <Field label="Zona">
            <select value={zonaIdx} onChange={e => setZonaIdx(e.target.value)} className={inputCls}>
              <option value="">Selecciona una zona...</option>
              {ZONAS_GALICIA.map((z, i) => (
                <option key={i} value={i}>{z.nombre}</option>
              ))}
            </select>
          </Field>
        )}

        {modo === 'libre' && !puntoLibre && (
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-sm text-blue-700">
            Haz clic en el mapa para marcar el punto exacto.
          </div>
        )}

        {/* Mapa */}
        {(coords || modo === 'libre') && (
          <Field label={modo === 'libre' ? 'Haz clic para marcar' : 'Ubicación'}>
            <div style={{ height: 280, borderRadius: 12, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
              <MapContainer
                center={coords ? [coords.lat, coords.lon] : [42.43, -8.86]}
                zoom={coords ? 13 : 8}
                style={{ height: '100%', width: '100%' }}>
                <ClickHandler activo={modo === 'libre'} onClic={(lat, lon) => setPuntoLibre({ lat, lon })} />
                {coords && <CentrarMapa lat={coords.lat} lon={coords.lon} />}
                <LayersControl position="topright">
                  <LayersControl.BaseLayer checked name="Satélite">
                    <TileLayer
                      url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                      attribution="&copy; Esri" />
                  </LayersControl.BaseLayer>
                  <LayersControl.BaseLayer name="Mapa">
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  </LayersControl.BaseLayer>
                </LayersControl>

                {modo === 'spot' && coords && (
                  <Marker position={[coords.lat, coords.lon]}>
                    <Popup>{spots.find(s => s.id === parseInt(spotId))?.nombre}</Popup>
                  </Marker>
                )}
                {modo === 'zona' && coords && (
                  <Marker position={[coords.lat, coords.lon]} icon={IconoVerde}>
                    <Popup>{ZONAS_GALICIA[parseInt(zonaIdx)]?.nombre}</Popup>
                  </Marker>
                )}
                {modo === 'libre' && puntoLibre && (
                  <Marker position={[puntoLibre.lat, puntoLibre.lon]} icon={IconoRojo}>
                    <Popup>
                      <span className="font-mono text-xs">
                        {puntoLibre.lat.toFixed(5)}, {puntoLibre.lon.toFixed(5)}
                      </span>
                    </Popup>
                  </Marker>
                )}
              </MapContainer>
            </div>
            {coords && (
              <p className="text-xs text-gray-400 font-mono text-center mt-1">
                {coords.lat.toFixed(5)}, {coords.lon.toFixed(5)}
              </p>
            )}
          </Field>
        )}

        {/* Fecha y hora con limitadores MAX */}
        <div className="grid grid-cols-2 gap-4">
          <Field label="Fecha *">
            <input 
              type="date" 
              name="fecha" 
              max={hoyStr} 
              value={form.fecha}
              onChange={handleChange} 
              className={inputCls} 
            />
          </Field>
          <Field label="Hora *">
            <input 
              type="time" 
              name="hora" 
              max={form.fecha === hoyStr ? horaActualStr : undefined} 
              value={form.hora}
              onChange={handleChange} 
              className={inputCls} 
            />
          </Field>
        </div>

        {/* Opcionales */}
        <div className="grid grid-cols-2 gap-4">
          <Field label="Peso (kg)">
            <input type="number" name="peso_kg" step="0.1" value={form.peso_kg} onChange={handleChange} className={inputCls} />
          </Field>
          <Field label="Longitud (cm)">
            <input type="number" name="longitud_cm" step="0.5" value={form.longitud_cm} onChange={handleChange} className={inputCls} />
          </Field>
        </div>

        <Field label="Notas">
          <textarea name="notas" rows={3} value={form.notas} onChange={handleChange} className={`${inputCls} resize-none`}
            placeholder="Condiciones, cebo, técnica..." />
        </Field>

        <Field label="Foto">
          <input type="file" accept="image/*"
            onChange={e => setForm(p => ({ ...p, foto: e.target.files[0] || null }))}
            className={inputCls} />
        </Field>

        <button onClick={handleSubmit} disabled={loading}
          className="w-full bg-ocean-700 text-white py-3 rounded-lg text-sm font-semibold hover:bg-ocean-900 disabled:opacity-50 transition-all">
          {loading ? 'Guardando...' : 'Guardar captura'}
        </button>

        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
      </div>
    </div>
  )
}