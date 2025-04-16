import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Header from '@/components/layout/Header'
import MapContainer from '@/components/map/MapContainer'
import AnalyticsPage from '@/pages/AnalyticsPage'
import { useDataStore } from '@/store/dataStore'
import { useMapStore } from '@/store/mapStore'
import Loading from '@/components/ui/loading'

const DashboardPage = () => {
  const { fetchGridData, isLoadingGrid, gridError, fetchHeatmapData } = useDataStore()
  const { currentDate, heatmapType } = useMapStore()

  // Fetch grid data on component mount
  useEffect(() => {
    fetchGridData()
  }, [fetchGridData])

  // Fetch heatmap data when date or type changes
  useEffect(() => {
    fetchHeatmapData(heatmapType, currentDate)
  }, [fetchHeatmapData, heatmapType, currentDate])

  if (isLoadingGrid) {
    return <Loading />
  }

  if (gridError) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Data</h2>
            <p className="text-gray-700 mb-4">{gridError}</p>
            <button
              onClick={() => fetchGridData()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<MapContainer />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  )
}

export default DashboardPage
