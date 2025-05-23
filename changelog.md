# Changelog - VSM Mermaid Generator

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-11-XX

### Added
- **Live Preview Feature**: Real-time visualization of VSM diagrams
  - Interactive modal window for diagram preview
  - Zoom controls (25% to 400% zoom range)
  - Fullscreen mode for detailed examination
  - Keyboard shortcuts (
, -, 0, Esc)
  - PNG export functionality with high-resolution output
  - Camera button for quick screenshot capture
  - Automatic filename generation based on diagram title

- **Enhanced Security**:
  - Mermaid.js strict security mode enabled
  - Comprehensive input sanitization
  - Content Security Policy recommendations
  - XSS prevention measures

- **Improved Testing**:
  - Preview feature test suite
  - Zoom control verification
  - Fullscreen mode testing
  - PNG export validation
  - Extended Selenium test coverage

- **Documentation Updates**:
  - Preview feature guide
  - Security documentation
  - Updated user instructions
  - Enhanced README with feature highlights

### Changed
- Updated `index.html` with preview modal implementation
- Enhanced test script to include preview functionality tests
- Improved error handling and user feedback
- Updated all documentation to reflect new features

### Technical Details
- Integrated Mermaid.js v10 for diagram rendering
- Added html2canvas v1.4.1 for PNG export
- Implemented asynchronous rendering for better performance
- Added CSS transform-based zoom for smooth scaling

### Fixed
- Improved form validation messages
- Better error handling for malformed Mermaid syntax
- Enhanced accessibility with ARIA labels

## [1.0.0] - 2024-10-XX

### Initial Release
- Core VSM diagram creation functionality
- Dynamic step management (add, remove, insert)
- Mermaid code generation
- Import/export capabilities
- Markdown file save feature
- Docker containerization
- Automated testing suite
- Comprehensive documentation

### Features
- Interactive web form for VSM creation
- Automatic flow efficiency calculations
- Process time and lead time metrics
- Wait time visualization
- Copy to clipboard functionality
- Responsive design with Tailwind CSS
- Zero backend dependencies

---

## Upgrade Instructions

### From 1.0.0 to 1.1.0

1. **Pull the latest Docker image**:
   ```bash
   docker pull buckeye90/vsm-generator-app:1.1.0
   ```

2. **Stop the old container**:
   ```bash
   docker stop vsm-generator-container
   docker rm vsm-generator-container
   ```

3. **Run the new version**:
   ```bash
   docker run -d -p 8080:8080 --name vsm-generator-container buckeye90/vsm-generator-app:1.1.0
   ```

4. **Clear browser cache** to ensure new assets load properly

### Breaking Changes
- None in this release

### Migration Notes
- Existing diagrams can be imported without modification
- All previous functionality remains unchanged
- New features are additive only

---

## Future Roadmap

### Planned for 1.2.0
- [ ] SVG export option
- [ ] Pan/drag functionality for large diagrams
- [ ] Dark mode support
- [ ] Collaborative features
- [ ] Multi-language support

### Under Consideration
- [ ] Template library
- [ ] Advanced metrics dashboard
- [ ] Integration with project management tools
- [ ] API for programmatic access
- [ ] Mobile app version

---

## Support

For issues, feature requests, or questions:
- Open an issue in the GitHub repository
- Check the [documentation](docs/docs-index.md)
- Review the [security guide](docs/security.md)

---

*For detailed commit history, see the git log.*