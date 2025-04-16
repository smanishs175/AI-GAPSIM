declare module 'leaflet.heat' {
  import * as L from 'leaflet';

  interface HeatLayerOptions {
    minOpacity?: number;
    maxZoom?: number;
    max?: number;
    radius?: number;
    blur?: number;
    gradient?: Record<number, string>;
  }

  namespace L {
    function heatLayer(
      latlngs: L.LatLngExpression[],
      options?: HeatLayerOptions
    ): L.Layer;
  }
}
