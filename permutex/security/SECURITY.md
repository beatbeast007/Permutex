[security.md](https://github.com/user-attachments/files/24147136/security.md)
# Security Policy

Thank you for your interest in the security of **Permutex**. We take the security of our software and the ethical application of our tools very seriously.

## Supported Versions

We only provide security updates and patches for the latest stable release. Please ensure you are using the most recent version before reporting a bug.

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.0.x   | :white_check_mark: | **Active** (Security Updates & Bug Fixes) |
| < 1.0   | :x:                | **End of Life** (No Support) |

---

## Project Purpose & Ethical Guidelines

**Permutex** is an advanced context-aware atomic password profiling engine designed for:

1.  **Authorized Red Teaming:** Generating target-specific wordlists for authorized penetration testing engagements.
2.  **Blue Team Defense:** Auditing password strength policies and identifying weak credentials before attackers do.
3.  **Educational Research:** Understanding the mechanics of password complexity and mutation patterns.
4.  **Forensic Analysis:** Assisting authorized digital forensics investigations where password recovery is legally mandated.

### Prohibited Use
* **Unauthorized Access:** Using this tool against targets without explicit, written permission is illegal and strictly prohibited.
* **Malicious Intent:** Using this tool for cyberstalking, harassment, or unauthorized data exfiltration is a violation of our policy and potentially local/international laws.

*The developers of Permutex disclaim all responsibility for any damage, loss, or legal consequences resulting from the misuse of this software.*

---

## Reporting a Vulnerability

If you discover a security vulnerability within the **Permutex** codebase itself (e.g., buffer overflows, unsafe file handling, command injection risks), please follow these steps:

1.  **Do NOT open a public GitHub issue.** We want to fix the issue before it can be exploited.
2.  Email the details directly to our security maintainer:
    * **Email:** `abhishekbhagat2107@gmail.com`
    * **Subject:** `[SECURITY] Permutex Vulnerability Report`
3.  Please include:
    * A description of the vulnerability.
    * Steps to reproduce the issue (PoC).
    * The version of Permutex you are using.
    * Your operating system/environment.

### Disclosure Policy
* We will acknowledge receipt of your report within **48 hours**.
* We will provide an estimated timeline for a fix.
* We ask that you maintain confidentiality until a patch is released (typically within 30 days).

---

## Scope for Bug Reports

### In Scope
* Code execution vulnerabilities within the CLI or Generator.
* Memory leaks or unsafe handling of large datasets leading to system instability.
* Insecure handling of user input that could lead to local privilege escalation.

### Out of Scope
* Bugs related to third-party libraries (unless a simple update fixes it).
* "Vulnerabilities" that require the attacker to already have root/admin access to the machine running Permutex.
* Issues related to the *output* files (e.g., generating "bad" passwords is the tool's job, not a bug).

---

## Disclaimer

This project is open-source software provided "as is", without warranty of any kind, express or implied. By downloading and using Permutex, you agree to use it responsibly and in compliance with all applicable laws.
