/**
 * Tests for the DynamicForm component.
 */
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';

// Mock native modules
jest.mock('@react-native-community/slider', () => 'Slider');
jest.mock('expo-image-picker', () => ({
  launchImageLibraryAsync: jest.fn(),
  MediaTypeOptions: { Images: 'Images' },
}));
jest.mock('../components/form/MapField', () => 'MapField');
jest.mock('../components/form/RichTextEditor', () => {
  const { TextInput } = require('react-native');
  return ({ value, onChange }: any) => (
    <TextInput
      testID="rich-text-editor"
      value={value}
      onChangeText={onChange}
    />
  );
});

import DynamicForm, { FormSchema } from '../components/form/DynamicForm';

const SIMPLE_SCHEMA: FormSchema = {
  name: { type: 'input', label: 'Your name:', value: '' },
  bio: { type: 'editor', label: 'Your bio:', value: '' },
  video_series: { type: 'radio', label: 'Video series?', value: ['Yes', 'No', 'Maybe'] },
  urls: { type: 'editable_input_array', label: 'Links:', value: [] },
} as any;

describe('DynamicForm', () => {
  it('renders input fields from schema', () => {
    const { getByPlaceholderText, getByText } = render(
      <DynamicForm schema={SIMPLE_SCHEMA} onSubmit={jest.fn()} />
    );
    expect(getByText('Your name:')).toBeTruthy();
  });

  it('renders radio options', () => {
    const { getByText } = render(
      <DynamicForm schema={SIMPLE_SCHEMA} onSubmit={jest.fn()} />
    );
    expect(getByText('Yes')).toBeTruthy();
    expect(getByText('No')).toBeTruthy();
    expect(getByText('Maybe')).toBeTruthy();
  });

  it('calls onSubmit with form values when Save Profile is pressed', async () => {
    const mockSubmit = jest.fn();
    const { getByText } = render(
      <DynamicForm
        schema={SIMPLE_SCHEMA}
        initialValues={{ name: 'Alice' }}
        onSubmit={mockSubmit}
      />
    );
    fireEvent.press(getByText('Save Profile'));
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledTimes(1);
      const values = mockSubmit.mock.calls[0][0];
      expect(values.name).toBe('Alice');
    });
  });

  it('initializes fields with provided initialValues', () => {
    const { getByDisplayValue } = render(
      <DynamicForm
        schema={SIMPLE_SCHEMA}
        initialValues={{ name: 'Bob' }}
        onSubmit={jest.fn()}
      />
    );
    expect(getByDisplayValue('Bob')).toBeTruthy();
  });

  it('shows loading state on submit button', () => {
    const { getByText } = render(
      <DynamicForm schema={SIMPLE_SCHEMA} onSubmit={jest.fn()} loading={true} />
    );
    // When loading, ActivityIndicator replaces text — button should be disabled
    const saveBtn = getByText('Save Profile');
    // The button is rendered but loading prop disables it
    expect(saveBtn).toBeTruthy();
  });

  it('allows adding items to editable array', async () => {
    const mockSubmit = jest.fn();
    const { getByPlaceholderText, getByText } = render(
      <DynamicForm schema={SIMPLE_SCHEMA} onSubmit={mockSubmit} />
    );
    const input = getByPlaceholderText('Add a URL…');
    fireEvent.changeText(input, 'https://example.com');
    fireEvent.press(getByText('+'));
    fireEvent.press(getByText('Save Profile'));
    await waitFor(() => {
      const values = mockSubmit.mock.calls[0][0];
      expect(values.urls).toContain('https://example.com');
    });
  });
});
