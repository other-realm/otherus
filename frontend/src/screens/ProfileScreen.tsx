/**
 * ProfileScreen — displays and auto-saves the current user's profile.
 *
 * Auto-save behaviour:
 *   - Every time any form field changes, a 1.5-second debounce timer is reset.
 *   - When the timer fires, the current values are sent to the API.
 *   - A status indicator in the header shows "Saving…", "Saved ✓", or any error.
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuthStore } from '../store/authStore';
import { Colors, Spacing, FontSize } from '../utils/theme';
import DynamicForm from '../components/form/DynamicForm';
import { PROFILE_SCHEMA } from '../utils/profileSchema';
import api from '../services/api';

type SaveStatus = 'idle' | 'pending' | 'saving' | 'saved' | 'error';

const DEBOUNCE_MS = 1500; // 1.5 s after last keystroke before saving

export default function ProfileScreen() {
  const { user } = useAuthStore();
  const [initialValues, setInitialValues] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  // Debounce timer ref — cleared/reset on every change
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Latest values ref — avoids stale closure in the debounced save
  const latestValues = useRef<Record<string, any>>({});

  // ── Load existing profile on mount ─────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/profiles/me');
        const data = res.data?.data ?? {};
        setInitialValues(data);
        latestValues.current = data;
      } catch {
        setInitialValues({});
      } finally {
        setLoading(false);
      }
    };
    load();

    // Cleanup debounce timer on unmount
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, []);

  // ── Persist to API ──────────────────────────────────────────────────────────
  const saveNow = useCallback(async (values: Record<string, any>) => {
    setSaveStatus('saving');
    try {
      await api.put('/profiles/me', { data: values });
      setSaveStatus('saved');
      // Reset to 'idle' after 3 seconds so the indicator fades away
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail ?? 'Save failed');
      setSaveStatus('error');
      // Allow retry after 4 seconds
      setTimeout(() => setSaveStatus('idle'), 4000);
    }
  }, []);

  // ── Debounced onChange handler ──────────────────────────────────────────────
  const handleChange = useCallback(
    (values: Record<string, any>) => {
      latestValues.current = values;
      setSaveStatus('pending');

      if (debounceTimer.current) clearTimeout(debounceTimer.current);
      debounceTimer.current = setTimeout(() => {
        saveNow(latestValues.current);
      }, DEBOUNCE_MS);
    },
    [saveNow]
  );

  // ── Status label ────────────────────────────────────────────────────────────
  const statusLabel = () => {
    switch (saveStatus) {
      case 'pending': return { text: 'Unsaved changes…', color: Colors.textMuted };
      case 'saving':  return { text: 'Saving…',          color: Colors.secondary };
      case 'saved':   return { text: 'Saved ✓',          color: Colors.success };
      case 'error':   return { text: `Error: ${errorMsg}`, color: Colors.error };
      default:        return null;
    }
  };

  const status = statusLabel();

  // ── Render ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <Text style={styles.title}>My Profile</Text>
          {status && (
            <Text style={[styles.statusText, { color: status.color }]}>
              {status.text}
            </Text>
          )}
        </View>
        <Text style={styles.subtitle}>Changes are saved automatically</Text>
      </View>

      {/* Form — no save button; auto-save via onChange */}
      <DynamicForm
        schema={PROFILE_SCHEMA}
        initialValues={initialValues ?? {}}
        onChange={handleChange}
        showSaveButton={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  title: { fontSize: FontSize.xl, fontWeight: '800', color: Colors.text },
  statusText: { fontSize: FontSize.sm, fontWeight: '500' },
  subtitle: { fontSize: FontSize.sm, color: Colors.textMuted, marginTop: 2 },
});
