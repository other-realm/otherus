export const Colors = {
    primary: '#6C63FF',
    primaryDark: '#4B44CC',
    secondary: '#FF6584',
    background: '#0F0E17',
    surface: '#1A1A2E',
    surfaceAlt: '#16213E',
    border: '#2D2D44',
    text: '#FFFFFE',
    textMuted: '#A7A9BE',
    success: '#43D9AD',
    warning: '#FFD166',
    error: '#EF233C',
    white: '#FFFFFF',
};
export const Spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
};
export const FontSize = {
    xs: 11,
    sm: 13,
    md: 15,
    lg: 18,
    xl: 22,
    xxl: 28,
    xxxl: 36,
};
export const Radius = {
    sm: 6,
    md: 12,
    lg: 20,
    full: 9999,
};
export const styles = StyleSheet.create({
    body: { background: background, color: '#FFFFFE', fontFamily: 'sans-serif',
        fontSize:'15px', lineHeight: '1.7', padding: '0 4px', margin: 0},
    a: { color: '#6C63FF'},
    img: { maxWidth: '100%', borderRadius: '8px' },
        h1, h2, h3: { color: '#FFFFFE' },
    blockquote: { borderLeft: '3px solid #6C63FF', paddingLeft: '12px', color: '#A7A9BE'}
});