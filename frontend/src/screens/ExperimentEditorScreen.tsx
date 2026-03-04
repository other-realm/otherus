import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    TextInput,
    ScrollView,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Colors, Spacing, FontSize, Radius } from '../utils/theme';
import { Button } from '../components/shared/Button';
import RichTextEditor from '../components/form/RichTextEditor';
import api from '../services/api';

export default function ExperimentEditorScreen() {
    const navigation = useNavigation<any>();
    const route = useRoute<any>();
    const { experimentId } = route.params;
    const isNew = experimentId === 'new';

    const [title, setTitle] = useState('');
    const [slug, setSlug] = useState('');
    const [content, setContent] = useState('');
    const [status, setStatus] = useState<'active' | 'completed'>('active');
    const [tagsInput, setTagsInput] = useState('');
    const [loading, setLoading] = useState(!isNew);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (!isNew) {
            const load = async () => {
                try {
                    const res = await api.get(`/experiments/${experimentId}`);
                    const exp = res.data;
                    setTitle(exp.title);
                    setSlug(exp.slug);
                    setContent(exp.content);
                    setStatus(exp.status);
                    setTagsInput(exp.tags.join(', '));
                } catch {
                    Alert.alert('Error', 'Could not load experiment.');
                    navigation.goBack();
                } finally {
                    setLoading(false);
                }
            };
            load();
        }
    }, [experimentId]);

    const handleSave = async () => {
        if (!title.trim()) {
            Alert.alert('Validation', 'Title is required.');
            return;
        }
        setSaving(true);
        const tags = tagsInput.split(',').map((t) => t.trim()).filter(Boolean);
        try {
            if (isNew) {
                const autoSlug = slug || title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
                await api.post('/experiments/', { title, slug: autoSlug, content, status, tags });
            } else {
                await api.put(`/experiments/${experimentId}`, { title, content, status, tags });
            }
            Alert.alert('Saved', 'Experiment saved successfully.');
            navigation.goBack();
        } catch (err: any) {
            Alert.alert('Error', err?.response?.data?.detail ?? 'Failed to save.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color={Colors.primary} />
            </View>
        );
    }

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Text style={styles.backText}>← Cancel</Text>
                </TouchableOpacity>
                <Text style={styles.headerTitle}>{isNew ? 'New Experiment' : 'Edit Experiment'}</Text>
                <Button title="Save" onPress={handleSave} loading={saving} style={styles.saveBtn} />
            </View>

            <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
                <Text style={styles.label}>Title *</Text>
                <TextInput
                    style={styles.input}
                    value={title}
                    onChangeText={setTitle}
                    placeholder="Experiment title"
                    placeholderTextColor={Colors.textMuted}
                />

                {isNew && (
                    <>
                        <Text style={styles.label}>Slug (auto-generated if blank)</Text>
                        <TextInput
                            style={styles.input}
                            value={slug}
                            onChangeText={setSlug}
                            placeholder="url-friendly-slug"
                            placeholderTextColor={Colors.textMuted}
                            autoCapitalize="none"
                        />
                    </>
                )}

                <Text style={styles.label}>Status</Text>
                <View style={styles.radioRow}>
                    {(['active', 'completed'] as const).map((s) => (
                        <TouchableOpacity
                            key={s}
                            style={[styles.radioOption, status === s && styles.radioSelected]}
                            onPress={() => setStatus(s)}
                        >
                            <Text style={[styles.radioText, status === s && styles.radioTextSelected]}>
                                {s.charAt(0).toUpperCase() + s.slice(1)}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>

                <Text style={styles.label}>Tags (comma-separated)</Text>
                <TextInput
                    style={styles.input}
                    value={tagsInput}
                    onChangeText={setTagsInput}
                    placeholder="consciousness, telepathy, EEG"
                    placeholderTextColor={Colors.textMuted}
                />

                <Text style={styles.label}>Content</Text>
                <RichTextEditor
                    value={content}
                    onChange={setContent}
                    minHeight={300}
                />
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    center: { flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: Spacing.md,
        paddingVertical: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
    },
    backText: { color: Colors.primary, fontSize: FontSize.md },
    headerTitle: { color: Colors.text, fontSize: FontSize.md, fontWeight: '700' },
    saveBtn: { paddingVertical: Spacing.xs, paddingHorizontal: Spacing.md, minHeight: 36 },
    scroll: { flex: 1 },
    content: { padding: Spacing.md, paddingBottom: Spacing.xxl },
    label: { color: Colors.text, fontSize: FontSize.sm, fontWeight: '600', marginBottom: Spacing.xs, marginTop: Spacing.md },
    input: {
        backgroundColor: Colors.surface,
        borderWidth: 1,
        borderColor: Colors.border,
        borderRadius: Radius.sm,
        color: Colors.text,
        padding: Spacing.sm + 2,
        fontSize: FontSize.md,
    },
    radioRow: { flexDirection: 'row', gap: Spacing.sm },
    radioOption: {
        paddingVertical: Spacing.sm,
        paddingHorizontal: Spacing.md,
        borderRadius: Radius.full,
        borderWidth: 1.5,
        borderColor: Colors.border,
    },
    radioSelected: { backgroundColor: Colors.primary, borderColor: Colors.primary },
    radioText: { color: Colors.textMuted, fontSize: FontSize.md },
    radioTextSelected: { color: Colors.white, fontWeight: '600' },
});
