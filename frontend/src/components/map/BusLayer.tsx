import { useMemo } from 'react'
import { CircleMarker, Tooltip } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'

const BusLayer = () => {
  const { buses } = useDataStore()
  const { selectComponent } = useMapStore()

  // Memoize buses to prevent unnecessary re-renders
  const busMarkers = useMemo(() => {
    return buses.map(bus => {
      // Extract coordinates from GeoJSON Point
      const coordinates: [number, number] = [
        bus.geometry.coordinates[1],
        bus.geometry.coordinates[0]
      ]

      return (
        <CircleMarker
          key={bus.id}
          center={coordinates}
          radius={4}
          pathOptions={{
            color: '#3388ff',
            fillColor: '#3388ff',
            fillOpacity: 0.8,
            weight: 1
          }}
          eventHandlers={{
            click: () => selectComponent('bus', bus.id)
          }}
        >
          <Tooltip>
            <div>
              <strong>{bus.name || `Bus ${bus.id}`}</strong>
              <div>Voltage: {bus.base_kv} kV</div>
              <div>Area: {bus.metadata?.area || 'Unknown'}</div>
            </div>
          </Tooltip>
        </CircleMarker>
      )
    })
  }, [buses, selectComponent])

  return (
    <MarkerClusterGroup
      chunkedLoading
      disableClusteringAtZoom={10}
      spiderfyOnMaxZoom={true}
      polygonOptions={{
        fillColor: '#3388ff',
        color: '#3388ff',
        weight: 2,
        opacity: 0.5,
        fillOpacity: 0.2
      }}
    >
      {busMarkers}
    </MarkerClusterGroup>
  )
}

export default BusLayer
