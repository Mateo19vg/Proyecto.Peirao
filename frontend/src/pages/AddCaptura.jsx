import React from "react"
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCaptura, getEspecies, getSpots } from '../services/api'

const initialForm = {
  especie: '', spot: '', fecha: '', hora: '',
  peso_kg: '', longitud_cm: '', notas: '', foto: null,
}

export default function AddCaptura() {
  const [form, setForm] = useState(initialForm)
  const [especies, setEspecies] = useState([])
  const [spots, setSpots] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getEspecies().then(setEspecies)
    getSpots().then(setSpots)
  }, [])

  const [fotoPreview, setFotoPreview] = useState(null)

  const handleChange = e => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleFoto = e => {
    const file = e.target.files[0]
    if (!file) return
    setForm(prev => ({ ...prev, foto: file }))
    setFotoPreview(URL.createObjectURL(file))  // preview local antes de subir
  }

  const handleSubmit = async () => {
    if (!form.especie || !form.spot || !form.fecha || !form.hora) {
      setError('Especie, spot, fecha y hora son obligatorios.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await createCaptura(form)
      navigate('/log')  // redirige al log tras guardar
    } catch {
      setError('Error al guardar. Revisa los datos e inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-ocean-900 mb-6">➕ Registrar Captura</h1>

      <div className="bg-white rounded-2xl shadow-md p-6 space-y-4">

        {/* Especie y Spot */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Especie *">
            <select name="especie" value={form.especie} onChange={handleChange} className="input">
              <option value="">Selecciona...</option>
              {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
            </select>
          </Field>
          <Field label="Spot *">
            <select name="spot" value={form.spot} onChange={handleChange} className="input">
              <option value="">Selecciona...</option>
              {spots.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          </Field>
        </div>

        {/* Fecha y Hora */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Fecha *">
            <input type="date" name="fecha" value={form.fecha} onChange={handleChange} className="input" />
          </Field>
          <Field label="Hora *">
            <input type="time" name="hora" value={form.hora} onChange={handleChange} className="input" />
          </Field>
        </div>

        {/* Peso y Longitud */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Peso (kg)">
            <input type="number" step="0.1" name="peso_kg" value={form.peso_kg} onChange={handleChange} className="input" placeholder="0.0" />
          </Field>
          <Field label="Longitud (cm)">
            <input type="number" step="0.5" name="longitud_cm" value={form.longitud_cm} onChange={handleChange} className="input" placeholder="0" />
          </Field>
        </div>

        {/* Notas */}
        <Field label="Notas">
          <textarea
            name="notas"
            value={form.notas}
            onChange={handleChange}
            rows={3}
            className="input resize-none"
            placeholder="Condiciones, cebo usado, observaciones..."
          />
        </Field>

        {/* Foto */}
        <Field label="Foto (opcional)">
          <input
            type="file"
            accept="image/*"
            onChange={handleFoto}
            className="w-full text-sm text-gray-500 file:mr-3 file:py-1 file:px-3 file:rounded-lg file:border-0 file:bg-ocean-50 file:text-ocean-700 hover:file:bg-ocean-100 cursor-pointer"
          />
          {fotoPreview && (
            <img
              src={fotoPreview}
              alt="Preview"
              className="mt-3 rounded-xl max-h-48 object-cover w-full"
            />
          )}
        </Field>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-ocean-700 text-white py-2 rounded-lg font-medium hover:bg-ocean-900 disabled:opacity-40 transition-colors"
        >
          {loading ? 'Guardando...' : '💾 Guardar captura'}
        </button>
      </div>
    </div>
  )
}

// Wrapper para label + campo
function Field({ label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {children}
    </div>
  )
}
