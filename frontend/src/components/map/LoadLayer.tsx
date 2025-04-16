import { useMemo } from 'react'
import { CircleMarker, Tooltip } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'

const LoadLayer = () => {
  const { loads } = useDataStore()
  const { selectComponent } = useMapStore()

  // Memoize loads to prevent unnecessary re-renders
  const loadMarkers = useMemo(() => {
    return loads.map(load => {
      // Extract coordinates from GeoJSON Point
      const coordinates: [number, number] = [
        load.geometry.coordinates[1],
        load.geometry.coordinates[0]
      ]
      
      // Determine marker size based on load value
      const radius = getLoadRadius(load.p_load)
      
      return (
        <CircleMarker
          key={load.id}
          center={coordinates}
          radius={radius}
          pathOptions={{
            color: '#ff0000',
            fillColor: '#ff0000',
            fillOpacity: 0.6,
            weight: 1
          }}
          eventHandlers={{
            click: () => selectComponent('load', load.id)
          }}
        >
          <Tooltip>
            <div>
              <strong>{load.name || `Load ${load.id}`}</strong>
              <div>Load: {load.p_load} MW</div>
              <div>Bus: {load.bus_id}</div>
            </div>
          </Tooltip>
        </CircleMarker>
      )
    })
  }, [loads, selectComponent])

  return (
    <MarkerClusterGroup
      chunkedLoading
      disableClusteringAtZoom={10}
      spiderfyOnMaxZoom={true}
      polygonOptions={{
        fillColor: '#ff0000',
        color: '#ff0000',
        weight: 2,
        opacity: 0.5,
        fillOpacity: 0.2
      }}
    >
      {loadMarkers}
    </MarkerClusterGroup>
  )
}

// Helper function to get radius based on load value
function getLoadRadius(load: number): number {
  if (!load) return 4
  
  // Scale radius based on load, but keep it within reasonable bounds
  return Math.max(4, Math.min(12, 4 + Math.log10(load) * 1.5))
}

export default LoadLayer
