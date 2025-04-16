import { useMemo } from 'react'
import { CircleMarker, Tooltip } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'

const GeneratorLayer = () => {
  const { generators } = useDataStore()
  const { selectComponent } = useMapStore()

  // Memoize generators to prevent unnecessary re-renders
  const generatorMarkers = useMemo(() => {
    return generators.map(generator => {
      // Extract coordinates from GeoJSON Point
      const coordinates: [number, number] = [
        generator.geometry.coordinates[1],
        generator.geometry.coordinates[0]
      ]

      // Determine marker style based on generator type
      const color = getGeneratorColor(generator.gen_type)
      const radius = getGeneratorRadius(generator.p_gen)

      return (
        <CircleMarker
          key={generator.id}
          center={coordinates}
          radius={radius}
          pathOptions={{
            color,
            fillColor: color,
            fillOpacity: 0.8,
            weight: 1
          }}
          eventHandlers={{
            click: () => selectComponent('generator', generator.id)
          }}
        >
          <Tooltip>
            <div>
              <strong>{generator.name || `Generator ${generator.id}`}</strong>
              <div>Type: {generator.gen_type}</div>
              <div>Capacity: {generator.p_gen} MW</div>
              <div>Bus: {generator.bus_id}</div>
            </div>
          </Tooltip>
        </CircleMarker>
      )
    })
  }, [generators, selectComponent])

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
      {generatorMarkers}
    </MarkerClusterGroup>
  )
}

// Helper function to get color based on generator type
function getGeneratorColor(genType: string): string {
  if (!genType) return '#808080' // Gray for unknown

  const type = genType.toLowerCase()

  if (type.includes('solar') || type.includes('pv')) return '#ffff00' // Yellow for solar
  if (type.includes('wind') || type.includes('wt')) return '#00ffff' // Cyan for wind
  if (type.includes('hydro')) return '#0000ff' // Blue for hydro
  if (type.includes('nuclear')) return '#800080' // Purple for nuclear
  if (type.includes('coal')) return '#000000' // Black for coal
  if (type.includes('gas') || type.includes('natural')) return '#ff8000' // Orange for natural gas

  return '#808080' // Gray for other types
}

// Helper function to get radius based on generator capacity
function getGeneratorRadius(capacity: number): number {
  if (!capacity) return 5

  // Scale radius based on capacity, but keep it within reasonable bounds
  return Math.max(5, Math.min(15, 5 + Math.log10(capacity) * 2))
}

export default GeneratorLayer
