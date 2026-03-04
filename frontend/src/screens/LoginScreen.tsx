import React, { useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Image,
    Platform,
    Linking,
} from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useNavigation } from '@react-navigation/native';
import { Button } from '../components/shared/Button';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { useAuthStore } from '../store/authStore';
import { API_BASE } from '../services/api';
WebBrowser.maybeCompleteAuthSession();
export default function LoginScreen() {
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();
    useEffect(() => {
        if (user) {
            navigation.replace('Main');
        }
    }, [user]);
    const handleGoogleLogin = async () => {
        const url = `${API_BASE}/auth/google/login`;
        if (Platform.OS === 'web') {
            window.location.href = url;
        } else {
            await WebBrowser.openBrowserAsync(url);
        }
    };
    const handleGitHubLogin = async () => {
        const url = `${API_BASE}/auth/github/login`;
        if (Platform.OS === 'web') {
            window.location.href = url;
        } else {
            await WebBrowser.openBrowserAsync(url);
        }
    };F
    return (
        <View style={styles.container}>
            <View style={styles.hero}>
                <Text style={styles.logo}>⟁</Text>
                <Text style={styles.title}>Other Us</Text>
                <Text style={styles.subtitle}>
                    A community for exploring consciousness,{'\n'}
                    intentional living, and collaborative research.
                </Text>
            </View>
            <View style={styles.authBox}>
                <Text style={styles.authTitle}>Sign in to continue</Text>
                <Button
                    title="Continue with Google"
                    onPress={handleGoogleLogin}
                    style={styles.googleBtn}
                />
                <View style={styles.divider}>
                    <View style={styles.dividerLine} />
                    <Text style={styles.dividerText}>or</Text>
                    <View style={styles.dividerLine} />
                </View>
                <Button
                    title="Continue with GitHub"
                    onPress={handleGitHubLogin}
                    variant="outline"
                    style={styles.githubBtn}
                />
                <Text style={styles.disclaimer}>
                    By signing in, you agree to our Terms of Service and Privacy Policy.
                </Text>
            </View>
        </View>
    );
}
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        alignItems: 'center',
        justifyContent: 'center',
        padding: Spacing.xl,
    },
    hero: {
        alignItems: 'center',
        marginBottom: Spacing.xxl,
    },
    logo: {
        fontSize: 72,
        marginBottom: Spacing.md,
    },
    title: {
        fontSize: FontSize.xxxl,
        fontWeight: '800',
        color: Colors.text,
        letterSpacing: 1,
    },
    subtitle: {
        fontSize: FontSize.md,
        color: Colors.textMuted,
        textAlign: 'center',
        marginTop: Spacing.sm,
        lineHeight: 22,
    },
    authBox: {
        width: '100%',
        maxWidth: 400,
        backgroundColor: Colors.surface,
        borderRadius: Radius.lg,
        padding: Spacing.xl,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    authTitle: {
        fontSize: FontSize.lg,
        fontWeight: '700',
        color: Colors.text,
        marginBottom: Spacing.lg,
        textAlign: 'center',
    },
    googleBtn: {
        backgroundColor: '#4285F4',
        marginBottom: Spacing.sm,
    },
    githubBtn: {
        marginBottom: Spacing.sm,
    },
    divider: {
        flexDirection: 'row',
        alignItems: 'center',
        marginVertical: Spacing.sm,
    },
    dividerLine: {
        flex: 1,
        height: 1,
        backgroundColor: Colors.border,
    },
    dividerText: {
        color: Colors.textMuted,
        marginHorizontal: Spacing.sm,
        fontSize: FontSize.sm,
    },
    disclaimer: {
        fontSize: FontSize.xs,
        color: Colors.textMuted,
        textAlign: 'center',
        marginTop: Spacing.md,
        lineHeight: 16,
    },
});
