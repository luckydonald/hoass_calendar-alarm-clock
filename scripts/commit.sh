#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

COMMIT_MSG_ERRORS="ai: updated errors"
COMMIT_MSG_QUERY="ai: updated query"
COMMIT_MSG_STEP="ai: running... ({step}-{substep})"

tmpl() {
    local tmpl_str=$1
    local -n vars=$2          # nameref to the associative array

    # Escape any characters that could be interpreted by the shell
    # when we later perform the replacement.
    local result=$tmpl_str

    for key in "${!vars[@]}"; do
        # Build the exact placeholder we want to replace: {key}
        local placeholder="{${key}}"
        # Replace *all* occurrences of that placeholder.
        result=${result//${placeholder}/${vars[$key]}}
    done

    printf '%s' "$result"
}

echo -e "${GREEN}📝 Calendar Alarm Clock - Commit Script${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "custom_components/calendar_alarm_clock/manifest.json" ]; then
    echo -e "${RED}Error: Must be run from the repository root${NC}"
    exit 1
fi

# Save any currently staged changes
STASH_STAGED=false
if [ -n "$(git diff --cached --name-only)" ]; then
    echo -e "${YELLOW}Saving staged changes...${NC}"
    git stash push --staged -m "commit-script-staged-backup"
    STASH_STAGED=true
fi

# Commit ai/query.md if it has changes
if git diff --name-only | grep -q "^ai/query.md$"; then
    echo -e "${GREEN}Committing ai/query.md...${NC}"
    git add ai/query.md
    git commit -m "${COMMIT_MSG_QUERY}"
    echo "  Done"
elif [ -f "ai/query.md" ] && git ls-files --others --exclude-standard | grep -q "^ai/query.md$"; then
    echo -e "${GREEN}Committing ai/query.md (new file)...${NC}"
    git add ai/query.md
    git commit -m "${COMMIT_MSG_QUERY}"
    echo "  Done"
else
    echo -e "${YELLOW}No changes to ai/query.md${NC}"
fi

# Commit ai/errors.md if it has changes
if git diff --name-only | grep -q "^ai/errors.md$"; then
    echo -e "${GREEN}Committing ai/errors.md...${NC}"
    git add ai/errors.md
    git commit -m "${COMMIT_MSG_ERRORS}"
    echo "  Done"
elif [ -f "ai/errors.md" ] && git ls-files --others --exclude-standard | grep -q "^ai/errors.md$"; then
    echo -e "${GREEN}Committing ai/errors.md (new file)...${NC}"
    git add ai/errors.md
    git commit -m "${COMMIT_MSG_ERRORS}"
    echo "  Done"
else
    echo -e "${YELLOW}No changes to ai/errors.md${NC}"
fi

# Restore staged changes before the final commit
if [ "$STASH_STAGED" = true ]; then
    echo -e "${YELLOW}Restoring staged changes...${NC}"
    git stash pop
fi

# Check if there are any other changes to commit
if [ -n "$(git status --porcelain)" ]; then
    # Find the last "ai: running..." commit and extract the step number
    # macOS-compatible: use sed instead of grep -P
    LAST_STEP=$(git log --oneline | grep "ai: running\.\.\. (" | head -1 | sed 's/.*ai: running\.\.\. (\([0-9]*\).*/\1/')

    if [ -z "$LAST_STEP" ]; then
        NEW_STEP=1
    else
        NEW_STEP=$((LAST_STEP + 1))
    fi

    echo -e "${GREEN}Committing remaining changes as step ${NEW_STEP}...${NC}"
    git add -u
    git add .  # Also add new files that aren't ignored
    # shellcheck disable=SC2034
    declare -A template_context=(
        [step]="$NEW_STEP"
        [substep]="1"
    )

    git commit -m "$(tmpl "${GIT_MSG_TEMPLATE}" template_context)"
    echo "  Done"
else
    echo -e "${YELLOW}No other changes to commit${NC}"
fi

echo ""
echo -e "${GREEN}✅ Commits complete!${NC}"

