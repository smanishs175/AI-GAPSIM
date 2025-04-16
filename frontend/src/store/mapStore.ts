import { create } from 'zustand'

export type HeatmapType = 'temperature' | 'humidity' | 'wind_speed' | 'precipitation' | 'radiation'

export interface MapState {
  // Map view settings
  center: [number, number]
  zoom: number

  // Date range
  startDate: string
  endDate: string
  currentDate: string

  // Layer visibility
  showBuses: boolean
  showBranches: boolean
  showGenerators: boolean
  showLoads: boolean
  showSubstations: boolean
  showBalancingAuthorities: boolean
  showHeatmap: boolean

  // Heatmap settings
  heatmapType: HeatmapType

  // Selected component
  selectedComponentType: string | null
  selectedComponentId: number | null

  // Actions
  setCenter: (center: [number, number]) => void
  setZoom: (zoom: number) => void
  setDateRange: (startDate: string, endDate: string) => void
  setCurrentDate: (date: string) => void
  toggleLayer: (layer: string, value?: boolean) => void
  setHeatmapType: (type: HeatmapType) => void
  selectComponent: (type: string, id: number) => void
  clearSelection: () => void
}

export const useMapStore = create<MapState>((set) => ({
  // Default map view centered on WECC region
  center: [40, -115],
  zoom: 5,

  // Default date range (one week)
  startDate: '2020-07-21',
  endDate: '2020-07-30',
  currentDate: '2020-07-21',

  // Default layer visibility
  showBuses: false,
  showBranches: true,
  showGenerators: true,
  showLoads: false,
  showSubstations: true,
  showBalancingAuthorities: true,
  showHeatmap: true,

  // Default heatmap type
  heatmapType: 'temperature',

  // Selected component
  selectedComponentType: null,
  selectedComponentId: null,

  // Actions
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),

  setDateRange: (startDate, endDate) => {
    let currentDate = '';
    set(state => {
      currentDate = state.currentDate;
      return {};
    });

    // Reset current date to start date if it's outside the new range
    if (currentDate < startDate) currentDate = startDate;
    if (currentDate > endDate) currentDate = endDate;

    set({
      startDate,
      endDate,
      currentDate
    });
  },

  setCurrentDate: (date) => set({ currentDate: date }),

  toggleLayer: (layer, value) => {
    switch (layer) {
      case 'buses':
        return set((state) => ({ showBuses: value !== undefined ? value : !state.showBuses }))
      case 'branches':
        return set((state) => ({ showBranches: value !== undefined ? value : !state.showBranches }))
      case 'generators':
        return set((state) => ({ showGenerators: value !== undefined ? value : !state.showGenerators }))
      case 'loads':
        return set((state) => ({ showLoads: value !== undefined ? value : !state.showLoads }))
      case 'substations':
        return set((state) => ({ showSubstations: value !== undefined ? value : !state.showSubstations }))
      case 'balancingAuthorities':
        return set((state) => ({ showBalancingAuthorities: value !== undefined ? value : !state.showBalancingAuthorities }))
      case 'heatmap':
        return set((state) => ({ showHeatmap: value !== undefined ? value : !state.showHeatmap }))
      default:
        return
    }
  },

  setHeatmapType: (type) => set({ heatmapType: type }),

  selectComponent: (type, id) => set({
    selectedComponentType: type,
    selectedComponentId: id
  }),

  clearSelection: () => set({
    selectedComponentType: null,
    selectedComponentId: null
  })
}))
