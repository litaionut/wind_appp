import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { TurbinePosition } from "../api";

type Props = {
  turbines: TurbinePosition[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onMove: (id: string, x: number, y: number) => void;
};

export function LayoutMap({ turbines, selectedId, onSelect, onMove }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current, {
      crs: L.CRS.Simple,
      minZoom: -5,
      maxZoom: 4,
      attributionControl: false,
    });
    mapRef.current = map;
    layerRef.current = L.layerGroup().addTo(map);
    return () => {
      map.remove();
      mapRef.current = null;
      layerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    layer.clearLayers();

    if (!turbines.length) {
      map.setView([0, 0], 0);
      return;
    }

    const bounds = L.latLngBounds([]);
    for (const t of turbines) {
      // Leaflet Simple CRS: lat=y, lng=x
      const latlng = L.latLng(t.y, t.x);
      bounds.extend(latlng);
      const marker = L.circleMarker(latlng, {
        radius: selectedId === t.id ? 10 : 7,
        color: selectedId === t.id ? "#0f3f48" : "#1f6f7a",
        weight: 2,
        fillColor: selectedId === t.id ? "#1f6f7a" : "#e8f2f0",
        fillOpacity: 0.95,
      });
      marker.bindTooltip(t.label, { permanent: false, direction: "top" });
      marker.on("click", () => onSelect(t.id));
      marker.on("mousedown", () => {
        map.dragging.disable();
        const onMoveDoc = (ev: MouseEvent) => {
          const p = map.mouseEventToLatLng(ev);
          marker.setLatLng(p);
        };
        const onUp = (ev: MouseEvent) => {
          document.removeEventListener("mousemove", onMoveDoc);
          document.removeEventListener("mouseup", onUp);
          map.dragging.enable();
          const p = map.mouseEventToLatLng(ev);
          onMove(t.id, p.lng, p.lat);
        };
        document.addEventListener("mousemove", onMoveDoc);
        document.addEventListener("mouseup", onUp);
      });
      marker.addTo(layer);
    }
    map.fitBounds(bounds.pad(0.25));
  }, [turbines, selectedId, onSelect, onMove]);

  return <div className="layout-map" ref={containerRef} role="img" aria-label="Turbine layout map" />;
}
