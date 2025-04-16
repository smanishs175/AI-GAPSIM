import { useEffect, useMemo } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'
import Loading from '@/components/ui/loading'

// Extend window interface to include L.heatLayer
declare global {
  interface Window {
    L: typeof L & {
      heatLayer: (latlngs: L.LatLngExpression[], options?: any) => L.Layer
    }
  }
}

const HeatmapLayer = () => {
  const map = useMap()
  const { heatmapData, isLoadingHeatmap, heatmapError, fetchHeatmapData } = useDataStore()
  const { currentDate, heatmapType } = useMapStore()

  // Convert heatmap data to format expected by Leaflet.heat
  const heatmapPoints = useMemo(() => {
    if (!heatmapData) return []
    
    return heatmapData.data.map(point => {
      // point is [lat, lon, value]
      return [point[0], point[1], point[2]]
    })
  }, [heatmapData])

  // Create and update heatmap layer
  useEffect(() => {
    if (!heatmapData || heatmapPoints.length === 0) return

    // Remove existing heatmap layer if it exists
    map.eachLayer(layer => {
      if ((layer as any)._heat) {
        map.removeLayer(layer)
      }
    })

    // Create new heatmap layer
    const heatLayer = (window.L || L).heatLayer(heatmapPoints as any, {
      radius: 25,
      blur: 15,
      maxZoom: 10,
      max: heatmapData.bounds.max_value,
      gradient: getGradient(heatmapType)
    })

    // Add layer to map
    heatLayer.addTo(map)

    // Cleanup on unmount
    return () => {
      map.removeLayer(heatLayer)
    }
  }, [map, heatmapPoints, heatmapData, heatmapType])

  // Fetch heatmap data when date or type changes
  useEffect(() => {
    fetchHeatmapData(heatmapType, currentDate)
  }, [fetchHeatmapData, heatmapType, currentDate])

  // Show loading or error overlay
  if (isLoadingHeatmap) {
    return (
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1000] bg-white bg-opacity-80 p-4 rounded-md shadow-md">
        <Loading />
      </div>
    )
  }

  if (heatmapError) {
    return (
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1000] bg-white bg-opacity-80 p-4 rounded-md shadow-md">
        <div className="text-red-500">{heatmapError}</div>
        <button
          onClick={() => fetchHeatmapData(heatmapType, currentDate)}
          className="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    )
  }

  return null
}

// Helper function to get gradient based on heatmap type
function getGradient(type: string): Record<number, string> {
  switch (type) {
    case 'temperature':
      return {
        0.0: 'blue',
        0.4: 'cyan',
        0.6: 'lime',
        0.8: 'yellow',
        1.0: 'red'
      }
    case 'humidity':
      return {
        0.0: 'white',
        0.4: 'lightblue',
        0.6: 'blue',
        0.8: 'darkblue',
        1.0: 'purple'
      }
    case 'wind_speed':
      return {
        0.0: 'white',
        0.4: 'lightgreen',
        0.6: 'green',
        0.8: 'darkgreen',
        1.0: 'black'
      }
    case 'precipitation':
      return {
        0.0: 'white',
        0.4: 'lightblue',
        0.6: 'blue',
        0.8: 'darkblue',
        1.0: 'purple'
      }
    case 'radiation':
      return {
        0.0: 'black',
        0.4: 'purple',
        0.6: 'orange',
        0.8: 'yellow',
        1.0: 'white'
      }
    default:
      return {
        0.0: 'blue',
        0.4: 'cyan',
        0.6: 'lime',
        0.8: 'yellow',
        1.0: 'red'
      }
  }
}

export default HeatmapLayer
