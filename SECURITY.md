# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in System//Zero, please report it by:

1. **DO NOT** open a public issue
2. Email security details to the maintainers privately
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Within 7 days with assessment
- **Fix Timeline**: Critical vulnerabilities patched within 30 days

## Security Considerations

### Immutable Logging
- Hash chains in audit logs are tamper-evident but not cryptographically signed
- Log files should be stored with appropriate filesystem permissions (read-only after write)
- Consider additional encryption for logs containing sensitive UI data

### Template Validation
- YAML templates are loaded from the filesystem without sandboxing
- Only load templates from trusted sources
- Validate template structure before deployment

### Accessibility API Access
- Requires system-level permissions to read UI state
- May capture sensitive information from applications
- Ensure compliance with organizational privacy policies

### Network Exposure
- API server (`interface/api/server.py`) should only bind to localhost in production
- Use authentication/authorization for any network-exposed endpoints
- Do not expose raw logs via API without access controls

## Best Practices

1. **Principle of Least Privilege**: Run with minimal required system permissions
2. **Log Rotation**: Implement retention policies for immutable logs
3. **Access Control**: Restrict read access to captured UI trees and drift logs
4. **Monitoring**: Regularly verify hash chain integrity using `ImmutableLog.verify_integrity()`
5. **Updates**: Keep dependencies updated to address known vulnerabilities
