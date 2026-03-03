import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  Image,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { Button } from '../components/shared/Button';
import { Card } from '../components/shared/Card';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';

export default function SettingsScreen() {
  const navigation = useNavigation<any>();
  const { user, logout } = useAuthStore();
  const [ntfyTopic, setNtfyTopic] = useState(user?.ntfy_topic ?? '');
  const [savingNtfy, setSavingNtfy] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  const handleSaveNtfy = async () => {
    setSavingNtfy(true);
    try {
      await api.put('/users/me/ntfy', { ntfy_topic: ntfyTopic });
      Alert.alert('Saved', 'Push notification topic updated.');
    } catch {
      Alert.alert('Error', 'Failed to update notification topic.');
    } finally {
      setSavingNtfy(false);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      '⚠️ Delete Account',
      'This action is permanent and cannot be undone. All your profile data, messages, and account information will be permanently deleted. Are you absolutely sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Yes, Delete My Account',
          style: 'destructive',
          onPress: confirmDelete,
        },
      ]
    );
  };

  const confirmDelete = async () => {
    setDeletingAccount(true);
    try {
      await api.delete('/profiles/me');
      await logout();
    } catch (err: any) {
      Alert.alert('Error', err?.response?.data?.detail ?? 'Failed to delete account.');
      setDeletingAccount(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Profile summary */}
        <Card style={styles.profileCard}>
          <View style={styles.profileRow}>
            {user?.avatar_url ? (
              <Image source={{ uri: user.avatar_url }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarFallback}>
                <Text style={styles.avatarInitial}>{user?.name?.[0]?.toUpperCase()}</Text>
              </View>
            )}
            <View>
              <Text style={styles.userName}>{user?.name}</Text>
              <Text style={styles.userEmail}>{user?.email}</Text>
              <Text style={styles.userProvider}>via {user?.provider}</Text>
            </View>
          </View>
        </Card>

        {/* Push notifications */}
        <Text style={styles.sectionTitle}>Push Notifications (ntfy.sh)</Text>
        <Card>
          <Text style={styles.ntfyDescription}>
            Subscribe to your personal ntfy.sh topic to receive chat notifications when you're offline.
            Install the ntfy app and subscribe to the topic below.
          </Text>
          <Text style={styles.label}>Your ntfy topic</Text>
          <TextInput
            style={styles.input}
            value={ntfyTopic}
            onChangeText={setNtfyTopic}
            placeholder="other-us-xxxxxxxx"
            placeholderTextColor={Colors.textMuted}
            autoCapitalize="none"
          />
          <Button
            title="Save Notification Topic"
            onPress={handleSaveNtfy}
            loading={savingNtfy}
            variant="outline"
            style={{ marginTop: Spacing.sm }}
          />
        </Card>

        {/* Sign out */}
        <Text style={styles.sectionTitle}>Account</Text>
        <Card>
          <Button
            title="Sign Out"
            onPress={handleLogout}
            variant="outline"
          />
        </Card>

        {/* Delete account */}
        <Text style={[styles.sectionTitle, { color: Colors.error }]}>Danger Zone</Text>
        <Card style={styles.dangerCard}>
          <Text style={styles.dangerText}>
            Permanently delete your account and all associated data. This action cannot be undone.
          </Text>
          <Button
            title="Delete My Account"
            onPress={handleDeleteAccount}
            variant="danger"
            loading={deletingAccount}
            style={{ marginTop: Spacing.md }}
          />
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: { fontSize: FontSize.xl, fontWeight: '800', color: Colors.text },
  content: { padding: Spacing.md, paddingBottom: Spacing.xxl },
  profileCard: { marginBottom: Spacing.lg },
  profileRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  avatar: { width: 56, height: 56, borderRadius: 28 },
  avatarFallback: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInitial: { color: Colors.white, fontSize: FontSize.xl, fontWeight: '700' },
  userName: { color: Colors.text, fontSize: FontSize.md, fontWeight: '700' },
  userEmail: { color: Colors.textMuted, fontSize: FontSize.sm },
  userProvider: { color: Colors.textMuted, fontSize: FontSize.xs, marginTop: 2 },
  sectionTitle: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: Spacing.sm,
    marginTop: Spacing.md,
  },
  ntfyDescription: { color: Colors.textMuted, fontSize: FontSize.sm, marginBottom: Spacing.md, lineHeight: 20 },
  label: { color: Colors.text, fontSize: FontSize.sm, fontWeight: '600', marginBottom: Spacing.xs },
  input: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.sm,
    color: Colors.text,
    padding: Spacing.sm + 2,
    fontSize: FontSize.md,
  },
  dangerCard: { borderColor: Colors.error },
  dangerText: { color: Colors.textMuted, fontSize: FontSize.sm, lineHeight: 20 },
});
