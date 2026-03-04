/**
 * ProfileDetailScreen — displays a specific user's profile with all their data.
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import api from '../services/api';
import { Card } from '../components/shared/Card';

interface Profile {
  user_id: string;
  user_name: string;
  avatar_url?: string;
  data: Record<string, any>;
  updated_at: string;
}

export default function ProfileDetailScreen() {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { userId } = route.params;

  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const res = await api.get(`/profiles/${userId}`);
        setProfile(res.data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load profile');
        setProfile(null);
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [userId]);

  const handleMessage = async () => {
    if (!profile) return;
    try {
      // Create a DM room with this user
      const res = await api.post('/chat/rooms', {
        type: 'dm',
        member_ids: [profile.user_id],
      });
      const roomId = res.data.id;
      navigation.navigate('ChatRoom', { roomId });
    } catch (err) {
      console.error('Failed to create chat room:', err);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  if (error || !profile) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Text style={styles.backButton}>← Back</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.center}>
          <Text style={styles.errorText}>{error || 'Profile not found'}</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Avatar & Name */}
        <View style={styles.profileHeader}>
          {profile.avatar_url ? (
            <Image source={{ uri: profile.avatar_url }} style={styles.avatar} />
          ) : (
            <View style={styles.avatarFallback}>
              <Text style={styles.avatarInitial}>{profile.user_name[0]?.toUpperCase()}</Text>
            </View>
          )}
          <Text style={styles.name}>{profile.user_name}</Text>
          <Text style={styles.updated}>Updated: {new Date(profile.updated_at).toLocaleDateString()}</Text>
        </View>

        {/* Message Button */}
        <TouchableOpacity style={styles.messageButton} onPress={handleMessage}>
          <Text style={styles.messageButtonText}>Send Message</Text>
        </TouchableOpacity>

        {/* Profile Data */}
        {Object.entries(profile.data).map(([key, value]) => (
          <Card key={key} style={styles.dataCard}>
            <Text style={styles.dataKey}>{key.replace(/_/g, ' ').toUpperCase()}</Text>
            {typeof value === 'string' ? (
              <Text style={styles.dataValue}>{value.replace(/<[^>]+>/g, '')}</Text>
            ) : typeof value === 'object' ? (
              <View>
                {value.items ? (
                  Object.entries(value.items).map(([itemKey, itemValue]: [string, any]) => (
                    <View key={itemKey} style={styles.dataItem}>
                      <Text style={styles.itemLabel}>{itemValue.label || itemKey}</Text>
                      <Text style={styles.itemValue}>
                        {typeof itemValue === 'object' ? itemValue.value ?? 'N/A' : itemValue}
                      </Text>
                    </View>
                  ))
                ) : (
                  <Text style={styles.dataValue}>{JSON.stringify(value, null, 2)}</Text>
                )}
              </View>
            ) : (
              <Text style={styles.dataValue}>{String(value)}</Text>
            )}
          </Card>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    color: Colors.primary,
    fontSize: FontSize.md,
    fontWeight: '600',
  },
  content: { flex: 1 },
  contentContainer: { padding: Spacing.md, paddingBottom: Spacing.xl },
  profileHeader: {
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  avatar: { width: 80, height: 80, borderRadius: 40, marginBottom: Spacing.md },
  avatarFallback: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  avatarInitial: { color: Colors.white, fontSize: FontSize.xl, fontWeight: '700' },
  name: { fontSize: FontSize.xl, fontWeight: '700', color: Colors.text, textAlign: 'center' },
  updated: { fontSize: FontSize.sm, color: Colors.textMuted, marginTop: Spacing.xs },
  messageButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: Radius.md,
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  messageButtonText: { color: Colors.white, fontSize: FontSize.md, fontWeight: '600' },
  dataCard: { marginBottom: Spacing.md },
  dataKey: { fontSize: FontSize.md, fontWeight: '700', color: Colors.primary, marginBottom: Spacing.sm },
  dataValue: { fontSize: FontSize.md, color: Colors.text, lineHeight: 20 },
  dataItem: { marginBottom: Spacing.sm, paddingBottom: Spacing.sm, borderBottomWidth: 1, borderBottomColor: Colors.border },
  itemLabel: { fontSize: FontSize.sm, fontWeight: '600', color: Colors.textMuted },
  itemValue: { fontSize: FontSize.md, color: Colors.text, marginTop: Spacing.xs },
  errorText: { fontSize: FontSize.md, color: Colors.error, textAlign: 'center' },
});
