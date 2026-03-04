import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
    View,
    Text,
    TextInput,
    FlatList,
    StyleSheet,
    TouchableOpacity,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import api, { WS_BASE, getToken } from '../services/api';
import { useAuthStore } from '../store/authStore';
interface Message {
    id: string;
    room_id: string;
    sender_id: string;
    sender_name: string;
    sender_avatar?: string;
    content: string;
    created_at: string;
}
export default function ChatRoomScreen() {
    const navigation = useNavigation<any>();
    const route = useRoute<any>();
    const { user } = useAuthStore();
    const { roomId, roomName } = route.params;
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const listRef = useRef<FlatList>(null);

    // Load message history
    useEffect(() => {
        const load = async () => {
            try {
                const res = await api.get(`/chat/rooms/${roomId}/messages`);
                setMessages(res.data ?? []);
            } catch {
                setMessages([]);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [roomId]);

    // Connect WebSocket
    useEffect(() => {
        let ws: WebSocket;
        const connect = async () => {
            const token = await getToken();
            if (!token) return;
            ws = new WebSocket(`${WS_BASE}/chat/ws/${roomId}?token=${token}`);
            ws.onopen = () => console.log('WS connected');
            ws.onmessage = (event) => {
                try {
                    const msg: Message = JSON.parse(event.data);
                    setMessages((prev) => {
                        if (prev.find((m) => m.id === msg.id)) return prev;
                        return [...prev, msg];
                    });
                    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100);
                } catch { }
            };
            ws.onerror = (e) => console.error('WS error', e);
            ws.onclose = () => console.log('WS closed');
            wsRef.current = ws;
        };
        connect();
        return () => {
            ws?.close();
        };
    }, [roomId]);

    const sendMessage = useCallback(async () => {
        const content = input.trim();
        if (!content || sending) return;
        setInput('');
        setSending(true);

        // Try WebSocket first
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ content }));
            setSending(false);
        } else {
            // Fallback to REST
            try {
                const res = await api.post(`/chat/rooms/${roomId}/messages`, { content });
                setMessages((prev) => [...prev, res.data]);
            } catch { }
            setSending(false);
        }
    }, [input, roomId, sending]);

    const renderMessage = ({ item }: { item: Message }) => {
        const isMe = item.sender_id === user?.id;
        return (
            <View style={[styles.msgRow, isMe && styles.msgRowMe]}>
                {!isMe && (
                    <View style={styles.msgAvatar}>
                        <Text style={styles.msgAvatarText}>{item.sender_name[0]?.toUpperCase()}</Text>
                    </View>
                )}
                <View style={[styles.msgBubble, isMe ? styles.msgBubbleMe : styles.msgBubbleOther]}>
                    {!isMe && <Text style={styles.msgSender}>{item.sender_name}</Text>}
                    <Text style={styles.msgContent}>{item.content}</Text>
                    <Text style={styles.msgTime}>
                        {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Text>
                </View>
            </View>
        );
    };

    return (
        <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Text style={styles.backText}>←</Text>
                </TouchableOpacity>
                <Text style={styles.roomName} numberOfLines={1}>{roomName}</Text>
                <View style={{ width: 32 }} />
            </View>

            {/* Messages */}
            {loading ? (
                <View style={styles.center}>
                    <ActivityIndicator size="large" color={Colors.primary} />
                </View>
            ) : (
                <FlatList
                    ref={listRef}
                    data={messages}
                    keyExtractor={(item) => item.id}
                    renderItem={renderMessage}
                    contentContainerStyle={styles.messageList}
                    onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: false })}
                    ListEmptyComponent={
                        <Text style={styles.empty}>No messages yet. Say hello!</Text>
                    }
                />
            )}

            {/* Input */}
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                keyboardVerticalOffset={90}
            >
                <View style={styles.inputRow}>
                    <TextInput
                        style={styles.input}
                        value={input}
                        onChangeText={setInput}
                        placeholder="Type a message…"
                        placeholderTextColor={Colors.textMuted}
                        multiline
                        maxLength={4000}
                        onSubmitEditing={sendMessage}
                    />
                    <TouchableOpacity
                        style={[styles.sendBtn, (!input.trim() || sending) && styles.sendBtnDisabled]}
                        onPress={sendMessage}
                        disabled={!input.trim() || sending}
                    >
                        <Text style={styles.sendBtnText}>↑</Text>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
        gap: Spacing.sm,
    },
    backText: { color: Colors.primary, fontSize: FontSize.xl, width: 32 },
    roomName: { flex: 1, color: Colors.text, fontSize: FontSize.md, fontWeight: '700', textAlign: 'center' },
    messageList: { padding: Spacing.md, paddingBottom: Spacing.sm },
    msgRow: { flexDirection: 'row', marginBottom: Spacing.sm, alignItems: 'flex-end' },
    msgRowMe: { justifyContent: 'flex-end' },
    msgAvatar: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: Colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: Spacing.xs,
    },
    msgAvatarText: { color: Colors.white, fontSize: FontSize.sm, fontWeight: '700' },
    msgBubble: {
        maxWidth: '75%',
        padding: Spacing.sm,
        borderRadius: Radius.md,
    },
    msgBubbleMe: {
        backgroundColor: Colors.primary,
        borderBottomRightRadius: 4,
    },
    msgBubbleOther: {
        backgroundColor: Colors.surface,
        borderBottomLeftRadius: 4,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    msgSender: { color: Colors.textMuted, fontSize: FontSize.xs, fontWeight: '600', marginBottom: 2 },
    msgContent: { color: Colors.text, fontSize: FontSize.md, lineHeight: 20 },
    msgTime: { color: 'rgba(255,255,255,0.5)', fontSize: FontSize.xs, marginTop: 2, textAlign: 'right' },
    empty: { color: Colors.textMuted, textAlign: 'center', marginTop: Spacing.xl },
    inputRow: {
        flexDirection: 'row',
        padding: Spacing.sm,
        borderTopWidth: 1,
        borderTopColor: Colors.border,
        backgroundColor: Colors.surface,
        alignItems: 'flex-end',
        gap: Spacing.sm,
    },
    input: {
        flex: 1,
        backgroundColor: Colors.background,
        borderWidth: 1,
        borderColor: Colors.border,
        borderRadius: Radius.lg,
        color: Colors.text,
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        fontSize: FontSize.md,
        maxHeight: 120,
    },
    sendBtn: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: Colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
    },
    sendBtnDisabled: { opacity: 0.4 },
    sendBtnText: { color: Colors.white, fontSize: FontSize.xl, fontWeight: '700' },
});
