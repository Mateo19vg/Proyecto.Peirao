import React from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents, LayersControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Iconas (Mantemos as túas)
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
let DefaultIcon = L.icon({ iconUrl: markerIcon, shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41] })
L.Marker.prototype.options.icon = DefaultIcon

function ClickHandler({ onClick }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

export default function MapPicker({ lat, lng, onChange }) {
  // Centro en Sanxenxo
  const center = [42.400, -8.810]

  return (
    /* IMPORTANTE: O height ten que estar aquí ou non se verá nada */
    <div style={{ height: '400px', width: '100%', position: 'relative', zIndex: 1 }}>
      <MapContainer 
        center={center} 
        zoom={12} 
        style={{ height: '100%', width: '100%' }}
      >
        <LayersControl position="topright">
          
          <LayersControl.BaseLayer checked name="Mapa Satélite">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Mapa Callejero">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="Batimetría (Profundidade)">
            <TileLayer
              url="https://tiles.emodnet-bathymetry.eu/osm_tiles_marine/{z}/{x}/{y}.png"
              opacity={0.6}
            />
          </LayersControl.Overlay>

        </LayersControl>

        <ClickHandler onClick={onChange} />
        {lat && lng && <Marker position={[lat, lng]} />}
      </MapContainer>
    </div>
  )
}   