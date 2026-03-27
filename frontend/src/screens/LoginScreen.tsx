import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Linking,
    TextInput,
    TouchableOpacity,
    ScrollView,
    Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Button } from '../components/shared/Button';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { useAuthStore } from '../store/authStore';
import { API_BASE } from '../services/api';

export default function LoginScreen() {
    const navigation = useNavigation<any>();
    const { user, isLoading, error, loginWithEmail, registerWithEmail } = useAuthStore();
    const [isRegisterMode, setIsRegisterMode] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [showEmailForm, setShowEmailForm] = useState(false);

    useEffect(() => {
        if (user) {
            navigation.replace('Main');
        }
    }, [user]);

    const handleEmailAuth = async () => {
        if (!email || !password || (isRegisterMode && !name)) {
            Alert.alert('Error', 'Please fill in all fields');
            return;
        }
        try {
            if (isRegisterMode) {
                await registerWithEmail(email, password, name);
            } else {
                await loginWithEmail(email, password);
            }
        } catch (err: any) {
            Alert.alert('Error', err.message || 'Authentication failed');
        }
    };
    const handleGoogleLogin = async () => {
        const url = `${API_BASE}/auth/google/login`;
        if (typeof window !== 'undefined' && window.location) {
            window.location.href = url;
        } else {
            await Linking.openURL(url);
        }
    };
    const handleGitHubLogin = async () => {
        const url = `${API_BASE}/auth/github/login`;
        if (typeof window !== 'undefined' && window.location) {
            window.location.href = url;
        } else {
            await Linking.openURL(url);
        }
    };
    const toggleMode = () => {
        setIsRegisterMode(!isRegisterMode);
        setEmail('');
        setPassword('');
        setName('');
    };
    const toggleEmailForm = () => {
        setShowEmailForm(!showEmailForm);
        setEmail('');
        setPassword('');
        setName('');
        setIsRegisterMode(false);
    };
    return (
        <ScrollView contentContainerStyle={styles.container}>
            <View style={styles.hero}>
                <Text style={styles.logo}>⟁</Text>
                <Text style={styles.title}>Other Us</Text>
                <Text style={styles.subtitle}>
                    A community for exploring collaborative research.
                </Text>
            </View>
            <View style={styles.authBox}>
                <Text style={styles.authTitle}>
                    {showEmailForm
                        ? (isRegisterMode ? 'Create Account' : 'Sign In')
                        : 'Get Started!'}
                </Text>
                {showEmailForm ? (
                    <>
                        {isRegisterMode && (
                            <TextInput
                                style={styles.input}
                                placeholder="Full Name"
                                placeholderTextColor={Colors.textMuted}
                                value={name}
                                onChangeText={setName}
                                autoCapitalize="words"
                            />
                        )}
                        <TextInput
                            style={styles.input}
                            placeholder="Email"
                            placeholderTextColor={Colors.textMuted}
                            value={email}
                            onChangeText={setEmail}
                            autoCapitalize="none"
                            keyboardType="email-address"
                        />
                        <TextInput
                            style={styles.input}
                            placeholder="Password"
                            placeholderTextColor={Colors.textMuted}
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />
                        {error && <Text style={styles.errorText}>{error}</Text>}
                        <Button
                            title={isRegisterMode ? 'Create Account' : 'Sign In'}
                            onPress={handleEmailAuth}
                            loading={isLoading}
                            style={styles.emailBtn}
                        />
                        <TouchableOpacity onPress={toggleMode}>
                            <Text style={styles.toggleText}>
                                {isRegisterMode
                                    ? 'Already have an account? Sign In'
                                    : "Don't have an account? Sign Up"}
                            </Text>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={toggleEmailForm} style={styles.backButton}>
                            <Text style={styles.backText}>← Back to options</Text>
                        </TouchableOpacity>
                    </>
                ) : (
                    <>
                        <Button
                            title="Continue with Email"
                            onPress={toggleEmailForm}
                            style={styles.emailBtn}
                        />
                        <View style={styles.divider}>
                            <View style={styles.dividerLine} />
                            <Text style={styles.dividerText}>or</Text>
                            <View style={styles.dividerLine} />
                        </View>
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
                    </>
                )}

                <Text style={styles.disclaimer}>
                    By signing in, you agree to our Terms of Service and Privacy Policy.
                </Text>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
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
    input: {
        backgroundColor: Colors.background,
        borderWidth: 1,
        borderColor: Colors.border,
        borderRadius: Radius.md,
        padding: Spacing.md,
        marginBottom: Spacing.md,
        fontSize: FontSize.md,
        color: Colors.text,
    },
    emailBtn: {
        backgroundColor: '#890909',
        marginBottom: Spacing.sm,
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
    toggleText: {
        color: Colors.primary,
        textAlign: 'center',
        marginTop: Spacing.md,
        fontSize: FontSize.sm,
    },
    backButton: {
        marginTop: Spacing.md,
        alignItems: 'center',
    },
    backText: {
        color: Colors.textMuted,
        fontSize: FontSize.sm,
    },
    errorText: {
        color: Colors.error,
        fontSize: FontSize.sm,
        marginBottom: Spacing.sm,
        textAlign: 'center',
    },
    disclaimer: {
        fontSize: FontSize.xs,
        color: Colors.textMuted,
        textAlign: 'center',
        marginTop: Spacing.md,
        lineHeight: 16,
    },
});
