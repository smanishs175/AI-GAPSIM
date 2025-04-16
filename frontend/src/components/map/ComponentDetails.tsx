import { useEffect } from 'react'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Loading from '@/components/ui/loading'

interface ComponentDetailsProps {
  onClose: () => void
}

const ComponentDetails: React.FC<ComponentDetailsProps> = ({ onClose }) => {
  const { selectedComponentWeather, isLoadingComponentWeather, componentWeatherError, clearComponentWeather } = useDataStore()
  const { selectedComponentType, startDate, endDate } = useMapStore()

  // Clean up when component unmounts
  useEffect(() => {
    return () => {
      clearComponentWeather()
    }
  }, [clearComponentWeather])

  if (isLoadingComponentWeather) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[2000]">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Loading Component Data</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <Loading />
        </div>
      </div>
    )
  }

  if (componentWeatherError) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[2000]">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Error</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <div className="text-red-500 mb-4">{componentWeatherError}</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Close
          </button>
        </div>
      </div>
    )
  }

  if (!selectedComponentWeather) {
    return null
  }

  const { component, weather_data, impacts } = selectedComponentWeather

  // Prepare data for charts
  const chartData = weather_data.map((data, index) => {
    const dailyImpact = impacts.daily_impacts[index]
    return {
      date: new Date(data.date).toLocaleDateString(),
      maxTemp: data.max_temperature,
      avgTemp: data.avg_temperature,
      minTemp: data.min_temperature,
      humidity: data.relative_humidity,
      windSpeed: data.wind_speed,
      precipitation: data.precipitation,
      // Component-specific impacts
      ...getComponentImpacts(selectedComponentType, dailyImpact)
    }
  })

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[2000]">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {getComponentTitle(selectedComponentType, component)}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Component Details</h3>
          <div className="grid grid-cols-2 gap-4">
            {renderComponentDetails(selectedComponentType, component)}
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Weather Impact</h3>
          <p className="text-sm text-gray-600 mb-4">
            Date Range: {startDate} to {endDate}
          </p>

          <div className="mb-6">
            <h4 className="font-medium mb-2">Temperature</h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="maxTemp" name="Max Temp" stroke="#ff0000" />
                  <Line yAxisId="left" type="monotone" dataKey="avgTemp" name="Avg Temp" stroke="#ff8c00" />
                  <Line yAxisId="left" type="monotone" dataKey="minTemp" name="Min Temp" stroke="#0000ff" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mb-6">
            <h4 className="font-medium mb-2">Weather Parameters</h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'Humidity (%)', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Wind Speed (m/s)', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="humidity" name="Humidity" stroke="#8884d8" />
                  <Line yAxisId="right" type="monotone" dataKey="windSpeed" name="Wind Speed" stroke="#82ca9d" />
                  <Line yAxisId="right" type="monotone" dataKey="precipitation" name="Precipitation" stroke="#4682b4" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {renderComponentImpactChart(selectedComponentType, chartData)}
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            {renderSummary(selectedComponentType, impacts.summary)}
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper function to get component title
function getComponentTitle(type: string | null, component: any): string {
  if (!type || !component) return 'Component Details'

  const name = component.name || `${type.charAt(0).toUpperCase() + type.slice(1)} ${component.id}`

  return `${name} (${type.charAt(0).toUpperCase() + type.slice(1)})`
}

