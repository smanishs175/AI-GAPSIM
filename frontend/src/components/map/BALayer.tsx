import { useMemo } from 'react'
import { GeoJSON, Tooltip } from 'react-leaflet'
import { useDataStore } from '@/store/dataStore'

const BALayer = () => {
  const { balancingAuthorities } = useDataStore()

  // Memoize BA polygons to prevent unnecessary re-renders
  const baPolygons = useMemo(() => {
    return balancingAuthorities.map(ba => {
      // Generate a random color based on BA id for consistent coloring
      const color = getColorForBA(ba.id)

      return (
        <GeoJSON
          key={ba.id}
          data={ba.geometry as any}
          style={{
            fillColor: color,
            weight: 2,
            opacity: 0.7,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.3
          }}
          eventHandlers={{
            mouseover: (event) => {
              const layer = event.target
              layer.setStyle({
                weight: 3,
                color: '#666',
                dashArray: '',
                fillOpacity: 0.5
              })
              layer.bringToFront()
            },
            mouseout: (event) => {
              const layer = event.target
              layer.setStyle({
                fillColor: color,
                weight: 2,
                opacity: 0.7,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.3
              })
            },
            click: () => {
              // Handle click event if needed
              console.log(`Clicked on BA: ${ba.name}`)
            }
          }}
        >
          <Tooltip sticky>
            <div>
              <strong>{ba.name}</strong>
              <div>Abbreviation: {ba.abbreviation}</div>
            </div>
          </Tooltip>
        </GeoJSON>
      )
    })
  }, [balancingAuthorities])

  return <>{baPolygons}</>
}

// Helper function to get a consistent color for a BA based on its ID
function getColorForBA(id: number): string {
  // List of distinct colors for BAs
  const colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
  ]

  // Use modulo to cycle through colors if there are more BAs than colors
  return colors[id % colors.length]
}

export default BALayer
