/**
 * CommunityScreen — shows aggregated profile data as radar charts,
 * lists all member profiles, and supports search/filter.
 */
import React, { useEffect, useState, useMemo } from 'react';
import {
    View,
    Text,
    TextInput,
    FlatList,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
    Image,
    Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import api from '../services/api';
import { Card } from '../components/shared/Card';

// ── Radar chart (web only via Chart.js; native fallback) ──────────────────────

let RadarChart: React.FC<{ labels: string[]; datasets: any[] }> | null = null;

if (Platform.OS === 'web') {
    const {
        Chart,
        RadialLinearScale,
        PointElement,
        LineElement,
        Filler,
        Tooltip,
        Legend,
    } = require('chart.js');
    const { Radar } = require('react-chartjs-2');

    Chart.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

    RadarChart = ({ labels, datasets }) => (
        <Radar
            data={{ labels, datasets }}
            options={{
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: { color: '#A7A9BE', stepSize: 25 },
                        grid: { color: '#2D2D44' },
                        pointLabels: { color: '#FFFFFE', font: { size: 11 } },
                    },
                },
                plugins: {
                    legend: { labels: { color: '#FFFFFE' } },
                },
            }}
        />
    );
}

// ── Types ──────────────────────────────────────────────────────────────────────

interface Profile {
    user_id: string;
    user_name: string;
    avatar_url?: string;
    data: Record<string, any>;
    updated_at: string;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function extractSliderValues(profiles: Profile[], groupKey: string): { labels: string[]; avg: number[] } {
    if (!profiles.length) return { labels: [], avg: [] };
    const first = profiles.find((p) => p.data?.[groupKey]?.items);
    if (!first) return { labels: [], avg: [] };
    const items = first.data[groupKey].items as Record<string, any>;
    const labels = Object.values(items).map((v: any) => v.label ?? '');
    const keys = Object.keys(items);
    const avg = keys.map((k) => {
        const vals = profiles
            .map((p) => {
                const v = p.data?.[groupKey]?.items?.[k];
                return typeof v === 'number' ? v : v?.value ?? 50;
            })
            .filter((v) => typeof v === 'number');
        return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 50;
    });
    return { labels, avg };
}
// ── Component ──────────────────────────────────────────────────────────────────
export default function CommunityScreen() {
    const navigation = useNavigation<any>();
    const [profiles, setProfiles] = useState<Profile[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [activeTab, setActiveTab] = useState<'members' | 'charts'>('members');
    useEffect(() => {
        const load = async () => {
            try {
                const res = await api.get('/profiles/');
                setProfiles(res.data ?? []);
            } catch {
                setProfiles([]);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const filtered = useMemo(() => {
        if (!search.trim()) return profiles;
        const q = search.toLowerCase();
        return profiles.filter(
            (p) =>
                p.user_name.toLowerCase().includes(q) ||
                JSON.stringify(p.data).toLowerCase().includes(q)
        );
    }, [profiles, search]);

    const wantsChart = useMemo(() => extractSliderValues(profiles, 'wants'), [profiles]);
    const sharingChart = useMemo(() => extractSliderValues(profiles, 'sharing'), [profiles]);

    const renderMember = ({ item }: { item: Profile }) => (
        <TouchableOpacity
            onPress={() => navigation.navigate('ProfileDetail', { userId: item.user_id })}
        >
            <Card style={styles.memberCard}>
                <View style={styles.memberRow}>
                    {item.avatar_url ? (
                        <Image source={{ uri: item.avatar_url }} style={styles.avatar} />
                    ) : (
                        <View style={styles.avatarFallback}>
                            <Text style={styles.avatarInitial}>{item.user_name[0]?.toUpperCase()}</Text>
                        </View>
                    )}
                    <View style={{ flex: 1 }}>
                        <Text style={styles.memberName}>{item.user_name}</Text>
                        {item.data?.transhumanist_ideas ? (
                            <Text style={styles.memberSnippet} numberOfLines={2}>
                                {item.data.transhumanist_ideas.replace(/<[^>]+>/g, '')}
                            </Text>
                        ) : null}
                    </View>
                </View>
            </Card>
        </TouchableOpacity>
    );

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.title}>Community</Text>
                <Text style={styles.subtitle}>{profiles.length} members</Text>
            </View>

            {/* Search */}
            <View style={styles.searchRow}>
                <TextInput
                    style={styles.searchInput}
                    placeholder="Search members or traits…"
                    placeholderTextColor={Colors.textMuted}
                    value={search}
                    onChangeText={setSearch}
                />
            </View>

            {/* Tabs */}
            <View style={styles.tabs}>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'members' && styles.activeTab]}
                    onPress={() => setActiveTab('members')}
                >
                    <Text style={[styles.tabText, activeTab === 'members' && styles.activeTabText]}>Members</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.tab, activeTab === 'charts' && styles.activeTab]}
                    onPress={() => setActiveTab('charts')}
                >
                    <Text style={[styles.tabText, activeTab === 'charts' && styles.activeTabText]}>Aggregate Charts</Text>
                </TouchableOpacity>
            </View>

            {loading ? (
                <View style={styles.center}>
                    <ActivityIndicator size="large" color={Colors.primary} />
                </View>
            ) : activeTab === 'members' ? (
                <FlatList
                    data={filtered}
                    keyExtractor={(item) => item.user_id}
                    renderItem={renderMember}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={
                        <Text style={styles.empty}>No members found.</Text>
                    }
                />
            ) : (
                <View style={styles.chartsContainer}>
                    {Platform.OS === 'web' && RadarChart ? (
                        <>
                            <Text style={styles.chartTitle}>Community Wants (avg)</Text>
                            {wantsChart.labels.length > 0 ? (
                                <RadarChart
                                    labels={wantsChart.labels}
                                    datasets={[
                                        {
                                            label: 'Community Average',
                                            data: wantsChart.avg,
                                            backgroundColor: 'rgba(108, 99, 255, 0.2)',
                                            borderColor: '#6C63FF',
                                            borderWidth: 2,
                                        },
                                    ]}
                                />
                            ) : (
                                <Text style={styles.empty}>No data yet.</Text>
                            )}

                            <Text style={[styles.chartTitle, { marginTop: Spacing.xl }]}>Sharing Comfort (avg)</Text>
                            {sharingChart.labels.length > 0 ? (
                                <RadarChart
                                    labels={sharingChart.labels}
                                    datasets={[
                                        {
                                            label: 'Community Average',
                                            data: sharingChart.avg,
                                            backgroundColor: 'rgba(255, 101, 132, 0.2)',
                                            borderColor: '#FF6584',
                                            borderWidth: 2,
                                        },
                                    ]}
                                />
                            ) : (
                                <Text style={styles.empty}>No data yet.</Text>
                            )}
                        </>
                    ) : (
                        <Text style={styles.empty}>
                            Radar charts are available on the web version. On mobile, please view individual profiles.
                        </Text>
                    )}
                </View>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
    header: {
        paddingHorizontal: Spacing.md,
        paddingTop: Spacing.md,
        paddingBottom: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
    },
    title: { fontSize: FontSize.xl, fontWeight: '800', color: Colors.text },
    subtitle: { fontSize: FontSize.sm, color: Colors.textMuted, marginTop: 2 },
    searchRow: { padding: Spacing.md, paddingBottom: Spacing.sm },
    searchInput: {
        backgroundColor: Colors.surface,
        borderWidth: 1,
        borderColor: Colors.border,
        borderRadius: Radius.full,
        color: Colors.text,
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        fontSize: FontSize.md,
    },
    tabs: {
        flexDirection: 'row',
        paddingHorizontal: Spacing.md,
        marginBottom: Spacing.sm,
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
    memberCard: { marginBottom: Spacing.sm },
    memberRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
    avatar: { width: 48, height: 48, borderRadius: 24 },
    avatarFallback: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: Colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
    },
    avatarInitial: { color: Colors.white, fontSize: FontSize.lg, fontWeight: '700' },
    memberName: { color: Colors.text, fontSize: FontSize.md, fontWeight: '600' },
    memberSnippet: { color: Colors.textMuted, fontSize: FontSize.sm, marginTop: 2 },
    empty: { color: Colors.textMuted, textAlign: 'center', marginTop: Spacing.xl },
    chartsContainer: { flex: 1, padding: Spacing.md },
    chartTitle: { color: Colors.text, fontSize: FontSize.lg, fontWeight: '700', marginBottom: Spacing.md },
});
