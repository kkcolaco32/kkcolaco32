# Security Policy

## Supported Versions
| Version | Supported          |
| ------- | ----------------- |
| latest  | :white_check_mark:|

## Reporting a Vulnerability
If you discover a security vulnerability, please report it by emailing [security@yourdomain.com](mailto:security@yourdomain.com) or opening a private security advisory on GitHub. We will respond promptly and coordinate a fix.

## Responsible Disclosure
- Do **not** publicly disclose vulnerabilities before a fix is released.
- Provide as much detail as possible to help us reproduce and address the issue.

## Security Best Practices
- All secrets and credentials must be stored in environment variables (never in code or git).
- Use the provided `.env.example` as a template and never commit real secrets.
- Keep dependencies up to date and monitor for vulnerabilities (see below).

## Dependency Management
- Use `pip-audit` or `pip install --upgrade` regularly to check for vulnerable dependencies.
- Review and update `requirements.txt` as needed.

## Code Security
- Avoid use of `eval`, `exec`, or other unsafe code execution.
- All user input is sanitized and validated.
- No hardcoded credentials or secrets in the codebase.

## Compliance
- This project follows [OpenSSF Best Practices](https://openssf.org/best-practices/).
- All sensitive data is handled according to [OWASP Top 10](https://owasp.org/www-project-top-ten/) recommendations.

## Contact
For any security concerns, contact: [kevincolaco@gofynd.com]