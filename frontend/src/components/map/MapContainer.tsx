import { useEffect, useState } from 'react'
import { MapContainer as LeafletMapContainer, TileLayer, ZoomControl } from 'react-leaflet'
import { useMapStore } from '@/store/mapStore'
import { useDataStore } from '@/store/dataStore'
import LayerControls from '@/components/controls/LayerControls'
import DateRangePicker from '@/components/controls/DateRangePicker'
import TimeSlider from '@/components/controls/TimeSlider'
import HeatmapLayer from '@/components/map/HeatmapLayer'
import BranchLayer from '@/components/map/BranchLayer'
import GeneratorLayer from '@/components/map/GeneratorLayer'
import SubstationLayer from '@/components/map/SubstationLayer'
import BALayer from '@/components/map/BALayer'
import ComponentDetails from '@/components/map/ComponentDetails'

const MapContainer = () => {
  const { center, zoom, showHeatmap, showBranches, showGenerators, showSubstations, showBalancingAuthorities } = useMapStore()
  const { selectedComponentWeather, isLoadingComponentWeather } = useDataStore()
  const [showDetails, setShowDetails] = useState(false)

  // Show component details when weather data is loaded
  useEffect(() => {
    if (selectedComponentWeather && !isLoadingComponentWeather) {
      setShowDetails(true)
    }
  }, [selectedComponentWeather, isLoadingComponentWeather])

  return (
    <div className="map-container">
      <LeafletMapContainer
        center={center}
        zoom={zoom}
        zoomControl={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="bottomright" />
        
        {/* Map Layers */}
        {showHeatmap && <HeatmapLayer />}
        {showBalancingAuthorities && <BALayer />}
        {showBranches && <BranchLayer />}
        {showGenerators && <GeneratorLayer />}
        {showSubstations && <SubstationLayer />}
      </LeafletMapContainer>
      
      {/* Controls */}
      <div className="absolute top-4 right-4 z-[1000]">
        <LayerControls />
      </div>
      
      <div className="absolute top-4 left-4 z-[1000]">
        <DateRangePicker />
      </div>
      
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-[1000] w-4/5 max-w-3xl">
        <TimeSlider />
      </div>
      
      {/* Component Details Modal */}
      {showDetails && selectedComponentWeather && (
        <ComponentDetails onClose={() => setShowDetails(false)} />
      )}
    </div>
  )
}

export default MapContainer
