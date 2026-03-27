/**
 * ReadOnlyMapField — displays a Leaflet map for web, or a WebView-wrapped Leaflet for native.
 * This is a read-only version without click handlers.
 */
import React from 'react';
import { View, StyleSheet, Platform, Text } from 'react-native';
import { Colors, Radius } from '../../utils/theme';

interface ReadOnlyMapFieldProps {
  lat: number;
  lng: number;
}

// ── Web implementation using react-leaflet ────────────────────────────────────

let WebMap: React.FC<ReadOnlyMapFieldProps> | null = null;

if (Platform.OS === 'web') {
  // Dynamic import to avoid SSR issues
  const { MapContainer, TileLayer, Marker } = require('react-leaflet');
  require('leaflet/dist/leaflet.css');
  const L = require('leaflet');

  // Fix default marker icon paths for webpack/bundlers
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  });

  WebMap = ({ lat, lng }: ReadOnlyMapFieldProps) => (
    <MapContainer
      center={[lat, lng]}
      zoom={10}
      style={{ height: 300, width: '100%', borderRadius: 12 }}
      dragging={true}
      zoomControl={true}
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[lat, lng]} />
    </MapContainer>
  );
}

// ── Native implementation using WebView + inline Leaflet HTML ─────────────────

let NativeMap: React.FC<ReadOnlyMapFieldProps> | null = null;

if (Platform.OS !== 'web') {
  const { WebView } = require('react-native-webview');

  NativeMap = ({ lat, lng }: ReadOnlyMapFieldProps) => {
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
</script>
</body>
</html>`;

    return (
      <WebView
        source={{ html }}
        style={styles.nativeMap}
        javaScriptEnabled
        scrollEnabled={false}
      />
    );
  };
}

// ── Unified export ─────────────────────────────────────────────────────────────

export default function ReadOnlyMapField(props: ReadOnlyMapFieldProps) {
  if (Platform.OS === 'web' && WebMap) {
    return (
      <View style={styles.container}>
        <WebMap {...props} />
      </View>
    );
  }
  if (NativeMap) {
    return (
      <View style={styles.container}>
        <NativeMap {...props} />
      </View>
    );
  }
  return (
    <View style={styles.fallback}>
      <Text style={{ color: Colors.textMuted }}>Map not available</Text>
      <Text style={{ color: Colors.textMuted, fontSize: 12, marginTop: 4 }}>
        Location: {props.lat.toFixed(4)}, {props.lng.toFixed(4)}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { borderRadius: Radius.md, overflow: 'hidden' },
  nativeMap: { height: 300, width: '100%' },
  fallback: {
    height: 200,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: Radius.md,
  },
});
