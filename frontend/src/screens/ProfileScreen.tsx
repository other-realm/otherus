import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuthStore } from '../store/authStore';
import { Colors, Spacing, FontSize } from '../utils/theme';
import DynamicForm from '../components/form/DynamicForm';
import { PROFILE_SCHEMA } from '../utils/profileSchema';
import api from '../services/api';

export default function ProfileScreen() {
  const { user } = useAuthStore();
  const [initialValues, setInitialValues] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/profiles/me');
        setInitialValues(res.data?.data ?? {});
      } catch {
        setInitialValues({});
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSubmit = async (values: Record<string, any>) => {
    setSaving(true);
    try {
      await api.put('/profiles/me', { data: values });
      Alert.alert('Saved', 'Your profile has been updated.');
    } catch (err: any) {
      Alert.alert('Error', err?.response?.data?.detail ?? 'Failed to save profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>My Profile</Text>
        {user?.avatar_url ? null : null}
        <Text style={styles.subtitle}>Tell the community about yourself</Text>
      </View>
      <DynamicForm
        schema={PROFILE_SCHEMA}
        initialValues={initialValues ?? {}}
        onSubmit={handleSubmit}
        loading={saving}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: { flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' },
  header: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: { fontSize: FontSize.xl, fontWeight: '800', color: Colors.text },
  subtitle: { fontSize: FontSize.sm, color: Colors.textMuted, marginTop: 2 },
});
