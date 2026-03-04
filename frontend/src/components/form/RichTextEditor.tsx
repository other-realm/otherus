/**
 * RichTextEditor — WYSIWYG editor using Quill.js via WebView on native,
 * and a contentEditable div with Quill on web.
 */
import React, { useRef, useEffect } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { Colors, Radius } from '../../utils/theme';

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  minHeight?: number;
}
const QUILL_HTML = (initialValue: string, minHeight: number) => `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.quilljs.com/1.3.7/quill.snow.css" rel="stylesheet">
  <script src="https://cdn.quilljs.com/1.3.7/quill.js"></script>
  <style>
    body { margin: 0; background: #1A1A2E; color: #FFFFFE; font-family: sans-serif; }
    .ql-toolbar { background: #2D2D44; border-color: #2D2D44 !important; }
    .ql-toolbar .ql-stroke { stroke: #A7A9BE; }
    .ql-toolbar .ql-fill { fill: #A7A9BE; }
    .ql-toolbar .ql-picker { color: #A7A9BE; }
    .ql-container { background: #1A1A2E; border-color: #2D2D44 !important; min-height: ${minHeight}px; }
    .ql-editor { color: #FFFFFE; min-height: ${minHeight}px; }
  </style>
</head>
<body>
<div id="editor"></div>
<script>
  var quill = new Quill('#editor', { theme: 'snow' });
  quill.root.innerHTML = ${JSON.stringify(initialValue)};
  quill.on('text-change', function() {
    var html = quill.root.innerHTML;
    if (window.ReactNativeWebView) {
      window.ReactNativeWebView.postMessage(JSON.stringify({ type: 'change', html: html }));
    } else {
      window.parent.postMessage(JSON.stringify({ type: 'change', html: html }), '*');
    }
  });
  // Listen for external value updates
  window.addEventListener('message', function(e) {
    try {
      var data = JSON.parse(e.data);
      if (data.type === 'setValue') {
        quill.root.innerHTML = data.html;
      }
    } catch(err) {}
  });
</script>
</body>
</html>`;
export default function RichTextEditor({
  value,
  onChange,
  minHeight = 150,
}: RichTextEditorProps) {
  const webviewRef = useRef<any>(null);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  if (Platform.OS === 'web') {
    // Web: render an iframe with Quill
    useEffect(() => {
      const handleMessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'change') {
            onChange(data.html);
          }
        } catch {}
      };
      window.addEventListener('message', handleMessage);
      return () => window.removeEventListener('message', handleMessage);
    }, [onChange]);
    return (
      <View style={[styles.container, { minHeight: minHeight + 44 }]}>
        <iframe
          ref={iframeRef}
          srcDoc={QUILL_HTML(value, minHeight)}
          style={{
            width: '100%',
            minHeight: minHeight + 44,
            border: 'none',
            borderRadius: Radius.sm,
          }}
          sandbox="allow-scripts allow-same-origin"
        />
      </View>
    );
  }

  // Native: use WebView
  const { WebView } = require('react-native-webview');

  return (
    <View style={[styles.container, { height: minHeight + 80 }]}>
      <WebView
        ref={webviewRef}
        source={{ html: QUILL_HTML(value, minHeight) }}
        style={{ flex: 1, backgroundColor: Colors.surface }}
        onMessage={(event: any) => {
          try {
            const data = JSON.parse(event.nativeEvent.data);
            if (data.type === 'change') {
              onChange(data.html);
            }
          } catch {}
        }}
        javaScriptEnabled
        domStorageEnabled
        scrollEnabled={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: Radius.sm,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
});
