# 🚨 AIOS v2 Git History Cleanup Guide

**CRITICAL: Remove exposed credentials from git history**

## Step 1: Install BFG Repo-Cleaner

```bash
# On macOS
brew install bfg

# Or download directly
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
```

## Step 2: Create Fresh Backup

```bash
cd /Users/arielmuslera/Development/Projects
cp -r bluelabel-AIOS-V2 bluelabel-AIOS-V2-backup-$(date +%Y%m%d)
```

## Step 3: Create Secrets File to Remove

Create a file `secrets-to-remove.txt` with the exposed credentials:

```
sk-proj-DLZUH9x31
sk-ant-api03-odcklFFz
AIzaSyAw6wWezz1TDJGG9xCUKZgmvPdWXF0KJlw
1094552487600-r4r8i8kmbl2hbh57q4pdjpdqt01sm5pr.apps.googleusercontent.com
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
4OTTl7HGyJqo8WEZR7fE6CqXgGqsOKdxQcw-_NrUNEd0EZGrQlWNQA
ABaBagx1VxGWQxrUy9hE6J8WEJSoQE-Tg9x88R0yxFfzQqSjLg
```

## Step 4: Clean Repository

```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2

# Remove secrets from all commits
bfg --replace-text secrets-to-remove.txt

# Alternative: Remove entire files if needed
bfg --delete-files .env
bfg --delete-files gmail_token.json
bfg --delete-files token.json

# Clean up the repository
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Step 5: Force Push Changes

⚠️ **WARNING: This rewrites history. Coordinate with team members!**

```bash
# Force push to all branches
git push --force --all
git push --force --tags
```

## Step 6: Notify Team

Send this message to all team members:

```
URGENT: Git history has been rewritten to remove exposed credentials.
Everyone must:
1. Delete local repository
2. Re-clone fresh: git clone [repository-url]
3. Update .env with new credentials
4. Never commit credentials again
```

## Step 7: Verify Cleanup

```bash
# Search for any remaining secrets
git log -p | grep -E "(sk-proj|sk-ant|AIzaSy|apps.googleusercontent|GOCSPX)"

# Should return empty
```

## Step 8: Implement Safeguards

```bash
# Install pre-commit hooks
pip install pre-commit detect-secrets

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Initialize
detect-secrets scan > .secrets.baseline
pre-commit install
```

## Alternative: Start Fresh Repository

If history is too contaminated:

```bash
# Create new repo with clean history
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2
rm -rf .git

# Initialize fresh
git init
git add .
git commit -m "Initial commit - cleaned repository"
git remote add origin [new-repository-url]
git push -u origin main
```

## Post-Cleanup Checklist

- [ ] All exposed credentials rotated
- [ ] New credentials stored securely
- [ ] .env.example updated
- [ ] .gitignore comprehensive
- [ ] Pre-commit hooks installed
- [ ] Team notified
- [ ] Backup retained
- [ ] Production credentials in secrets manager

## Emergency Contacts

If credentials were compromised:
- OpenAI: Regenerate at platform.openai.com
- Anthropic: Regenerate at console.anthropic.com
- Google: Revoke at console.cloud.google.com
- Monitor for unauthorized usage immediately

---

**Remember: NEVER commit credentials to version control again!**