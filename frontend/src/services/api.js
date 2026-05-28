import axios from 'axios'

const API = axios.create({ baseURL: '/api' })

export const getEspecies   = ()       => API.get('/especies/').then(r => r.data)
export const getSpots      = ()       => API.get('/spots/').then(r => r.data)

export const getCapturas   = (params) => API.get('/capturas/', { params }).then(r => r.data)
export const createCaptura = (form)   => {
  const data = new FormData()
  Object.entries(form).forEach(([k, v]) => { if (v !== null && v !== '') data.append(k, v) })
  return API.post('/capturas/', data, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const deleteCaptura = (id)     => API.delete(`/capturas/${id}/`)

/**
 * getPrediccion — dos modos:
 *   Spot guardado:  getPrediccion(spotId, especieId)
 *   Punto libre:    getPrediccion(null, especieId, lat, lon)
 */
export const getPrediccion = (spotId, especieId, lat = null, lon = null) => {
  const params = { especie_id: especieId }
  if (spotId) {
    params.spot_id = spotId
  } else if (lat !== null && lon !== null) {
    params.lat = lat
    params.lon = lon
  }
  return API.get('/prediccion/', { params }).then(r => r.data)
}