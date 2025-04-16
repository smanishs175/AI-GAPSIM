import { useState } from 'react'
import { useMapStore } from '@/store/mapStore'

const LayerControls = () => {
  const {
    showBuses,
    showBranches,
    showGenerators,
    showLoads,
    showSubstations,
    showBalancingAuthorities,
    showHeatmap,
    heatmapType,
    toggleLayer,
    setHeatmapType
  } = useMapStore()
  
  const [isExpanded, setIsExpanded] = useState(true)

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 w-64">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-lg">Map Layers</h3>
        <button
          onClick={toggleExpanded}
          className="text-gray-500 hover:text-gray-700"
        >
          {isExpanded ? '−' : '+'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="space-y-3">
          <div className="space-y-2">
            <h4 className="font-medium text-sm text-gray-700">Grid Components</h4>
            <div className="space-y-1">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="branches"
                  checked={showBranches}
                  onChange={() => toggleLayer('branches')}
                  className="mr-2"
                />
                <label htmlFor="branches" className="text-sm">Transmission Lines</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="generators"
                  checked={showGenerators}
                  onChange={() => toggleLayer('generators')}
                  className="mr-2"
                />
                <label htmlFor="generators" className="text-sm">Generators</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="substations"
                  checked={showSubstations}
                  onChange={() => toggleLayer('substations')}
                  className="mr-2"
                />
                <label htmlFor="substations" className="text-sm">Substations</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="loads"
                  checked={showLoads}
                  onChange={() => toggleLayer('loads')}
                  className="mr-2"
                />
                <label htmlFor="loads" className="text-sm">Loads</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="buses"
                  checked={showBuses}
                  onChange={() => toggleLayer('buses')}
                  className="mr-2"
                />
                <label htmlFor="buses" className="text-sm">Buses</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="bas"
                  checked={showBalancingAuthorities}
                  onChange={() => toggleLayer('balancingAuthorities')}
                  className="mr-2"
                />
                <label htmlFor="bas" className="text-sm">Balancing Authorities</label>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium text-sm text-gray-700">Weather Heatmap</h4>
            <div className="flex items-center mb-2">
              <input
                type="checkbox"
                id="heatmap"
                checked={showHeatmap}
                onChange={() => toggleLayer('heatmap')}
                className="mr-2"
              />
              <label htmlFor="heatmap" className="text-sm">Show Heatmap</label>
            </div>
            
            {showHeatmap && (
              <div className="pl-5">
                <h5 className="text-xs text-gray-500 mb-1">Heatmap Type</h5>
                <select
                  value={heatmapType}
                  onChange={(e) => setHeatmapType(e.target.value as any)}
                  className="w-full text-sm p-1 border rounded"
                  disabled={!showHeatmap}
                >
                  <option value="temperature">Temperature</option>
                  <option value="humidity">Humidity</option>
                  <option value="wind_speed">Wind Speed</option>
                  <option value="precipitation">Precipitation</option>
                  <option value="radiation">Solar Radiation</option>
                </select>
              </div>
            )}
          </div>
          
          <div className="pt-2 text-xs text-gray-500">
            <p>Click on grid components to view weather impacts.</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default LayerControls
