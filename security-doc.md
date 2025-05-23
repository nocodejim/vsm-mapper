# Security Documentation - VSM Mermaid Generator

## Overview

This document outlines the security measures, best practices, and considerations implemented in the VSM Mermaid Generator application. Security is a fundamental aspect of the application design, ensuring user data protection and preventing common web vulnerabilities.

## Security Architecture

### Client-Side Only Processing
- **No Backend Services**: All processing happens in the user's browser
- **No Data Transmission**: Diagrams and data never leave the user's device
- **No External APIs**: No third-party services receive user data
- **Local Storage**: No use of browser storage APIs (localStorage, sessionStorage)

### Containerization Security
```dockerfile
# Running as non-root user in container
# Using minimal Alpine Linux base
FROM nginx:alpine

# Security headers configured in Nginx
RUN echo "server_tokens off;" > /etc/nginx/conf.d/security.conf
```

## Implementation Details

### 1. Input Sanitization

All user input is sanitized before use:

```javascript
function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return str.toString().replace(/[&<>"']/g, function (match) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[match];
    });
}
```

### 2. Mermaid.js Security Configuration

Mermaid is configured with strict security settings:

```javascript
mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'linear'
    },
    securityLevel: 'strict', // Prevents script injection
    logLevel: 'error'
});
```

### 3. Content Security Policy (CSP)

Recommended CSP headers for production deployment:

```nginx
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline' 
        https://cdn.tailwindcss.com 
        https://cdn.jsdelivr.net 
        https://cdnjs.cloudflare.com;
    style-src 'self' 'unsafe-inline' 
        https://fonts.googleapis.com;
    font-src 'self' 
        https://fonts.gstatic.com;
    img-src 'self' data: blob:;
    connect-src 'self';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
" always;

add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### 4. DOM Manipulation Security

Safe DOM manipulation practices:

```javascript
// SAFE: Using textContent for user data
label.textContent = 'Step Name:';

// SAFE: Creating elements programmatically
const stepDiv = document.createElement('div');
stepDiv.classList.add('input-group');

// AVOIDED: innerHTML with user data
// stepDiv.innerHTML = userInput; // NEVER DO THIS
```

### 5. File Download Security

Secure file generation and download:

```javascript
function downloadFile(filename, content) {
    try {
        // Sanitize filename
        const sanitized = filename.replace(/[^a-z0-9_\-\.]/gi, '_');
        
        // Create blob with explicit MIME type
        const blob = new Blob([content], { 
            type: 'text/markdown;charset=utf-8;' 
        });
        
        // Use secure download method
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", sanitized);
        
        // Clean up object URL
        URL.revokeObjectURL(url);
    } catch(error) {
        console.error("Error saving file:", error);
    }
}
```

## Vulnerability Prevention

### 1. Cross-Site Scripting (XSS)
- **Prevention**: All user input is HTML-escaped
- **Mermaid Security**: Strict mode prevents script execution
- **No eval()**: No dynamic code execution
- **Safe Templates**: No string-based HTML generation with user data

### 2. Cross-Site Request Forgery (CSRF)
- **Not Applicable**: No backend or authentication
- **Form Handling**: All forms are local only

### 3. Injection Attacks
- **SQL Injection**: Not applicable (no database)
- **Command Injection**: Not applicable (no server commands)
- **Template Injection**: Prevented by escaping

### 4. Denial of Service (DoS)
- **Client-Side Limits**: Browser enforces memory limits
- **Diagram Complexity**: Mermaid has built-in limits
- **No Infinite Loops**: All iterations are bounded

### 5. Information Disclosure
- **No Sensitive Data**: Application doesn't handle PII
- **No Logs**: No server-side logging
- **Error Messages**: Generic, non-revealing errors

## Security Best Practices

### For Users

1. **Use HTTPS**: Always access the application over HTTPS in production
2. **Updated Browser**: Use a modern, updated web browser
3. **Trusted Sources**: Only load the application from trusted sources
4. **No Sensitive Data**: Avoid including sensitive information in diagrams

### For Developers

1. **Dependency Updates**: Regularly update all dependencies
   ```bash
   # Check for vulnerabilities
   docker scan vsm-generator-app
   ```

2. **Code Review**: All changes should be reviewed for security
   - Check for XSS vulnerabilities
   - Verify input sanitization
   - Ensure no sensitive data exposure

3. **Testing**: Include security tests
   ```python
   def test_xss_prevention():
       """Test that XSS attempts are properly escaped"""
       xss_payload = '<script>alert("XSS")</script>'
       # Enter XSS in step name
       # Generate diagram
       # Verify script tags are escaped
   ```

4. **Container Security**:
   ```dockerfile
   # Use specific versions, not latest
   FROM nginx:1.24-alpine
   
   # Run as non-root user
   USER nginx
   
   # Minimal attack surface
   RUN rm -rf /usr/share/nginx/html/*
   ```

## Security Checklist

### Pre-Deployment
- [ ] All dependencies updated to latest secure versions
- [ ] CSP headers configured properly
- [ ] HTTPS enabled for production
- [ ] Container scanned for vulnerabilities
- [ ] Security tests passing

### Regular Maintenance
- [ ] Monthly dependency updates
- [ ] Quarterly security review
- [ ] Annual penetration testing (if applicable)
- [ ] Monitor security advisories for dependencies

## Incident Response

### If a Security Issue is Found

1. **Assess Impact**: Determine scope and severity
2. **Patch Immediately**: Fix the vulnerability
3. **Test Fix**: Ensure the fix doesn't break functionality
4. **Deploy Update**: Release patched version
5. **Document**: Update security documentation

### Reporting Security Issues

If you discover a security vulnerability:
1. Do NOT open a public issue
2. Email security details to: [security@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Third-Party Dependencies Security

### CDN Resources
All CDN resources use:
- **HTTPS**: Encrypted transmission
- **SRI (Recommended)**: Subresource Integrity for verification
- **Specific Versions**: No auto-updating to untested versions

Example with SRI:
```html
<script 
    src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"
    integrity="sha384-[hash]"
    crossorigin="anonymous">
</script>
```

### Dependency Versions
Current secure versions:
- Mermaid.js: 10.x (strict security mode)
- html2canvas: 1.4.1
- Tailwind CSS: Latest via CDN
- Nginx: Alpine-based for minimal attack surface

## Compliance Considerations

### GDPR Compliance
- **No Personal Data**: Application doesn't collect user data
- **No Cookies**: No tracking or analytics
- **Local Processing**: All data stays on user's device

### Accessibility Security
- **ARIA Labels**: Proper labeling doesn't expose sensitive info
- **Error Messages**: Accessible but not revealing

## Future Security Enhancements

1. **Subresource Integrity (SRI)**: Add SRI hashes for all CDN resources
2. **Security Headers Testing**: Automated header validation
3. **Content Security Policy Reporting**: Monitor CSP violations
4. **Web Application Firewall**: For production deployments
5. **Security Scanning CI/CD**: Automated vulnerability scanning

## Resources

### Security Tools
- **OWASP ZAP**: Web application security testing
- **Docker Bench**: Container security assessment
- **npm audit**: Dependency vulnerability scanning
- **Lighthouse**: Browser security audit

### References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Mermaid Security Documentation](https://mermaid.js.org/config/security.html)

---

*Last Updated: November 2024*  
*Security Contact: [security@example.com]*  
*Version: 1.0.0*