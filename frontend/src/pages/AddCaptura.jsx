import React, { useState, useEffect } from "react"
import { useNavigate } from 'react-router-dom'
import { createCaptura, getEspecies, getSpots } from '../services/api'
import MapPicker from '../components/MapPicker'

export default function AddCaptura() {
  const [form, setForm] = useState({ especie: '', spot: '', fecha: '', hora: '', peso_kg: '', longitud_cm: '', notas: '', foto: null })
  const [especies, setEspecies] = useState([])
  const [spots, setSpots] = useState([])
  const [coords, setCoords] = useState({ lat: null, lng: null })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getEspecies().then(res => setEspecies(res.results || res)).catch(() => setError("Erro ao cargar especies."))
    getSpots().then(res => setSpots(res.results || res)).catch(() => setError("Erro ao cargar spots."))
  }, [])

  const handleChange = e => {
    const { name, value } = e.target
    setForm(p => ({ ...p, [name]: value }))
    if (name === 'spot') {
      const s = spots.find(x => x.id === parseInt(value))
      if (s) setCoords({ lat: s.latitud, lng: s.longitud })
    }
  }

  const handleSubmit = async () => {
    if (!form.especie || !form.spot || !form.fecha || !form.hora) {
      setError('Cubre os campos obrigatorios (*)')
      return
    }
    setLoading(true)
    try {
      await createCaptura(form)
      navigate('/log')
    } catch (err) {
      setError('Erro ao gardar a captura.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-blue-900 mb-6">➕ Nova Captura</h1>
      <div className="bg-white rounded-2xl shadow-lg p-6 space-y-6 border border-blue-50">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Peixe *">
            <select name="especie" value={form.especie} onChange={handleChange} className="border-2 p-3 rounded-xl outline-none focus:border-blue-500">
              <option value="">Selecciona...</option>
              {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
            </select>
          </Field>
          <Field label="Zona *">
            <select name="spot" value={form.spot} onChange={handleChange} className="border-2 p-3 rounded-xl outline-none focus:border-blue-500">
              <option value="">Selecciona...</option>
              {spots.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          </Field>
        </div>

        <Field label="Ubicación na costa">
          <MapPicker lat={coords.lat} lng={coords.lng} onChange={(lat, lng) => setCoords({ lat, lng })} />
        </Field>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Data *"><input type="date" name="fecha" onChange={handleChange} className="border-2 p-3 rounded-xl"/></Field>
          <Field label="Hora *"><input type="time" name="hora" onChange={handleChange} className="border-2 p-3 rounded-xl"/></Field>
        </div>

        <button onClick={handleSubmit} disabled={loading} className="w-full bg-blue-600 text-white py-4 rounded-xl font-bold hover:bg-blue-800 disabled:opacity-50 transition-all">
          {loading ? 'Gardando...' : '💾 Gardar captura'}
        </button>
        {error && <p className="text-red-500 text-center font-medium">{error}</p>}
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div className="flex flex-col">
      <label className="text-xs font-bold text-gray-400 mb-2 uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}