/**
 * DynamicForm — renders a form from a JSON schema object.
 *
 * Supported field types:
 *   input, editor, image, editable_input_array, radio,
 *   slider_group, 2_slider_group, map
 */
import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Platform,
  Image,
  Alert,
} from 'react-native';
import Slider from '@react-native-community/slider';
import * as ImagePicker from 'expo-image-picker';
import { Colors, Spacing, FontSize, Radius } from '../../utils/theme';
import { Button } from '../shared/Button';
import MapField from './MapField';
import RichTextEditor from './RichTextEditor';

// ── Types ──────────────────────────────────────────────────────────────────────

export type FormSchema = Record<string, FieldDef>;

export type FieldDef =
  | InputField
  | EditorField
  | ImageField
  | EditableArrayField
  | RadioField
  | SliderGroupField
  | DoubleSliderGroupField
  | MapField;

interface BaseField {
  label: string;
}

interface InputField extends BaseField { type: 'input'; value: string }
interface EditorField extends BaseField { type: 'editor'; value: string }
interface ImageField extends BaseField { type: 'image'; src: string }
interface EditableArrayField extends BaseField { type: 'editable_input_array'; value: string[] }
interface RadioField extends BaseField { type: 'radio'; value: string[] }
interface SliderGroupField extends BaseField {
  type: 'slider_group';
  items: Record<string, { label: string; value: number }>;
  other: { label: string; value: string };
}
interface DoubleSliderGroupField extends BaseField {
  type: '2_slider_group';
  items: Record<string, { label: string; have: number; want: number }>;
  other: { label: string; value: string };
}
interface MapField extends BaseField {
  type: 'map';
  placed: string;
  coordinates: { lat: number; lng: number };
}

// ── Component ──────────────────────────────────────────────────────────────────

interface DynamicFormProps {
  schema: FormSchema;
  initialValues?: Record<string, any>;
  onSubmit?: (values: Record<string, any>) => void;
  onChange?: (values: Record<string, any>) => void;
  loading?: boolean;
  showSaveButton?: boolean;
}

