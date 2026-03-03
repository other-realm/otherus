/**
 * MapField — renders a Leaflet map for web, or a WebView-wrapped Leaflet for native.
 * The user can click/tap to place a marker.
 */
import React, { useRef } from 'react';
import { View, StyleSheet, Platform, Text } from 'react-native';
import { Colors, Radius } from '../../utils/theme';

interface MapFieldProps {
  lat: number;
  lng: number;
  onChange: (lat: number, lng: number) => void;
}

// ── Web implementation using react-leaflet ────────────────────────────────────

let WebMap: React.FC<MapFieldProps> | null = null;

if (Platform.OS === 'web') {
  // Dynamic import to avoid SSR issues
  const { MapContainer, TileLayer, Marker, useMapEvents } = require('react-leaflet');
  require('leaflet/dist/leaflet.css');
  const L = require('leaflet');

  // Fix default marker icon paths for webpack/bundlers
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  });

  function ClickHandler({ onChange }: { onChange: (lat: number, lng: number) => void }) {
    useMapEvents({
      click(e: any) {
        onChange(e.latlng.lat, e.latlng.lng);
      },
    });
    return null;
  }

  WebMap = ({ lat, lng, onChange }: MapFieldProps) => (
    <MapContainer
      center={[lat, lng]}
      zoom={10}
      style={{ height: 300, width: '100%', borderRadius: 12 }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[lat, lng]} />
      <ClickHandler onChange={onChange} />
    </MapContainer>
  );
}

// ── Native implementation using WebView + inline Leaflet HTML ─────────────────

let NativeMap: React.FC<MapFieldProps> | null = null;

if (Platform.OS !== 'web') {
  const { WebView } = require('react-native-webview');

  NativeMap = ({ lat, lng, onChange }: MapFieldProps) => {
    const webviewRef = useRef<any>(null);

    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>body{margin:0;padding:0}#map{height:100vh;width:100vw}</style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([${lat}, ${lng}], 10);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  var marker = L.marker([${lat}, ${lng}]).addTo(map);
  map.on('click', function(e) {
    marker.setLatLng(e.latlng);
    window.ReactNativeWebView.postMessage(JSON.stringify({lat: e.latlng.lat, lng: e.latlng.lng}));
  });
</script>
</body>
</html>`;

    return (
      <WebView
        ref={webviewRef}
        source={{ html }}
        style={styles.nativeMap}
        onMessage={(event: any) => {
          try {
            const data = JSON.parse(event.nativeEvent.data);
            onChange(data.lat, data.lng);
          } catch {}
        }}
        javaScriptEnabled
      />
    );
  };
}

// ── Unified export ─────────────────────────────────────────────────────────────

export default function MapField(props: MapFieldProps) {
  if (Platform.OS === 'web' && WebMap) {
    return (
      <View style={styles.container}>
        <WebMap {...props} />
        <Text style={styles.hint}>Click on the map to set your location</Text>
      </View>
    );
  }
  if (NativeMap) {
    return (
      <View style={styles.container}>
        <NativeMap {...props} />
        <Text style={styles.hint}>Tap on the map to set your location</Text>
      </View>
    );
  }
  return (
    <View style={styles.fallback}>
      <Text style={{ color: Colors.textMuted }}>Map not available</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { borderRadius: Radius.md, overflow: 'hidden' },
  nativeMap: { height: 300, width: '100%' },
  hint: { color: Colors.textMuted, fontSize: 12, marginTop: 4 },
  fallback: {
    height: 200,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: Radius.md,
  },
});