// Helper function to render component details
function renderComponentDetails(type: string | null, component: any): React.ReactNode {
  if (!type || !component) return null

  switch (type) {
    case 'bus':
      return (
        <>
          <div>
            <span className="font-medium">ID:</span> {component.id}
          </div>
          <div>
            <span className="font-medium">Name:</span> {component.name || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Type:</span> {getBusType(component.bus_type)}
          </div>
          <div>
            <span className="font-medium">Base kV:</span> {component.base_kv} kV
          </div>
        </>
      )
    case 'branch':
      return (
        <>
          <div>
            <span className="font-medium">ID:</span> {component.id}
          </div>
          <div>
            <span className="font-medium">Name:</span> {component.name || 'N/A'}
          </div>
          <div>
            <span className="font-medium">From Bus:</span> {component.from_bus_id}
          </div>
          <div>
            <span className="font-medium">To Bus:</span> {component.to_bus_id}
          </div>
          <div>
            <span className="font-medium">Rating:</span> {component.rate1} MVA
          </div>
          <div>
            <span className="font-medium">Status:</span> {component.status ? 'In Service' : 'Out of Service'}
          </div>
        </>
      )
    case 'generator':
      return (
        <>
          <div>
            <span className="font-medium">ID:</span> {component.id}
          </div>
          <div>
            <span className="font-medium">Name:</span> {component.name || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Bus:</span> {component.bus_id}
          </div>
          <div>
            <span className="font-medium">Type:</span> {component.gen_type}
          </div>
          <div>
            <span className="font-medium">Active Power:</span> {component.p_gen} MW
          </div>
          <div>
            <span className="font-medium">Reactive Power:</span> {component.q_gen} MVAr
          </div>
          <div>
            <span className="font-medium">P Max:</span> {component.p_max} MW
          </div>
          <div>
            <span className="font-medium">P Min:</span> {component.p_min} MW
          </div>
        </>
      )
    case 'load':
      return (
        <>
          <div>
            <span className="font-medium">ID:</span> {component.id}
          </div>
          <div>
            <span className="font-medium">Name:</span> {component.name || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Bus:</span> {component.bus_id}
          </div>
          <div>
            <span className="font-medium">Active Power:</span> {component.p_load} MW
          </div>
          <div>
            <span className="font-medium">Reactive Power:</span> {component.q_load} MVAr
          </div>
        </>
      )
    case 'substation':
      return (
        <>
          <div>
            <span className="font-medium">ID:</span> {component.id}
          </div>
          <div>
            <span className="font-medium">Name:</span> {component.name || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Voltage:</span> {component.voltage} kV
          </div>
        </>
      )
    default:
      return null
  }
}

// Helper function to get bus type description
function getBusType(type: number): string {
  switch (type) {
    case 1:
      return 'PQ Bus'
    case 2:
      return 'PV Bus'
    case 3:
      return 'Slack Bus'
    default:
      return `Type ${type}`
  }
}

// Helper function to get component-specific impacts
function getComponentImpacts(type: string | null, dailyImpact: any): Record<string, number> {
  if (!type || !dailyImpact) return {}

  switch (type) {
    case 'load':
      return {
        PL_day: dailyImpact?.load_impact?.PL_day || 0,
        QL_day: dailyImpact?.load_impact?.QL_day || 0
      }
    case 'generator':
      return {
        Pgen_day: dailyImpact?.generator_impact?.Pgen_day || 0,
        Qgen_day: dailyImpact?.generator_impact?.Qgen_day || 0,
        Efficiency: dailyImpact?.generator_impact?.Efficiency || 0
      }
    case 'branch':
      return {
        CL_day: dailyImpact?.branch_impact?.CL_day || 0
      }
    default:
      return {}
  }
}

// Helper function to render component-specific impact chart
function renderComponentImpactChart(type: string | null, chartData: any[]): React.ReactNode {
  if (!type || !chartData.length) return null

  switch (type) {
    case 'load':
      return (
        <div className="mb-6">
          <h4 className="font-medium mb-2">Load Impact</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Power (MW/MVAr)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="PL_day" name="Active Power" stroke="#8884d8" />
                <Line type="monotone" dataKey="QL_day" name="Reactive Power" stroke="#82ca9d" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )
    case 'generator':
      return (
        <div className="mb-6">
          <h4 className="font-medium mb-2">Generator Impact</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" label={{ value: 'Power (MW/MVAr)', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" label={{ value: 'Efficiency', angle: 90, position: 'insideRight' }} />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="Pgen_day" name="Active Power" stroke="#8884d8" />
                <Line yAxisId="left" type="monotone" dataKey="Qgen_day" name="Reactive Power" stroke="#82ca9d" />
                <Line yAxisId="right" type="monotone" dataKey="Efficiency" name="Efficiency" stroke="#ff7300" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )
    case 'branch':
      return (
        <div className="mb-6">
          <h4 className="font-medium mb-2">Line Capacity Impact</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Capacity (MVA)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="CL_day" name="Line Capacity" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )
    default:
      return null
  }
}

// Helper function to render summary
function renderSummary(type: string | null, summary: any): React.ReactNode {
  if (!type || !summary) return null

  // Render weather summary
  const weatherSummary = (
    <>
      <div>
        <span className="font-medium">Max Temperature:</span>{' '}
        {summary.weather.max_temperature.max.toFixed(1)}°C on {new Date(summary.weather.max_temperature.max_date).toLocaleDateString()}
      </div>
      <div>
        <span className="font-medium">Min Temperature:</span>{' '}
        {summary.weather.min_temperature.min.toFixed(1)}°C on {new Date(summary.weather.min_temperature.min_date).toLocaleDateString()}
      </div>
      <div>
        <span className="font-medium">Max Humidity:</span>{' '}
        {summary.weather.relative_humidity.max.toFixed(1)}% on {new Date(summary.weather.relative_humidity.max_date).toLocaleDateString()}
      </div>
      <div>
        <span className="font-medium">Max Wind Speed:</span>{' '}
        {summary.weather.wind_speed.max.toFixed(1)} m/s on {new Date(summary.weather.wind_speed.max_date).toLocaleDateString()}
      </div>
    </>
  )

  // Render component-specific summary
  let componentSummary = null

  switch (type) {
    case 'load':
      if (summary.load_impact) {
        componentSummary = (
          <>
            <div>
              <span className="font-medium">Max Active Power:</span>{' '}
              {summary.load_impact.PL_day.max.toFixed(1)} MW on {new Date(summary.load_impact.PL_day.max_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Min Active Power:</span>{' '}
              {summary.load_impact.PL_day.min.toFixed(1)} MW on {new Date(summary.load_impact.PL_day.min_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Max Reactive Power:</span>{' '}
              {summary.load_impact.QL_day.max.toFixed(1)} MVAr on {new Date(summary.load_impact.QL_day.max_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Min Reactive Power:</span>{' '}
              {summary.load_impact.QL_day.min.toFixed(1)} MVAr on {new Date(summary.load_impact.QL_day.min_date).toLocaleDateString()}
            </div>
          </>
        )
      }
      break
    case 'generator':
      if (summary.generator_impact) {
        componentSummary = (
          <>
            <div>
              <span className="font-medium">Max Active Power:</span>{' '}
              {summary.generator_impact.Pgen_day.max.toFixed(1)} MW on {new Date(summary.generator_impact.Pgen_day.max_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Min Active Power:</span>{' '}
              {summary.generator_impact.Pgen_day.min.toFixed(1)} MW on {new Date(summary.generator_impact.Pgen_day.min_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Min Efficiency:</span>{' '}
              {(summary.generator_impact.Efficiency.min * 100).toFixed(1)}% on {new Date(summary.generator_impact.Efficiency.min_date).toLocaleDateString()}
            </div>
          </>
        )
      }
      break
    case 'branch':
      if (summary.branch_impact) {
        componentSummary = (
          <>
            <div>
              <span className="font-medium">Max Line Capacity:</span>{' '}
              {summary.branch_impact.CL_day.max.toFixed(1)} MVA on {new Date(summary.branch_impact.CL_day.max_date).toLocaleDateString()}
            </div>
            <div>
              <span className="font-medium">Min Line Capacity:</span>{' '}
              {summary.branch_impact.CL_day.min.toFixed(1)} MVA on {new Date(summary.branch_impact.CL_day.min_date).toLocaleDateString()}
            </div>
          </>
        )
      }
      break
    default:
      break
  }

  return (
    <>
      {weatherSummary}
      {componentSummary}
    </>
  )
}

export default ComponentDetails