export default function DynamicForm({
  schema,
  initialValues = {},
  onSubmit,
  onChange,
  loading = false,
  showSaveButton = false,
}: DynamicFormProps) {
  const [values, setValues] = useState<Record<string, any>>(() => {
    const init: Record<string, any> = {};
    Object.entries(schema).forEach(([key, field]) => {
      if (key === 'id') return;
      const f = field as FieldDef;
      if (f.type === 'input') init[key] = initialValues[key] ?? (f as InputField).value ?? '';
      else if (f.type === 'editor') init[key] = initialValues[key] ?? (f as EditorField).value ?? '';
      else if (f.type === 'image') init[key] = initialValues[key] ?? (f as ImageField).src ?? '';
      else if (f.type === 'editable_input_array') init[key] = initialValues[key] ?? (f as EditableArrayField).value ?? [];
      else if (f.type === 'radio') init[key] = initialValues[key] ?? '';
      else if (f.type === 'slider_group') {
        const sf = f as SliderGroupField;
        init[key] = initialValues[key] ?? {
          items: Object.fromEntries(
            Object.entries(sf.items).map(([k, v]) => [k, v.value])
          ),
          other: sf.other.value,
        };
      } else if (f.type === '2_slider_group') {
        const df = f as DoubleSliderGroupField;
        init[key] = initialValues[key] ?? {
          items: Object.fromEntries(
            Object.entries(df.items).map(([k, v]) => [k, { have: v.have, want: v.want }])
          ),
          other: df.other.value,
        };
      } else if (f.type === 'map') {
        const mf = f as MapField;
        init[key] = initialValues[key] ?? { lat: mf.coordinates.lat, lng: mf.coordinates.lng };
      }
    });
    return init;
  });

  // Notify parent of every change for auto-save
  const onChangeRef = useRef(onChange);
  useEffect(() => { onChangeRef.current = onChange; }, [onChange]);

  const update = useCallback((key: string, val: any) => {
    setValues((prev) => {
      const next = { ...prev, [key]: val };
      // Fire onChange asynchronously so state has settled
      setTimeout(() => onChangeRef.current?.(next), 0);
      return next;
    });
  }, []);

  const renderField = (key: string, field: FieldDef) => {
    switch (field.type) {
      case 'input':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <TextInput
              style={styles.input}
              value={values[key] ?? ''}
              onChangeText={(v) => update(key, v)}
              placeholderTextColor={Colors.textMuted}
            />
          </View>
        );

      case 'editor':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <RichTextEditor
              value={values[key] ?? ''}
              onChange={(v) => update(key, v)}
            />
          </View>
        );

      case 'image':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <ImageUploadField
              value={values[key] ?? ''}
              onChange={(v) => update(key, v)}
            />
          </View>
        );

      case 'editable_input_array':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <EditableArrayField
              value={values[key] ?? []}
              onChange={(v) => update(key, v)}
            />
          </View>
        );

      case 'radio':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <RadioField
              options={field.value}
              selected={values[key] ?? ''}
              onChange={(v) => update(key, v)}
            />
          </View>
        );

      case 'slider_group': {
        const sf = field as SliderGroupField;
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={sf.label} />
            {Object.entries(sf.items).map(([itemKey, item]) => (
              <SliderRow
                key={itemKey}
                label={item.label}
                value={values[key]?.items?.[itemKey] ?? item.value}
                onChange={(v) => {
                  update(key, {
                    ...values[key],
                    items: { ...values[key]?.items, [itemKey]: v },
                  });
                }}
              />
            ))}
            <Text style={styles.otherLabel}>{sf.other.label}</Text>
            <TextInput
              style={styles.input}
              value={values[key]?.other ?? ''}
              onChangeText={(v) => update(key, { ...values[key], other: v })}
              placeholderTextColor={Colors.textMuted}
            />
          </View>
        );
      }

      case '2_slider_group': {
        const df = field as DoubleSliderGroupField;
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={df.label} />
            <View style={styles.doubleSliderHeader}>
              <Text style={[styles.sliderHeaderLabel, { flex: 2 }]}>Skill</Text>
              <Text style={[styles.sliderHeaderLabel, { flex: 1, textAlign: 'center' }]}>Have</Text>
              <Text style={[styles.sliderHeaderLabel, { flex: 1, textAlign: 'center' }]}>Want</Text>
            </View>
            {Object.entries(df.items).map(([itemKey, item]) => (
              <DoubleSliderRow
                key={itemKey}
                label={item.label}
                have={values[key]?.items?.[itemKey]?.have ?? item.have}
                want={values[key]?.items?.[itemKey]?.want ?? item.want}
                onHaveChange={(v) => {
                  update(key, {
                    ...values[key],
                    items: {
                      ...values[key]?.items,
                      [itemKey]: { ...values[key]?.items?.[itemKey], have: v },
                    },
                  });
                }}
                onWantChange={(v) => {
                  update(key, {
                    ...values[key],
                    items: {
                      ...values[key]?.items,
                      [itemKey]: { ...values[key]?.items?.[itemKey], want: v },
                    },
                  });
                }}
              />
            ))}
            <Text style={styles.otherLabel}>{df.other.label}</Text>
            <TextInput
              style={styles.input}
              value={values[key]?.other ?? ''}
              onChangeText={(v) => update(key, { ...values[key], other: v })}
              placeholderTextColor={Colors.textMuted}
            />
          </View>
        );
      }

      case 'map':
        return (
          <View key={key} style={styles.fieldWrapper}>
            <Label html={field.label} />
            <MapField
              lat={values[key]?.lat ?? (field as any).coordinates.lat}
              lng={values[key]?.lng ?? (field as any).coordinates.lng}
              onChange={(lat, lng) => update(key, { lat, lng })}
            />
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {Object.entries(schema).map(([key, field]) => {
        if (key === 'id') return null;
        return renderField(key, field as FieldDef);
      })}
      {showSaveButton && onSubmit && (
        <Button
          title="Save Profile"
          onPress={() => onSubmit(values)}
          loading={loading}
          style={styles.submitBtn}
        />
      )}
    </ScrollView>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function Label({ html }: { html: string }) {
  // Strip basic HTML tags for native rendering
  const plain = html.replace(/<[^>]+>/g, '');
  return <Text style={styles.label}>{plain}</Text>;
}

function ImageUploadField({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const pick = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
      base64: true,
    });
    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      onChange(asset.uri);
    }
  };

  return (
    <View>
      {value ? (
        <Image source={{ uri: value }} style={styles.avatar} />
      ) : (
        <View style={styles.avatarPlaceholder}>
          <Text style={styles.avatarPlaceholderText}>No image selected</Text>
        </View>
      )}
      <Button title="Choose Image" onPress={pick} variant="outline" style={styles.imageBtn} />
    </View>
  );
}

