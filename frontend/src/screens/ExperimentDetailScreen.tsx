import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/shared/Button';

interface Experiment {
    id: string;
    title: string;
    content: string;
    status: string;
    tags: string[];
    created_at: string;
    updated_at: string;
}

export default function ExperimentDetailScreen() {
    const navigation = useNavigation<any>();
    const route = useRoute<any>();
    const { user } = useAuthStore();
    const { experimentId } = route.params;
    const [experiment, setExperiment] = useState<Experiment | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await api.get(`/experiments/${experimentId}`);
                setExperiment(res.data);
            } catch {
                setExperiment(null);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [experimentId]);

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color={Colors.primary} />
            </View>
        );
    }

    if (!experiment) {
        return (
            <View style={styles.center}>
                <Text style={styles.error}>Experiment not found.</Text>
            </View>
        );
    }

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Text style={styles.backText}>← Back</Text>
                </TouchableOpacity>
                {user?.is_admin && (
                    <Button
                        title="Edit"
                        onPress={() => navigation.navigate('ExperimentEditor', { experimentId: experiment.id })}
                        variant="outline"
                        style={styles.editBtn}
                    />
                )}
            </View>

            <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
                <Text style={styles.title}>{experiment.title}</Text>
                <View style={styles.meta}>
                    <View style={[styles.badge, experiment.status === 'active' ? styles.badgeActive : styles.badgeCompleted]}>
                        <Text style={styles.badgeText}>{experiment.status}</Text>
                    </View>
                    <Text style={styles.date}>
                        Updated {new Date(experiment.updated_at).toLocaleDateString()}
                    </Text>
                </View>
                {experiment.tags.length > 0 && (
                    <View style={styles.tags}>
                        {experiment.tags.map((tag) => (
                            <View key={tag} style={styles.tag}>
                                <Text style={styles.tagText}>{tag}</Text>
                            </View>
                        ))}
                    </View>
                )}

                {/* Render HTML content */}
                {Platform.OS === 'web' ? (
                    <div
                        style={{ color: '#FFFFFE', lineHeight: '1.7', marginTop: 16 }}
                        dangerouslySetInnerHTML={{ __html: experiment.content }}
                    />
                ) : (
                    <HtmlContent html={experiment.content} />
                )}
            </ScrollView>
        </SafeAreaView>
    );
}

function HtmlContent({ html }: { html: string }) {
    const { WebView } = require('react-native-webview');
    const styledHtml = `
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { background: #0F0E17; color: #FFFFFE; font-family: sans-serif;
               font-size: 15px; line-height: 1.7; padding: 0 4px; margin: 0; }
        a { color: #6C63FF; }
        img { max-width: 100%; border-radius: 8px; }
        h1,h2,h3 { color: #FFFFFE; }
        blockquote { border-left: 3px solid #6C63FF; padding-left: 12px; color: #A7A9BE; }
      </style>
    </head>
    <body>${html}</body>
    </html>`;

    return (
        <WebView
            source={{ html: styledHtml }}
            style={{ flex: 1, minHeight: 400, backgroundColor: '#0F0E17' }}
            scrollEnabled={false}
            javaScriptEnabled={false}
        />
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    center: { flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' },
    error: { color: Colors.error },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
    },
    backBtn: { padding: Spacing.xs },
    backText: { color: Colors.primary, fontSize: FontSize.md },
    editBtn: { paddingVertical: Spacing.xs, paddingHorizontal: Spacing.md, minHeight: 36 },
    scroll: { flex: 1 },
    content: { padding: Spacing.md, paddingBottom: Spacing.xxl },
    title: { fontSize: FontSize.xxl, fontWeight: '800', color: Colors.text, marginBottom: Spacing.sm },
    meta: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.sm },
    badge: { paddingHorizontal: Spacing.sm, paddingVertical: 2, borderRadius: Radius.full },
    badgeActive: { backgroundColor: 'rgba(67, 217, 173, 0.2)' },
    badgeCompleted: { backgroundColor: 'rgba(167, 169, 190, 0.2)' },
    badgeText: { fontSize: FontSize.xs, color: Colors.textMuted, fontWeight: '600' },
    date: { color: Colors.textMuted, fontSize: FontSize.xs },
    tags: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs, marginBottom: Spacing.md },
    tag: { backgroundColor: Colors.surfaceAlt, paddingHorizontal: Spacing.sm, paddingVertical: 2, borderRadius: Radius.full },
    tagText: { color: Colors.textMuted, fontSize: FontSize.xs },
});
