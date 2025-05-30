# 🚨 URGENT: Google OAuth2 Credential Exposure Remediation

**Date:** May 30, 2025  
**Severity:** CRITICAL  
**Status:** IN PROGRESS

## What Happened

GitGuardian detected exposed Google OAuth2 credentials in commit `6879388` pushed at May 30, 2025 07:22:53 UTC.

The file `scripts/aios_v2_credential_setup.py` contained hardcoded credentials including:
- Google OAuth Client Secret: `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`
- Google OAuth Client ID: `1094552487600-r4r8i8kmbl2hbh57q4pdjpdqt01sm5pr`

## Immediate Actions Taken

1. ✅ Identified the exposed file
2. ✅ Removed the file from the repository (`git rm scripts/aios_v2_credential_setup.py`)
3. 🔄 Need to commit and push the removal
4. 🔄 Need to clean git history

## Required Remediation Steps

### 1. Revoke Exposed Credentials (DO THIS NOW!)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Find the OAuth 2.0 Client ID ending in `...sm5pr`
4. Click on it and then click "Delete" or "Regenerate"
5. Create new OAuth credentials

### 2. Clean Git History

```bash
# Use BFG Repo Cleaner to remove the file from history
brew install bfg  # If not installed
cd /Users/arielmuslera/Development/Projects/bluelabel-autopilot
bfg --delete-files aios_v2_credential_setup.py
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

### 3. Update All References

- Update any local `.env` files with new credentials
- Update any deployment configurations
- Notify any team members who might have the old credentials

### 4. Security Audit

- Check for any other exposed credentials
- Review all commits for sensitive data
- Enable GitHub secret scanning if not already enabled

## Prevention Measures

1. **Never hardcode credentials** - Always use environment variables
2. **Use .gitignore** - Ensure all `.env` files are ignored
3. **Pre-commit hooks** - Install tools to detect secrets before commit
4. **Secret scanning** - Enable GitHub's secret scanning feature

## Lessons Learned

The credential setup helper script was meant to help manage credentials but ironically contained hardcoded credentials for "scanning" purposes. This is a critical mistake - even example or test credentials should never be hardcoded.

## Next Steps

1. Complete credential rotation immediately
2. Clean git history
3. Implement pre-commit hooks to prevent future exposures
4. Review all other scripts for similar issues