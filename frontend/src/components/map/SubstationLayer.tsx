import { useMemo } from 'react'
import { Marker, Tooltip } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import L from 'leaflet'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'

// Create custom substation icon
const substationIcon = L.divIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-800"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect><line x1="3" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="21" y2="12"></line><line x1="12" y1="3" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="21"></line></svg>`,
  className: 'substation-icon',
  iconSize: [24, 24],
  iconAnchor: [12, 12]
})

const SubstationLayer = () => {
  const { substations } = useDataStore()
  const { selectComponent } = useMapStore()

  // Memoize substations to prevent unnecessary re-renders
  const substationMarkers = useMemo(() => {
    return substations.map(substation => {
      // Extract coordinates from GeoJSON Point
      const coordinates: [number, number] = [
        substation.geometry.coordinates[1],
        substation.geometry.coordinates[0]
      ]

      return (
        <Marker
          key={substation.id}
          position={coordinates}
          icon={substationIcon}
          eventHandlers={{
            click: () => selectComponent('substation', substation.id)
          }}
        >
          <Tooltip>
            <div>
              <strong>{substation.name || `Substation ${substation.id}`}</strong>
              <div>Voltage: {substation.voltage} kV</div>
            </div>
          </Tooltip>
        </Marker>
      )
    })
  }, [substations, selectComponent])

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
      {substationMarkers}
    </MarkerClusterGroup>
  )
}

export default SubstationLayer