function EditableArrayField({
  value,
  onChange,
}: {
  value: string[];
  onChange: (v: string[]) => void;
}) {
  const [draft, setDraft] = useState('');

  const add = () => {
    if (!draft.trim()) return;
    onChange([...value, draft.trim()]);
    setDraft('');
  };

  const remove = (idx: number) => {
    onChange(value.filter((_, i) => i !== idx));
  };

  return (
    <View>
      {value.map((item, idx) => (
        <View key={idx} style={styles.arrayRow}>
          <Text style={styles.arrayItem} numberOfLines={1}>{item}</Text>
          <TouchableOpacity onPress={() => remove(idx)}>
            <Text style={styles.removeBtn}>✕</Text>
          </TouchableOpacity>
        </View>
      ))}
      <View style={styles.arrayInputRow}>
        <TextInput
          style={[styles.input, { flex: 1, marginBottom: 0 }]}
          value={draft}
          onChangeText={setDraft}
          placeholder="Add a URL…"
          placeholderTextColor={Colors.textMuted}
          onSubmitEditing={add}
        />
        <TouchableOpacity style={styles.addBtn} onPress={add}>
          <Text style={styles.addBtnText}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function RadioField({
  options,
  selected,
  onChange,
}: {
  options: string[];
  selected: string;
  onChange: (v: string) => void;
}) {
  return (
    <View style={styles.radioGroup}>
      {options.map((opt) => (
        <TouchableOpacity
          key={opt}
          style={[styles.radioOption, selected === opt && styles.radioSelected]}
          onPress={() => onChange(opt)}
        >
          <Text style={[styles.radioText, selected === opt && styles.radioTextSelected]}>
            {opt}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

function SliderRow({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <View style={styles.sliderRow}>
      <Text style={styles.sliderLabel}>{label}</Text>
      <View style={styles.sliderContainer}>
        <Slider
          style={{ flex: 1 }}
          minimumValue={0}
          maximumValue={100}
          value={value}
          onValueChange={onChange}
          minimumTrackTintColor={Colors.primary}
          maximumTrackTintColor={Colors.border}
          thumbTintColor={Colors.primary}
        />
        <Text style={styles.sliderValue}>{Math.round(value)}</Text>
      </View>
    </View>
  );
}

function DoubleSliderRow({
  label,
  have,
  want,
  onHaveChange,
  onWantChange,
}: {
  label: string;
  have: number;
  want: number;
  onHaveChange: (v: number) => void;
  onWantChange: (v: number) => void;
}) {
  return (
    <View style={styles.doubleSliderRow}>
      <Text style={[styles.sliderLabel, { flex: 2 }]}>{label}</Text>
      <View style={{ flex: 1 }}>
        <Slider
          minimumValue={0}
          maximumValue={100}
          value={have}
          onValueChange={onHaveChange}
          minimumTrackTintColor={Colors.success}
          maximumTrackTintColor={Colors.border}
          thumbTintColor={Colors.success}
        />
        <Text style={[styles.sliderValue, { textAlign: 'center' }]}>{Math.round(have)}</Text>
      </View>
      <View style={{ flex: 1 }}>
        <Slider
          minimumValue={0}
          maximumValue={100}
          value={want}
          onValueChange={onWantChange}
          minimumTrackTintColor={Colors.secondary}
          maximumTrackTintColor={Colors.border}
          thumbTintColor={Colors.secondary}
        />
        <Text style={[styles.sliderValue, { textAlign: 'center' }]}>{Math.round(want)}</Text>
      </View>
    </View>
  );
}

// ── Styles ─────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.md, paddingBottom: Spacing.xxl },
  fieldWrapper: { marginBottom: Spacing.lg },
  label: {
    color: Colors.text,
    fontSize: FontSize.md,
    fontWeight: '600',
    marginBottom: Spacing.sm,
    lineHeight: 22,
  },
  input: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.sm,
    color: Colors.text,
    padding: Spacing.sm + 2,
    fontSize: FontSize.md,
    marginBottom: Spacing.xs,
  },
  submitBtn: { marginTop: Spacing.xl },
  avatar: { width: 100, height: 100, borderRadius: 50, marginBottom: Spacing.sm },
  avatarPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  avatarPlaceholderText: { color: Colors.textMuted, fontSize: FontSize.xs, textAlign: 'center' },
  imageBtn: { alignSelf: 'flex-start' },
  arrayRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: Radius.sm,
    padding: Spacing.sm,
    marginBottom: Spacing.xs,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  arrayItem: { flex: 1, color: Colors.text, fontSize: FontSize.sm },
  removeBtn: { color: Colors.error, fontSize: FontSize.md, paddingHorizontal: Spacing.sm },
  arrayInputRow: { flexDirection: 'row', gap: Spacing.sm },
  addBtn: {
    backgroundColor: Colors.primary,
    borderRadius: Radius.sm,
    paddingHorizontal: Spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addBtnText: { color: Colors.white, fontSize: FontSize.xl, fontWeight: '700' },
  radioGroup: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
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
  sliderRow: { marginBottom: Spacing.sm },
  sliderLabel: { color: Colors.textMuted, fontSize: FontSize.sm, marginBottom: 2 },
  sliderContainer: { flexDirection: 'row', alignItems: 'center' },
  sliderValue: { color: Colors.primary, fontSize: FontSize.sm, width: 32, textAlign: 'right' },
  otherLabel: { color: Colors.textMuted, fontSize: FontSize.sm, marginTop: Spacing.sm, marginBottom: Spacing.xs },
  doubleSliderHeader: { flexDirection: 'row', marginBottom: Spacing.sm },
  sliderHeaderLabel: { color: Colors.textMuted, fontSize: FontSize.sm, fontWeight: '600' },
  doubleSliderRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: Spacing.sm },
});
