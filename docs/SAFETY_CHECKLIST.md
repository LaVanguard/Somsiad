# Project Safety Checklist

## 🛡️ Before Every Commit

Use this checklist to ensure you don't break the project:

### 1. Code Quality
- [ ] Code runs without syntax errors
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] No debug `print()` statements left in code
- [ ] No commented-out code blocks (clean them up)

### 2. Django Checks
```bash
# Run these commands before committing:

# System check
python manage.py check

# Check for missing migrations
python manage.py makemigrations --check --dry-run

# Test migrations work
python manage.py migrate

# Start server (verify no errors)
python manage.py runserver
```

### 3. Git Status Review
```bash
# What's being committed?
git status

# Review actual changes
git diff

# Review staged changes
git diff --cached
```

### 4. Files NOT to Commit
- [ ] `__pycache__/` directories
- [ ] `.env` files
- [ ] `db.sqlite3` database file
- [ ] Personal API keys
- [ ] Large binary files (>500KB)

---

## 🧪 Before Merging to Develop/Main

### 1. Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term

# Check coverage percentage
coverage report
```

### 2. Code Quality (Optional but Recommended)
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### 3. Update Branch
```bash
# Ensure you have latest changes
git checkout develop
git pull origin develop

# Merge your feature
git merge --no-ff feature/your-branch

# If conflicts, resolve them carefully!
```

### 4. Final Verification
- [ ] Server starts: `python manage.py runserver`
- [ ] No console errors when loading pages
- [ ] All tests pass: `pytest`
- [ ] Migrations applied: `python manage.py migrate`

---

## 🚨 Emergency Recovery

### If You Committed Something Bad (Not Pushed)
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Fix the issue
# Then commit again
git add .
git commit -m "Fixed version"
```

### If You Pushed Something Bad
```bash
# Create revert commit (safer than force-push)
git revert HEAD

# Or revert specific commit
git revert <commit-hash>

# Push revert
git push origin <branch>
```

### If Main Branch is Broken
```bash
# Switch to last known good state
git checkout main
git reset --hard <last-good-commit-hash>

# Or restore from tag
git checkout v0.1.0

# Create recovery branch
git checkout -b hotfix/restore-main
```

---

## 🔒 CI/CD Guardrails

GitHub Actions will automatically:
- ✅ Run tests on every push
- ✅ Check Django system
- ✅ Verify migrations
- ✅ Lint code
- ✅ Scan for security issues
- ❌ **Block merge if tests fail**

**See CI status:** Check GitHub Actions tab in repo

---

## 📋 Sprint Release Checklist

Before releasing a sprint to `main`:

### Pre-Release
- [ ] All sprint features complete
- [ ] All tests passing (100%)
- [ ] Documentation updated (README, PRD)
- [ ] No known bugs or blockers
- [ ] Code reviewed (self-review at minimum)

### Release Process
```bash
# 1. Update develop
git checkout develop
git pull origin develop

# 2. Run full test suite
pytest --cov=. --cov-report=term

# 3. Merge to main
git checkout main
git pull origin main
git merge --no-ff develop -m "Release Sprint X: [Feature Name]"

# 4. Tag release
git tag -a v0.X.0 -m "Sprint X: [Feature Name]"

# 5. Push with tags
git push origin main --tags

# 6. Verify CI passes
# Check GitHub Actions
```

### Post-Release
- [ ] Verify production deployment (if auto-deploy enabled)
- [ ] Test production URL
- [ ] Monitor logs for errors
- [ ] Update project board/issues

---

## 🎯 Quick Commands Reference

### Safe Operations
```bash
# Check status (always safe)
git status
git log --oneline
git branch -a

# View changes (safe)
git diff
git show HEAD

# Switch branches (safe if no uncommitted changes)
git checkout <branch>
```

### Potentially Dangerous (Use Carefully)
```bash
# Discard changes (cannot undo!)
git reset --hard

# Force push (NEVER on main!)
git push --force

# Delete branch (permanent!)
git branch -D <branch>
```

---

## 🆘 When to Ask for Help

If you encounter:
- Merge conflicts you can't resolve
- Tests failing with unclear errors
- Git in a weird state (detached HEAD, etc.)
- Accidentally deleted important code
- Need to revert multiple commits

**Don't guess!** It's better to ask than to make it worse.

---

## 📊 Project Health Indicators

### Green (Healthy)
- ✅ All tests passing
- ✅ CI/CD pipeline green
- ✅ No merge conflicts
- ✅ Server starts without errors
- ✅ Coverage >70%

### Yellow (Warning)
- ⚠️ Some tests skipped
- ⚠️ Coverage 50-70%
- ⚠️ Minor linting issues
- ⚠️ Outdated dependencies

### Red (Action Needed)
- ❌ Tests failing
- ❌ Server won't start
- ❌ Merge conflicts
- ❌ Security vulnerabilities
- ❌ Coverage <50%

---

**Remember:** It's always better to be safe than sorry. When in doubt, create a backup branch before making risky changes!

```bash
# Create safety backup
git checkout -b backup/before-risky-change
git checkout <original-branch>
# Now proceed with risky change
```

---

**Last Updated:** 11.10.2024
**Author:** Mike @LaVanguard
