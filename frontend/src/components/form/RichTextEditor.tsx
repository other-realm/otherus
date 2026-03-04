/**
 * RichTextEditor — WYSIWYG editor using TinyMCE (open-source, community edition)
 * via WebView on native and an iframe on web.
 *
 * Each instance gets a unique channelId so that message-passing between the
 * iframe/WebView and the React host is fully isolated — no cross-editor bleed.
 */
import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { Colors, Radius } from '../../utils/theme';

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  minHeight?: number;
}

// ── TinyMCE HTML template ─────────────────────────────────────────────────────
// Uses TinyMCE 6 open-source CDN (MIT-licensed community build).
// Each instance receives a unique `channelId` that is embedded in every
// postMessage payload, so the React host can ignore messages from other editors.

const buildTinyMCEHtml = (initialValue: string, minHeight: number, channelId: string) => `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
  <style>
    html, body { margin: 0; padding: 0; background: #1A1A2E; height: 100%; }
    #editor-container { width: 100%; min-height: ${minHeight}px; }
    .tox-tinymce { border-color: #2D2D44 !important; border-radius: 6px !important; }
    .tox .tox-toolbar, .tox .tox-toolbar__overflow, .tox .tox-toolbar-overlord {
      background: #2D2D44 !important;
    }
    .tox .tox-edit-area__iframe { background: #1A1A2E !important; }
    .tox .tox-statusbar { background: #2D2D44 !important; border-top-color: #2D2D44 !important; }
  </style>
</head>
<body>
  <textarea id="editor-container"></textarea>
  <script>
    var CHANNEL_ID = ${JSON.stringify(channelId)};
    var lastSent = '';
    var initialValue = ${JSON.stringify(initialValue)};

    tinymce.init({
      selector: '#editor-container',
      height: ${minHeight + 60},
      menubar: false,
      plugins: [
        'advlist', 'autolink', 'lists', 'link', 'charmap',
        'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'table', 'wordcount'
      ],
      toolbar:
        'undo redo | formatselect | bold italic underline strikethrough | ' +
        'alignleft aligncenter alignright alignjustify | ' +
        'bullist numlist outdent indent | link | code | removeformat',
      skin: 'oxide-dark',
      content_css: 'dark',
      content_style:
        'body { font-family: sans-serif; font-size: 14px; color: #FFFFFE; background: #1A1A2E; margin: 8px; }',
      setup: function(editor) {
        editor.on('init', function() {
          editor.setContent(initialValue);
        });
        editor.on('input change keyup', function() {
          var html = editor.getContent();
          if (html !== lastSent) {
            lastSent = html;
            var msg = JSON.stringify({ type: 'change', html: html, channelId: CHANNEL_ID });
            if (window.ReactNativeWebView) {
              window.ReactNativeWebView.postMessage(msg);
            } else {
              window.parent.postMessage(msg, '*');
            }
          }
        });
      }
    });

    // Accept setValue messages only if channelId matches
    function handleIncoming(e) {
      try {
        var data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
        if (data && data.channelId === CHANNEL_ID && data.type === 'setValue') {
          var editor = tinymce.get('editor-container');
          if (editor && editor.getContent() !== data.html) {
            editor.setContent(data.html);
          }
        }
      } catch(err) {}
    }
    window.addEventListener('message', handleIncoming);
    document.addEventListener('message', handleIncoming); // Android WebView
  </script>
</body>
</html>`;

// ── Component ─────────────────────────────────────────────────────────────────

export default function RichTextEditor({
  value,
  onChange,
  minHeight = 150,
}: RichTextEditorProps) {
  // Each mounted instance gets its own stable channel ID for the lifetime of
  // the component. useMemo with [] ensures it never changes on re-render.
  const channelId = useMemo(
    () => `rte-${Math.random().toString(36).slice(2, 10)}`,
    []
  );

  const webviewRef = useRef<any>(null);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  // ── Web (iframe) ────────────────────────────────────────────────────────────
  if (Platform.OS === 'web') {
    // Stable message handler that only reacts to its own channelId
    const handleMessage = useCallback(
      (event: MessageEvent) => {
        try {
          const data =
            typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
          if (data?.channelId === channelId && data?.type === 'change') {
            onChange(data.html);
          }
        } catch {}
      },
      [channelId, onChange]
    );

    useEffect(() => {
      window.addEventListener('message', handleMessage);
      return () => window.removeEventListener('message', handleMessage);
    }, [handleMessage]);

    // Push external value changes into the iframe
    useEffect(() => {
      if (iframeRef.current?.contentWindow) {
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({ type: 'setValue', html: value, channelId }),
          '*'
        );
      }
    }, [value, channelId]);

    return (
      <View style={[styles.container, { minHeight: minHeight + 104 }]}>
        <iframe
          ref={iframeRef}
          srcDoc={buildTinyMCEHtml(value, minHeight, channelId)}
          style={{
            width: '100%',
            height: minHeight + 104,
            border: 'none',
            borderRadius: Radius.sm,
          }}
          // allow-popups is needed for TinyMCE link dialog
          sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"
        />
      </View>
    );
  }

  // ── Native (WebView) ────────────────────────────────────────────────────────
  const { WebView } = require('react-native-webview');

  return (
    <View style={[styles.container, { height: minHeight + 120 }]}>
      <WebView
        ref={webviewRef}
        source={{ html: buildTinyMCEHtml(value, minHeight, channelId) }}
        style={{ flex: 1, backgroundColor: Colors.surface }}
        onMessage={(event: any) => {
          try {
            const data = JSON.parse(event.nativeEvent.data);
            if (data?.channelId === channelId && data?.type === 'change') {
              onChange(data.html);
            }
          } catch {}
        }}
        javaScriptEnabled
        domStorageEnabled
        scrollEnabled={false}
        originWhitelist={['*']}
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
