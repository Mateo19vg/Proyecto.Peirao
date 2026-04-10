import axios from 'axios'

// Con el proxy de Vite, usamos rutas relativas.
// En producción cambia esto por la URL real del backend.
const api = axios.create({
  baseURL: '/api',
})

// --- Especies ---
export const getEspecies = () => api.get('/especies/').then(r => r.data)
export const createEspecie = (data) => api.post('/especies/', data).then(r => r.data)

// --- Spots ---
export const getSpots = () => api.get('/spots/').then(r => r.data)
export const createSpot = (data) => api.post('/spots/', data).then(r => r.data)

// --- Capturas ---
export const getCapturas = (filters = {}) =>
  api.get('/capturas/', { params: filters }).then(r => r.data)
  // r.data tendrá: { count, next, previous, results: [...] }

export const createCaptura = (data) => {
  // Si hay foto, enviamos multipart/form-data; si no, JSON normal
  if (data.foto instanceof File) {
    const formData = new FormData()
    Object.entries(data).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) formData.append(k, v)
    })
    return api.post('/capturas/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data)
  }
  return api.post('/capturas/', data).then(r => r.data)
}

export const deleteCaptura = (id) => api.delete(`/capturas/${id}/`).then(r => r.data)

// --- Predicción ---
export const getPrediccion = (spotId, especieId) =>
  api.get('/prediccion/', { params: { spot_id: spotId, especie_id: especieId } })
    .then(r => r.data)
