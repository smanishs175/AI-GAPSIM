import { useState, useEffect } from 'react'
// import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#8DD1E1']

const AnalyticsPage = () => {
  const { token } = useAuthStore()
  // const navigate = useNavigate()

  const [weatherSummary, setWeatherSummary] = useState<any>(null)
  const [gridStats, setGridStats] = useState<any>(null)
  const [eeaAnalysis, setEeaAnalysis] = useState<any>(null)
  const [correlation, setCorrelation] = useState<any>(null)

  const [startDate, setStartDate] = useState('2020-07-21')
  const [endDate, setEndDate] = useState('2020-07-30')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch data when component mounts or date range changes
  useEffect(() => {
    if (!token) return

    const fetchData = async () => {
      setIsLoading(true)
      setError(null)

      try {
        // Fetch weather summary
        const weatherResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/api/analytics/weather-summary?start_date=${startDate}&end_date=${endDate}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        if (!weatherResponse.ok) {
          throw new Error('Failed to fetch weather summary')
        }

        const weatherData = await weatherResponse.json()
        setWeatherSummary(weatherData)

        // Fetch grid statistics
        const gridResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/api/analytics/grid-statistics`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        if (!gridResponse.ok) {
          throw new Error('Failed to fetch grid statistics')
        }

        const gridData = await gridResponse.json()
        setGridStats(gridData)

        // Fetch EEA analysis
        const eeaResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/api/analytics/eea-analysis?start_date=${startDate}&end_date=${endDate}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        if (!eeaResponse.ok) {
          throw new Error('Failed to fetch EEA analysis')
        }

        const eeaData = await eeaResponse.json()
        setEeaAnalysis(eeaData)

        // Fetch weather-impact correlation
        const correlationResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/api/analytics/weather-impact-correlation?start_date=${startDate}&end_date=${endDate}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        if (!correlationResponse.ok) {
          throw new Error('Failed to fetch weather-impact correlation')
        }

        const correlationData = await correlationResponse.json()
        setCorrelation(correlationData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [token, startDate, endDate])

  const handleDateRangeChange = () => {
    // Validate dates
    if (new Date(startDate) > new Date(endDate)) {
      setError('Start date must be before end date')
      return
    }

    // Reset error
    setError(null)
  }

  // Prepare data for charts
  const prepareGenerationByTypeData = () => {
    if (!gridStats || !gridStats.generation || !gridStats.generation.by_type) {
      return []
    }

    return gridStats.generation.by_type.map((item: any) => ({
      name: item.type,
      value: item.total_capacity
    }))
  }

  const prepareEeaByLevelData = () => {
    if (!eeaAnalysis || !eeaAnalysis.summary || !eeaAnalysis.summary.by_level) {
      return []
    }

    return Object.entries(eeaAnalysis.summary.by_level).map(([level, count]: [string, any]) => ({
      name: `Level ${level}`,
      value: count
    }))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Power Grid Analytics</h1>

      {/* Date Range Selector */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-xl font-semibold mb-4">Date Range</h2>
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="p-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="p-2 border rounded"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleDateRangeChange}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Apply'}
            </button>
          </div>
        </div>
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>

      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics data...</p>
        </div>
      ) : (
        <>
          {/* Grid Statistics */}
          {gridStats && (
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <h2 className="text-xl font-semibold mb-4">Grid Statistics</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Component Counts */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Component Counts</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={Object.entries(gridStats.component_counts).map(([key, value]: [string, any]) => ({
                          name: key.charAt(0).toUpperCase() + key.slice(1),
                          count: value
                        }))}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Generation by Type */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Generation by Type</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={prepareGenerationByTypeData()}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {prepareGenerationByTypeData().map((_entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: any) => `${Number(value).toFixed(2)} MW`} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <h3 className="text-lg font-medium mb-2">System Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="text-gray-500 text-sm">Total Generation Capacity</div>
                    <div className="text-2xl font-bold">{gridStats.generation.total_capacity.toFixed(2)} MW</div>
                  </div>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="text-gray-500 text-sm">Total Load</div>
                    <div className="text-2xl font-bold">{gridStats.load.total_load.toFixed(2)} MW</div>
                  </div>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="text-gray-500 text-sm">Generation to Load Ratio</div>
                    <div className="text-2xl font-bold">{gridStats.system_metrics.generation_to_load_ratio.toFixed(2)}</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Weather Summary */}
          {weatherSummary && (
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <h2 className="text-xl font-semibold mb-4">Weather Summary</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Temperature Trend */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Temperature Trend</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={weatherSummary.temperature_trend}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#ff7300" name="Avg Temperature" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Precipitation Trend */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Precipitation Trend</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={weatherSummary.precipitation_trend}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis label={{ value: 'Precipitation (mm)', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#8884d8" name="Avg Precipitation" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-medium mb-2">Extreme Weather Events</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* High Temperature Events */}
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-red-600 mb-2">High Temperature Events</h4>
                    {weatherSummary.extreme_events.high_temperature.length > 0 ? (
                      <ul className="space-y-2">
                        {weatherSummary.extreme_events.high_temperature.map((event: any, index: number) => (
                          <li key={index} className="text-sm">
                            <div className="font-medium">{event.date}</div>
                            <div>Temperature: {event.max_temperature.toFixed(1)}°C</div>
                            <div className="text-gray-500">
                              Location: {event.latitude.toFixed(2)}, {event.longitude.toFixed(2)}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 text-sm">No high temperature events found</p>
                    )}
                  </div>

                  {/* High Wind Events */}
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-blue-600 mb-2">High Wind Events</h4>
                    {weatherSummary.extreme_events.high_wind.length > 0 ? (
                      <ul className="space-y-2">
                        {weatherSummary.extreme_events.high_wind.map((event: any, index: number) => (
                          <li key={index} className="text-sm">
                            <div className="font-medium">{event.date}</div>
                            <div>Wind Speed: {event.wind_speed.toFixed(1)} m/s</div>
                            <div className="text-gray-500">
                              Location: {event.latitude.toFixed(2)}, {event.longitude.toFixed(2)}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 text-sm">No high wind events found</p>
                    )}
                  </div>

                  {/* High Precipitation Events */}
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-purple-600 mb-2">High Precipitation Events</h4>
                    {weatherSummary.extreme_events.high_precipitation.length > 0 ? (
                      <ul className="space-y-2">
                        {weatherSummary.extreme_events.high_precipitation.map((event: any, index: number) => (
                          <li key={index} className="text-sm">
                            <div className="font-medium">{event.date}</div>
                            <div>Precipitation: {event.precipitation.toFixed(1)} mm</div>
                            <div className="text-gray-500">
                              Location: {event.latitude.toFixed(2)}, {event.longitude.toFixed(2)}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 text-sm">No high precipitation events found</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* EEA Analysis */}
          {eeaAnalysis && (
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <h2 className="text-xl font-semibold mb-4">Energy Emergency Alert Analysis</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* EEA by Level */}
                <div>
                  <h3 className="text-lg font-medium mb-2">EEA by Level</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={prepareEeaByLevelData()}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {prepareEeaByLevelData().map((_entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* EEA by BA */}
                <div>
                  <h3 className="text-lg font-medium mb-2">EEA by Balancing Authority</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={Object.entries(eeaAnalysis.summary.by_ba || {}).map(([ba, count]: [string, any]) => ({
                          name: ba,
                          count: count
                        }))}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" fill="#82ca9d" name="Number of Events" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-medium mb-2">Recent EEA Events</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">BA</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {eeaAnalysis.events.slice(0, 5).map((event: any) => (
                        <tr key={event.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{event.date}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              event.level === 1 ? 'bg-yellow-100 text-yellow-800' :
                              event.level === 2 ? 'bg-orange-100 text-orange-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              Level {event.level}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{event.ba_abbreviation}</td>
                          <td className="px-6 py-4 text-sm">{event.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Weather-Impact Correlation */}
          {correlation && (
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <h2 className="text-xl font-semibold mb-4">Weather-Impact Correlation</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Weather Comparison */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Weather Comparison: EEA Days vs. All Days</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={[
                          {
                            name: 'Temperature',
                            eea: correlation.summary.eea_days_weather.avg_max_temperature,
                            all: correlation.summary.all_days_weather.avg_max_temperature
                          },
                          {
                            name: 'Wind Speed',
                            eea: correlation.summary.eea_days_weather.avg_wind_speed,
                            all: correlation.summary.all_days_weather.avg_wind_speed
                          },
                          {
                            name: 'Precipitation',
                            eea: correlation.summary.eea_days_weather.avg_precipitation,
                            all: correlation.summary.all_days_weather.avg_precipitation
                          }
                        ]}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="eea" fill="#8884d8" name="EEA Days" />
                        <Bar dataKey="all" fill="#82ca9d" name="All Days" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Correlation Summary */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Correlation Summary</h3>
                  <div className="space-y-4">
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <div className="text-gray-500 text-sm">Temperature Correlation</div>
                      <div className="flex items-center">
                        <div className="text-xl font-bold">{correlation.conclusion.temperature_correlation}</div>
                        <div className="ml-2 text-sm text-gray-500">
                          ({correlation.summary.percentage_difference.max_temperature.toFixed(1)}% difference)
                        </div>
                      </div>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <div className="text-gray-500 text-sm">Wind Speed Correlation</div>
                      <div className="flex items-center">
                        <div className="text-xl font-bold">{correlation.conclusion.wind_correlation}</div>
                        <div className="ml-2 text-sm text-gray-500">
                          ({correlation.summary.percentage_difference.wind_speed.toFixed(1)}% difference)
                        </div>
                      </div>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <div className="text-gray-500 text-sm">Precipitation Correlation</div>
                      <div className="flex items-center">
                        <div className="text-xl font-bold">{correlation.conclusion.precipitation_correlation}</div>
                        <div className="ml-2 text-sm text-gray-500">
                          ({correlation.summary.percentage_difference.precipitation.toFixed(1)}% difference)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-medium mb-2">Interpretation</h3>
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                  <p className="text-blue-700">
                    {correlation.conclusion.temperature_correlation === 'High' &&
                      'There appears to be a strong correlation between temperature and grid emergencies. ' +
                      'Higher temperatures may lead to increased cooling demand and reduced generation efficiency.'}

                    {correlation.conclusion.wind_correlation === 'High' &&
                      'Wind speed shows a significant correlation with grid emergencies. ' +
                      'This could affect both wind generation output and transmission line capacity.'}

                    {correlation.conclusion.precipitation_correlation === 'High' &&
                      'Precipitation levels correlate with grid emergencies. ' +
                      'This may impact hydro generation and increase the risk of transmission line outages.'}

                    {correlation.conclusion.temperature_correlation !== 'High' &&
                     correlation.conclusion.wind_correlation !== 'High' &&
                     correlation.conclusion.precipitation_correlation !== 'High' &&
                      'No strong correlations were found between weather parameters and grid emergencies in this time period. ' +
                      'Other factors may be more significant in triggering emergency events.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AnalyticsPage
