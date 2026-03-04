import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { Card } from '../components/shared/Card';
import { Button } from '../components/shared/Button';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';
interface Experiment {
    id: string;
    title: string;
    slug: string;
    content: string;
    status: string;
    tags: string[];
    author_id: string;
    created_at: string;
    updated_at: string;
}

export default function ExperimentsScreen() {
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'active' | 'completed'>('active');

    const load = async () => {
        setLoading(true);
        try {
            const res = await api.get('/experiments/');
            setExperiments(res.data ?? []);
        } catch {
            setExperiments([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const filtered = experiments.filter((e) => e.status === activeTab);

    const renderItem = ({ item }: { item: Experiment }) => (
        <TouchableOpacity onPress={() => navigation.navigate('ExperimentDetail', { experimentId: item.id })}>
            <Card style={styles.card}>
                <View style={styles.cardHeader}>
                    <Text style={styles.cardTitle}>{item.title}</Text>
                    <View style={[styles.badge, item.status === 'active' ? styles.badgeActive : styles.badgeCompleted]}>
                        <Text style={styles.badgeText}>{item.status}</Text>
                    </View>
                </View>
                {item.tags.length > 0 && (
                    <View style={styles.tags}>
                        {item.tags.map((tag) => (
                            <View key={tag} style={styles.tag}>
                                <Text style={styles.tagText}>{tag}</Text>
                            </View>
                        ))}
                    </View>
                )}
                <Text style={styles.date}>
                    {item.status === 'active' ? 'Started' : 'Completed'}: {new Date(item.updated_at).toLocaleDateString()}
                </Text>
            </Card>
        </TouchableOpacity>
    );

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <View style={styles.header}>
                <Text style={styles.title}>Experiments</Text>
                {user?.is_admin && (
                    <Button
                        title="+ New"
                        onPress={() => navigation.navigate('ExperimentEditor', { experimentId: 'new' })}
                        style={styles.newBtn}
                    />
                )}
            </View>

            <View style={styles.tabs}>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'active' && styles.activeTab]}
                    onPress={() => setActiveTab('active')}
                >
                    <Text style={[styles.tabText, activeTab === 'active' && styles.activeTabText]}>Active</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'completed' && styles.activeTab]}
                    onPress={() => setActiveTab('completed')}
                >
                    <Text style={[styles.tabText, activeTab === 'completed' && styles.activeTabText]}>Results</Text>
                </TouchableOpacity>
            </View>

            {loading ? (
                <View style={styles.center}>
                    <ActivityIndicator size="large" color={Colors.primary} />
                </View>
            ) : (
                <FlatList
                    data={filtered}
                    keyExtractor={(item) => item.id}
                    renderItem={renderItem}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={
                        <Text style={styles.empty}>
                            {activeTab === 'active'
                                ? 'No active experiments yet.'
                                : 'No completed experiments yet.'}
                        </Text>
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
    tabs: {
        flexDirection: 'row',
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        gap: Spacing.sm,
    },
    tab: {
        paddingVertical: Spacing.xs + 2,
        paddingHorizontal: Spacing.md,
        borderRadius: Radius.full,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    activeTab: { backgroundColor: Colors.primary, borderColor: Colors.primary },
    tabText: { color: Colors.textMuted, fontSize: FontSize.sm },
    activeTabText: { color: Colors.white, fontWeight: '600' },
    list: { padding: Spacing.md, paddingTop: 0 },
    card: { marginBottom: Spacing.sm },
    cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: Spacing.sm },
    cardTitle: { flex: 1, color: Colors.text, fontSize: FontSize.md, fontWeight: '700', marginRight: Spacing.sm },
    badge: { paddingHorizontal: Spacing.sm, paddingVertical: 2, borderRadius: Radius.full },
    badgeActive: { backgroundColor: 'rgba(67, 217, 173, 0.2)' },
    badgeCompleted: { backgroundColor: 'rgba(167, 169, 190, 0.2)' },
    badgeText: { fontSize: FontSize.xs, color: Colors.textMuted, fontWeight: '600' },
    tags: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs, marginBottom: Spacing.sm },
    tag: { backgroundColor: Colors.surfaceAlt, paddingHorizontal: Spacing.sm, paddingVertical: 2, borderRadius: Radius.full },
    tagText: { color: Colors.textMuted, fontSize: FontSize.xs },
    date: { color: Colors.textMuted, fontSize: FontSize.xs },
    empty: { color: Colors.textMuted, textAlign: 'center', marginTop: Spacing.xl },
});
