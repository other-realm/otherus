import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { Card } from '../components/shared/Card';
import { Button } from '../components/shared/Button';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';

interface Room {
  id: string;
  type: string;
  name: string;
  members: string[];
  created_at: string;
  last_message?: {
    sender_name: string;
    content: string;
    created_at: string;
  };
}

export default function ChatListScreen() {
  const navigation = useNavigation<any>();
  const { user } = useAuthStore();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await api.get('/chat/rooms');
      setRooms(res.data ?? []);
    } catch {
      setRooms([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const createGroupChat = async () => {
    try {
      const usersRes = await api.get('/users/');
      const others = (usersRes.data as any[]).filter((u) => u.id !== user?.id);
      if (others.length === 0) {
        Alert.alert('No other members', 'There are no other members to chat with yet.');
        return;
      }
      const res = await api.post('/chat/rooms', {
        type: 'group',
        name: 'Community Chat',
        member_ids: others.map((u) => u.id),
      });
      navigation.navigate('ChatRoom', { roomId: res.data.id, roomName: res.data.name });
    } catch (err: any) {
      Alert.alert('Error', 'Could not create group chat.');
    }
  };

  const renderRoom = ({ item }: { item: Room }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('ChatRoom', { roomId: item.id, roomName: item.name })}
    >
      <Card style={styles.roomCard}>
        <View style={styles.roomRow}>
          <View style={styles.roomIcon}>
            <Text style={styles.roomIconText}>{item.type === 'group' ? '👥' : '💬'}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.roomName}>{item.name}</Text>
            {item.last_message ? (
              <Text style={styles.lastMessage} numberOfLines={1}>
                <Text style={{ fontWeight: '600' }}>{item.last_message.sender_name}: </Text>
                {item.last_message.content}
              </Text>
            ) : (
              <Text style={styles.lastMessage}>No messages yet</Text>
            )}
          </View>
          {item.last_message && (
            <Text style={styles.time}>
              {new Date(item.last_message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Text>
          )}
        </View>
      </Card>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Messages</Text>
        <Button
          title="Group Chat"
          onPress={createGroupChat}
          variant="outline"
          style={styles.newBtn}
        />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      ) : (
        <FlatList
          data={rooms}
          keyExtractor={(item) => item.id}
          renderItem={renderRoom}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.empty}>No conversations yet.</Text>
              <Text style={styles.emptySub}>Start a group chat or message a community member from their profile.</Text>
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: { fontSize: FontSize.xl, fontWeight: '800', color: Colors.text },
  newBtn: { paddingVertical: Spacing.xs, paddingHorizontal: Spacing.md, minHeight: 36 },
  list: { padding: Spacing.md, paddingTop: Spacing.sm },
  roomCard: { marginBottom: Spacing.sm, paddingVertical: Spacing.sm + 2 },
  roomRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  roomIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.surfaceAlt,
    alignItems: 'center',
    justifyContent: 'center',
  },
  roomIconText: { fontSize: 20 },
  roomName: { color: Colors.text, fontSize: FontSize.md, fontWeight: '600' },
  lastMessage: { color: Colors.textMuted, fontSize: FontSize.sm, marginTop: 2 },
  time: { color: Colors.textMuted, fontSize: FontSize.xs },
  emptyContainer: { alignItems: 'center', paddingTop: Spacing.xxl, paddingHorizontal: Spacing.xl },
  empty: { color: Colors.textMuted, fontSize: FontSize.md, textAlign: 'center' },
  emptySub: { color: Colors.textMuted, fontSize: FontSize.sm, textAlign: 'center', marginTop: Spacing.sm },
});
