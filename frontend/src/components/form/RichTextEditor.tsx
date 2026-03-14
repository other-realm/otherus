import '../../../assets/styles.css'
import React, { useState, useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { TextStyleKit } from '@tiptap/extension-text-style'
import { MenuBar } from './MenuBar';
interface RichTextEditorProps {
    value: string;
    onChange: (html: string) => void;
    minHeight?: number;
}
const RichTextEditor: React.FC<RichTextEditorProps> = ({ value, onChange, minHeight = 200 }) => {
    const [editorContent, setEditorContent,TextStyleKit] = useState(value);
    const editor = useEditor({
        extensions: [
            StarterKit,
        ],
        content: value,
        onUpdate: ({ editor }) => {
            const html = editor.getHTML();
            setEditorContent(html);
            onChange(html);
        },
    });
    // Update editor content when prop changes
    useEffect(() => {
        if (editor && editorContent !== value) {
            editor.commands.setContent(value);
            setEditorContent(value);
        }
    }, [value, editor]);
    return (
        <div className="rich-text-editor" style={{background:'#fff'}}>
            {editor && <MenuBar editor={editor} />}
            <div style={{ minHeight: `${minHeight}px`, border: '1px solid #ccc', borderRadius: '4px', marginTop: '8px' }}>
                <EditorContent editor={editor} />
            </div>
        </div>
    );
};
export default RichTextEditor;