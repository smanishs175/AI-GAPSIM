import { useMemo } from 'react'
import { Polyline, Tooltip } from 'react-leaflet'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'

const BranchLayer = () => {
  const { branches } = useDataStore()
  const { selectComponent } = useMapStore()

  // Memoize branches to prevent unnecessary re-renders
  const branchLines = useMemo(() => {
    return branches.map(branch => {
      // Extract coordinates from GeoJSON LineString
      const coordinates = branch.geometry.coordinates.map(coord => [coord[1], coord[0]] as [number, number])
      
      // Determine line style based on voltage level and status
      const color = getVoltageColor(branch.rate1)
      const weight = getVoltageWeight(branch.rate1)
      const dashArray = branch.status ? undefined : '5, 5'
      
      return (
        <Polyline
          key={branch.id}
          positions={coordinates}
          pathOptions={{
            color,
            weight,
            dashArray,
            opacity: 0.8
          }}
          eventHandlers={{
            click: () => selectComponent('branch', branch.id)
          }}
        >
          <Tooltip sticky>
            <div>
              <strong>{branch.name || `Branch ${branch.id}`}</strong>
              <div>Voltage: {branch.rate1} kV</div>
              <div>Status: {branch.status ? 'In Service' : 'Out of Service'}</div>
              <div>Rating: {branch.rate1} MVA</div>
            </div>
          </Tooltip>
        </Polyline>
      )
    })
  }, [branches, selectComponent])

  return <>{branchLines}</>
}

// Helper function to get color based on voltage level
function getVoltageColor(voltage: number): string {
  if (voltage >= 500) return '#ff0000' // Red for 500kV+
  if (voltage >= 345) return '#ffa500' // Orange for 345kV
  if (voltage >= 230) return '#0000ff' // Blue for 230kV
  if (voltage >= 115) return '#00ff00' // Green for 115kV
  return '#808080' // Gray for lower voltages
}

// Helper function to get line weight based on voltage level
function getVoltageWeight(voltage: number): number {
  if (voltage >= 500) return 4
  if (voltage >= 345) return 3
  if (voltage >= 230) return 2
  return 1
}

export default BranchLayer
