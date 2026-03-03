import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useAuthStore } from '../store/authStore';
import { Colors } from '../utils/theme';
import api from '../services/api';
export default function AuthCallbackScreen() {
    const navigation = useNavigation<any>();
    const route = useRoute<any>();
    const { setAuth } = useAuthStore();
    useEffect(() => {
        const handleCallback = async () => {
            try {
                // Token arrives as a query param: /auth-callback?token=...
                let token: string | null = null;

                if (typeof window !== 'undefined') {
                    const params = new URLSearchParams(window.location.search);
                    token = params.get('token');
                } else if (route.params?.token) {
                    token = route.params.token;
                }

                if (!token) {
                    navigation.replace('Login');
                    return;
                }

                // Fetch user info with the token
                const res = await api.get('/auth/me', {
                    headers: { Authorization: `Bearer ${token}` },
                });

                await setAuth(token, res.data);
                navigation.replace('Main');
            } catch (err) {
                console.error('Auth callback error:', err);
                navigation.replace('Login');
            }
        };

        handleCallback();
    }, []);

    return (
        <View style={styles.container}>
            <ActivityIndicator size="large" color={Colors.primary} />
            <Text style={styles.text}>Signing you in…</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
    },
    text: {
        color: Colors.textMuted,
        fontSize: 16,
    },
});
