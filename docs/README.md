# 📚 BlueLabel Documentation

Welcome to the BlueLabel documentation! This guide will help you navigate our documentation structure and find the information you need.

## 🗂 Directory Structure

```
/docs/
├── system/                    # Core system documentation
│   ├── ROLES_AND_RESPONSIBILITIES.md
│   ├── AGENT_ORCHESTRATION_GUIDE.md
│   ├── YAML_WORKFLOW_TEMPLATES.md
│   └── templates/            # System-wide templates
│
├── phases/                    # Phase-specific documentation
│   ├── current/              # Symlink to current phase
│   └── PHASE_6.13/
│       ├── plan.md
│       ├── sprints/
│       │   ├── SPRINT_1/
│       │   └── SPRINT_2/
│       ├── features/
│       └── architecture/
│           └── signoffs/
│
├── agents/                    # Agent-specific documentation
│   ├── ca/
│   │   ├── onboarding.md
│   │   └── checklist.md
│   ├── cc/
│   └── wa/
│
├── dev/                       # Development documentation
│   ├── testing/
│   ├── architecture/
│   └── guidelines/
│
└── security/                  # Security documentation
    ├── best_practices.md
    └── audit_reports/
```

## 📖 Quick Links

- [System Documentation](system/) - Core system documentation and guides
- [Current Phase](phases/current/) - Documentation for the current development phase
- [Agent Guides](agents/) - Agent-specific documentation and checklists
- [Development Guide](dev/) - Development guidelines and best practices
- [Security](security/) - Security documentation and audit reports

## 🔍 Finding Information

- **New to the project?** Start with the [Agent Orchestration Guide](system/AGENT_ORCHESTRATION_GUIDE.md)
- **Looking for your role?** Check [Roles and Responsibilities](system/ROLES_AND_RESPONSIBILITIES.md)
- **Current sprint info?** Visit [Current Phase](phases/current/)
- **Security concerns?** Review [Security Best Practices](security/best_practices.md)

## 📝 Contributing

When adding new documentation:
1. Place it in the appropriate directory based on its purpose
2. Follow the established naming conventions
3. Update this README if adding new major sections
4. Include cross-references to related documents

## 🔄 Version Control

- All documentation is version controlled in Git
- Major changes should be documented in commit messages
- Cross-reference changes in related documents
- Keep the structure clean and organized 