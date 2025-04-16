import { create } from 'zustand'

// Define types for grid components
export interface Bus {
  id: number
  name: string
  bus_type: number
  base_kv: number
  geometry: GeoJSON.Point
  metadata: Record<string, any>
}

export interface Branch {
  id: number
  name: string
  from_bus_id: number
  to_bus_id: number
  rate1: number
  rate2: number
  rate3: number
  status: boolean
  geometry: GeoJSON.LineString
  metadata: Record<string, any>
}

export interface Generator {
  id: number
  name: string
  bus_id: number
  p_gen: number
  q_gen: number
  p_max: number
  p_min: number
  q_max: number
  q_min: number
  gen_type: string
  geometry: GeoJSON.Point
  metadata: Record<string, any>
}

export interface Load {
  id: number
  name: string
  bus_id: number
  p_load: number
  q_load: number
  geometry: GeoJSON.Point
  metadata: Record<string, any>
}

export interface Substation {
  id: number
  name: string
  voltage: number
  geometry: GeoJSON.Point
  metadata: Record<string, any>
}

export interface BalancingAuthority {
  id: number
  name: string
  abbreviation: string
  geometry: GeoJSON.Polygon
  metadata: Record<string, any>
}

export interface HeatmapData {
  parameter: string
  date: string
  data: [number, number, number][] // [lat, lon, value]
  bounds: {
    min_lat: number
    max_lat: number
    min_lon: number
    max_lon: number
    min_value: number
    max_value: number
  }
}

export interface WeatherData {
  date: string
  latitude: number
  longitude: number
  max_temperature: number
  avg_temperature: number
  min_temperature: number
  relative_humidity: number
  specific_humidity: number
  longwave_radiation: number
  shortwave_radiation: number
  precipitation: number
  wind_speed: number
}

export interface ComponentWeatherData {
  component: any
  weather_data: WeatherData[]
  impacts: {
    daily_impacts: {
      date: string
      weather: Record<string, number>
      load_impact?: {
        PL_day: number
        QL_day: number
      }
      generator_impact?: {
        Pgen_day: number
        Qgen_day: number
        Efficiency: number
      }
      branch_impact?: {
        CL_day: number
      }
    }[]
    summary: Record<string, any>
  }
}

interface DataState {
  // Grid components
  buses: Bus[]
  branches: Branch[]
  generators: Generator[]
  loads: Load[]
  substations: Substation[]
  balancingAuthorities: BalancingAuthority[]

  // Weather and heatmap data
  heatmapData: HeatmapData | null
  selectedComponentWeather: ComponentWeatherData | null

  // Loading states
  isLoadingGrid: boolean
  isLoadingHeatmap: boolean
  isLoadingComponentWeather: boolean

  // Error states
  gridError: string | null
  heatmapError: string | null
  componentWeatherError: string | null

  // Actions
  fetchGridData: () => Promise<void>
  fetchHeatmapData: (parameter: string, date: string) => Promise<void>
  fetchComponentWeather: (componentType: string, componentId: number, startDate: string, endDate: string) => Promise<void>
  clearComponentWeather: () => void
  clearErrors: () => void
}

export const useDataStore = create<DataState>((set) => ({
  // Initial state
  buses: [],
  branches: [],
  generators: [],
  loads: [],
  substations: [],
  balancingAuthorities: [],

  heatmapData: null,
  selectedComponentWeather: null,

  isLoadingGrid: false,
  isLoadingHeatmap: false,
  isLoadingComponentWeather: false,

  gridError: null,
  heatmapError: null,
  componentWeatherError: null,

  // Actions
  fetchGridData: async () => {
    set({ isLoadingGrid: true, gridError: null })

    try {
      // Fetch all grid components in parallel using public endpoints
      const [busesRes, branchesRes, generatorsRes, loadsRes, substationsRes, basRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_URL}/api/public/buses`),
        fetch(`${import.meta.env.VITE_API_URL}/api/public/branches`),
        fetch(`${import.meta.env.VITE_API_URL}/api/public/generators`),
        fetch(`${import.meta.env.VITE_API_URL}/api/public/loads`),
        fetch(`${import.meta.env.VITE_API_URL}/api/public/substations`),
        fetch(`${import.meta.env.VITE_API_URL}/api/public/bas`)
      ])

      // Check for errors
      if (!busesRes.ok || !branchesRes.ok || !generatorsRes.ok || !loadsRes.ok || !substationsRes.ok || !basRes.ok) {
        throw new Error('Failed to fetch grid data')
      }

      // Parse responses
      const buses = await busesRes.json()
      const branches = await branchesRes.json()
      const generators = await generatorsRes.json()
      const loads = await loadsRes.json()
      const substations = await substationsRes.json()
      const balancingAuthorities = await basRes.json()

      set({
        buses,
        branches,
        generators,
        loads,
        substations,
        balancingAuthorities,
        isLoadingGrid: false
      })
    } catch (error) {
      set({
        gridError: error instanceof Error ? error.message : 'An unknown error occurred',
        isLoadingGrid: false
      })
    }
  },

  fetchHeatmapData: async (parameter, date) => {
    set({ isLoadingHeatmap: true, heatmapError: null })

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/public/heatmap?parameter=${parameter}&date=${date}`
      )

      if (!response.ok) {
        throw new Error('Failed to fetch heatmap data')
      }

      const heatmapData = await response.json()

      set({
        heatmapData,
        isLoadingHeatmap: false
      })
    } catch (error) {
      set({
        heatmapError: error instanceof Error ? error.message : 'An unknown error occurred',
        isLoadingHeatmap: false
      })
    }
  },

  fetchComponentWeather: async (componentType, componentId, startDate, endDate) => {
    set({ isLoadingComponentWeather: true, componentWeatherError: null })

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/weather/component/${componentType}/${componentId}?start_date=${startDate}&end_date=${endDate}`
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch weather data for ${componentType} ${componentId}`)
      }

      const componentWeatherData = await response.json()

      set({
        selectedComponentWeather: componentWeatherData,
        isLoadingComponentWeather: false
      })
    } catch (error) {
      set({
        componentWeatherError: error instanceof Error ? error.message : 'An unknown error occurred',
        isLoadingComponentWeather: false
      })
    }
  },

  clearComponentWeather: () => {
    set({ selectedComponentWeather: null })
  },

  clearErrors: () => {
    set({
      gridError: null,
      heatmapError: null,
      componentWeatherError: null
    })
  }
}))
