# VSM Mermaid Generator - Preview Feature Documentation

## Overview

The Preview feature allows users to visualize their Value Stream Map diagrams in real-time without leaving the application. This feature provides an interactive preview modal with zoom controls, fullscreen support, and the ability to save the diagram as a PNG image.

## Features

### 1. **Live Diagram Rendering**
- Renders Mermaid diagrams using the official Mermaid.js library
- Shows the exact visual representation of the generated code
- Updates reflect any changes made to the diagram

### 2. **Interactive Zoom Controls**
- **Zoom In/Out**: Scale the diagram from 25% to 400%
- **Reset Zoom**: Quickly return to 100% scale
- **Keyboard Shortcuts**:
  - `+` or `=`: Zoom in
  - `-` or `_`: Zoom out
  - `0`: Reset zoom to 100%
  - `Esc`: Close preview modal

### 3. **Fullscreen Mode**
- Expand the preview to fill the entire screen
- Minimize button appears when in fullscreen mode
- Maintains all zoom and interaction capabilities

### 4. **Screenshot Capture**
- Save the diagram as a PNG image
- High-quality export (2x resolution for crisp images)
- Automatic filename generation based on diagram title and timestamp
- Downloads to your browser's default download location

## How to Use

### Opening the Preview

1. Create or load a Value Stream Map diagram
2. Click "Generate Mermaid Code" to create the diagram code
3. Click the **"Preview"** button (appears next to the "Save as Markdown" button)
4. The preview modal will open with your rendered diagram

### Using Preview Controls

#### Zoom Controls
- Click the **[-]** button to zoom out
- Click the **[+]** button to zoom in
- Click the **[⊙]** button to reset zoom to 100%
- Current zoom level is displayed between the zoom buttons

#### Fullscreen Toggle
- Click the **[⛶]** button to enter fullscreen mode
- Click the **[⛶]** button again (or the minimize button) to exit fullscreen

#### Save as Image
- Click the **[📷]** camera button to save the diagram as PNG
- The image will be saved to your Downloads folder
- Filename format: `{DiagramTitle}_{Timestamp}.png` or `vsm_diagram_{Timestamp}.png`

#### Close Preview
- Click the **[X]** button in the top-right corner
- Or click outside the preview modal
- Or press the `Esc` key

## Technical Details

### Security
- Mermaid.js runs with `securityLevel: 'strict'` to prevent XSS attacks
- All user input is properly escaped before rendering
- Content Security Policy (CSP) compatible

### Browser Compatibility
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Uses html2canvas for screenshot functionality

### Performance
- Diagrams render asynchronously to prevent UI blocking
- Zoom transformations use CSS for smooth performance
- Large diagrams may take a moment to render initially

## Troubleshooting

### Preview Won't Open
- Ensure you've generated Mermaid code first
- Check browser console for any JavaScript errors
- Verify Mermaid.js CDN is accessible

### Diagram Not Rendering
- Check if the Mermaid syntax is valid
- Look for error messages in the preview modal
- Try regenerating the diagram code

### Screenshot Not Saving
- Check browser permissions for downloads
- Ensure sufficient disk space
- Try a different browser if issues persist
- Note: The browser controls where files are saved (not the application)

### Zoom Issues
- If zoom controls are unresponsive, try resetting zoom
- Close and reopen the preview modal
- Check if browser zoom is interfering (reset with Ctrl/Cmd + 0)

## Best Practices

1. **Preview Before Saving**: Always preview your diagram to ensure it looks correct before saving
2. **Use Appropriate Zoom**: Zoom out for large diagrams to see the complete flow
3. **Screenshot for Presentations**: Use the camera feature to capture diagrams for presentations or documentation
4. **Fullscreen for Detail**: Use fullscreen mode when examining complex diagrams

## Limitations

- Maximum zoom level: 400%
- Minimum zoom level: 25%
- PNG exports are limited by browser memory constraints
- Very large diagrams may experience performance issues

## Future Enhancements

Potential improvements under consideration:
- SVG export option
- Pan/drag functionality for large diagrams
- Multiple export resolutions
- Print-friendly view
- Dark mode support

---

*Last Updated: November 2024*  
*Feature Version: 1.0.0*