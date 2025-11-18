# Contributing to Flamapy

Thank you for your interest in contributing to Flamapy! We welcome contributions from both individuals and organisations.

Flamapy is a modular framework, and contributions are essential to its development and long-term sustainability. This document describes the contribution process, release policy, licensing model, and plugin ecosystem guidelines.

---

## Contribution workflow

### Branching model
Flamapy follows a lightweight Gitflow-inspired model:

- **`main`** — stable production-ready releases
- **`develop`** — latest development state where contributions are integrated

### Pull Request process
1. Fork the repository and create a branch based on **`develop`**
2. Implement changes, including tests and documentation updates as needed
3. Submit a Pull Request (PR) to **`develop`**
4. Describe clearly:
   - Expected behaviour
   - Design decisions
   - Breaking changes (if any)
5. PRs must be reviewed and approved by Flamapy maintainers
6. Once stable, the `develop` branch will be merged into `main` during a release cycle

---

## Release policy
Flamapy follows **Semantic Versioning** for stable releases.  
To ensure reliability and consistency:

- **Up to two major/minor stable releases per year**
- Patch releases will only include critical bug fixes

Release announcements will be shared via the website, GitHub, and mailing channels.

---

## Types of contributions
- Bug fixes 🐛
- New features ✨
- New metamodels or plugins 🔌
- Documentation improvements 📚
- Refactoring and performance improvements ⚙️

For major contributions, please first open an **Issue** describing the motivation, design, and scope, so we can align expectations before implementation.

---

## Plugin ecosystem and licensing
Flamapy supports an open plugin ecosystem. There are two categories of plugins:

### 🔌 Plugins hosted inside the Flamapy GitHub organisation
- Must adopt the **LGPL-3.0** license
- Integrated in the official roadmap and releases
- Reviewed and maintained jointly by the core team

### 🔌 External plugins (hosted outside the organisation)
- May use **any license chosen by the authors**
- Fully compatible with Flamapy architecture
- Can be promoted to the community

If you maintain an external plugin and would like visibility (listing on the webpage, documentation, or community releases), please contact:

📧 **flamapy@us.es**

---

## Licensing model
Flamapy is distributed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**.

By submitting a Pull Request, you agree to the **implicit contribution agreement**:
- You retain copyright to your contribution
- You grant Flamapy users rights to use, modify and redistribute it under LGPL-3.0

Organisations requiring a **Contributor License Agreement (CLA)** can contact the maintainers. If not, it will be defaulting to implicit contribution agreement. 

---

## Code quality guidelines
- Follow existing code style and architecture
- Provide unit tests when applicable
- Explain design decisions in PR description
- Avoid introducing breaking changes without prior discussion
- Document new functionality

---

## Governance
- Core maintainers review and approve contributions
- Major design decisions are taken publicly via Issues and PR discussions
- Roadmap is driven by community needs and research/industry applications
- All new contributors teams are welcome to the core team

---

Thank you again for supporting Flamapy.  
Together we build an open, extensible, and high-quality ecosystem for automated feature-model analysis!


