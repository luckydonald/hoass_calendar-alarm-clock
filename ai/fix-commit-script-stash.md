# Fix for commit.sh Stash Error

## Problem
The commit script was using `git stash push --staged` and `git stash pop` to temporarily save staged changes. When trying to pop the stash, it encountered conflicts because the files had changed.

## Solution
Changed the approach to be simpler and more reliable:

### Before (Problematic):
```bash
# Save staged changes
git stash push --staged -m "commit-script-staged-backup"

# ... do commits ...

# Restore staged changes
git stash pop  # ← This could fail with conflicts
```

### After (Fixed):
```bash
# Save list of staged files and unstage them
STAGED_FILES=$(git diff --cached --name-only)
git reset HEAD

# ... do commits ...

# Re-stage the files that were originally staged
echo "$STAGED_FILES" | while IFS= read -r file; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        git add "$file"
    fi
done
```

## Why This Works Better
1. **No stash conflicts**: We don't use stash at all, just track which files were staged
2. **Simpler**: Just unstage → commit → re-stage
3. **More reliable**: No patch application that can fail
4. **Cleaner**: No stash entries left behind

## Cleanup Old Stash (if needed)
If you have the old stash entry from the failed run:

```bash
# List stashes
git stash list

# If you see "commit-script-staged-backup", drop it:
git stash drop stash@{0}  # or whatever index it is
```

## Testing
The script should now work without the stash pop error:
```bash
make commit
```

