# Git Workflow & Branching Strategy

## 🛡️ Project Protection Rules

**Never break `main` branch!** All development happens in feature branches.

---

## 📊 Branch Structure

```
main (production-ready, protected)
  └── develop (integration branch)
      ├── feature/sprint2-rag-core
      ├── feature/sprint3-query-history
      └── feature/sprint4-testing
```

### Branch Purposes

| Branch | Purpose | Protected | Merge Strategy |
|--------|---------|-----------|----------------|
| `main` | Production-ready code | ✅ Yes | Only from `develop` after testing |
| `develop` | Integration branch for sprints | ⚠️ Semi | From feature branches |
| `feature/*` | Individual features/sprints | ❌ No | Into `develop` after testing |
| `hotfix/*` | Emergency fixes | ❌ No | Directly to `main` (exceptional) |

---

## 🔄 Standard Workflow

### 1. Starting New Work (Sprint/Feature)

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/sprint2-rag-core

# OR create develop first (one-time)
git checkout -b develop
git push -u origin develop
git checkout -b feature/sprint2-rag-core
```

### 2. Working on Feature

```bash
# Make changes
# Stage files
git add <files>

# Commit with descriptive message
git commit -m "Add document chunking logic"

# Push to remote regularly
git push -u origin feature/sprint2-rag-core
```

### 3. Merging Feature to Develop

```bash
# Update develop
git checkout develop
git pull origin develop

# Merge feature (no fast-forward to preserve history)
git merge --no-ff feature/sprint2-rag-core

# Run tests before pushing!
pytest

# If tests pass
git push origin develop

# Delete feature branch
git branch -d feature/sprint2-rag-core
git push origin --delete feature/sprint2-rag-core
```

### 4. Releasing to Main (End of Sprint)

```bash
# Update main
git checkout main
git pull origin main

# Merge develop
git merge --no-ff develop -m "Release Sprint 2: RAG Core"

# Tag release
git tag -a v0.2.0 -m "Sprint 2 Complete: RAG integration"

# Push with tags
git push origin main --tags
```

---

## 🚨 Emergency Hotfix

```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/fix-auth-bug

# Fix bug
# ... make changes ...

# Commit
git commit -m "Fix: authentication bypass vulnerability"

# Merge to main
git checkout main
git merge --no-ff hotfix/fix-auth-bug
git push origin main

# Also merge to develop
git checkout develop
git merge --no-ff hotfix/fix-auth-bug
git push origin develop

# Delete hotfix branch
git branch -d hotfix/fix-auth-bug
```

---

## ✅ Pre-Commit Checklist

Before every commit, ensure:

- [ ] Code runs without errors: `python manage.py check`
- [ ] Migrations created if models changed: `python manage.py makemigrations --check`
- [ ] No sensitive data (API keys, passwords) in code
- [ ] No `print()` debug statements left in code
- [ ] `.gitignore` prevents `__pycache__/`, `.env`, `db.sqlite3`

---

## 🧪 Pre-Merge Checklist

Before merging to `develop` or `main`:

- [ ] All tests pass: `pytest`
- [ ] Code coverage acceptable: `pytest --cov`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Static files collected (if needed): `python manage.py collectstatic --noinput`
- [ ] Local server runs: `python manage.py runserver`
- [ ] No merge conflicts
- [ ] Branch up to date with target branch

---

## 🎯 Commit Message Convention

Use clear, descriptive commit messages:

```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting (no code change)
- `refactor:` - Code restructure (no behavior change)
- `test:` - Adding tests
- `chore:` - Build/config changes

### Examples:

```bash
# Good
git commit -m "feat: add document chunking with LangChain"
git commit -m "fix: resolve RAG context overflow error"
git commit -m "test: add E2E test for query flow"

# Bad
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

---

## 🔒 What NOT to Commit

**NEVER commit:**
- `__pycache__/` directories (tracked by `.gitignore`)
- `.env` files with secrets
- `db.sqlite3` database (use migrations instead)
- Large binary files (images, PDFs - use Git LFS or external storage)
- IDE-specific files (`.vscode/`, `.idea/`)
- Personal API keys or tokens

**Check before commit:**
```bash
git status           # See what's staged
git diff --cached    # Review staged changes
```

---

## 🚀 CI/CD Integration

GitHub Actions will automatically:
1. Run tests on every push to feature branches
2. Block merge if tests fail
3. Run tests on PR to `develop` or `main`
4. Deploy to production on push to `main`

**See:** `.github/workflows/django-tests.yml`

---

## 🆘 Recovery Commands

### Undo Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1  # Keep changes staged
# or
git reset --hard HEAD~1  # Discard changes (dangerous!)
```

### Undo Pushed Commit (Create Revert)
```bash
git revert HEAD          # Creates new commit that undoes last
git push origin main
```

### Discard Local Changes
```bash
git restore <file>       # Discard changes to specific file
git restore .            # Discard all changes
```

### Stash Changes Temporarily
```bash
git stash                # Save changes temporarily
git stash pop            # Restore stashed changes
```

### Return to Last Working State
```bash
git checkout main        # Switch to stable main
git reset --hard origin/main  # Match remote exactly
```

---

## 📈 Sprint-Based Branching

For 6-sprint project:

```bash
# Sprint 2
git checkout -b feature/sprint2-rag-core
# ... work ...
git merge into develop → test → merge to main → tag v0.2.0

# Sprint 3
git checkout -b feature/sprint3-query-history
# ... work ...
git merge into develop → test → merge to main → tag v0.3.0

# Sprint 4
git checkout -b feature/sprint4-testing
# ... work ...
git merge into develop → test → merge to main → tag v0.4.0

# And so on...
```

---

## 🏷️ Version Tagging

Use semantic versioning:

- `v0.1.0` - Sprint 1 (Auth + UI)
- `v0.2.0` - Sprint 2 (RAG Core)
- `v0.3.0` - Sprint 3 (Query History)
- `v0.4.0` - Sprint 4 (Testing)
- `v0.5.0` - Sprint 5 (CI/CD + Deployment)
- `v1.0.0` - Sprint 6 (Final Release)

```bash
git tag -a v0.2.0 -m "Sprint 2: RAG Core Complete"
git push origin v0.2.0
```

---

## 📞 Need Help?

If you break something:
1. **Don't panic** - Git tracks everything
2. Check `git reflog` to see recent actions
3. Use `git reset` or `git revert` to undo
4. Ask for help before force-pushing!

**Never use:** `git push --force` on `main` branch!

---

**Last Updated:** 11.10.2024
**Author:** Mike @LaVanguard
