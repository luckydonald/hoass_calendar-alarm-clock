#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Calendar Alarm Clock - Release Script${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "custom_components/calendar_alarm_clock/manifest.json" ]; then
    echo -e "${RED}Error: Must be run from the repository root${NC}"
    exit 1
fi

# Check for uncommitted changes (only tracked files, respects .gitignore)
if ! git diff --quiet HEAD -- || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    git status --short
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current version from latest git tag
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${YELLOW}No existing tags found, starting at v0.0.0-pre1${NC}"
    CURRENT_VERSION="0.0.0-pre0"
fi
echo -e "Current version: ${YELLOW}v${CURRENT_VERSION}${NC}"

# Parse version and bump
if [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)-pre([0-9]+)$ ]]; then
    # Pre-release version (e.g., 0.0.0-pre11 -> 0.0.0-pre12)
    MAJOR="${BASH_REMATCH[1]}"
    MINOR="${BASH_REMATCH[2]}"
    PATCH="${BASH_REMATCH[3]}"
    PRE="${BASH_REMATCH[4]}"
    NEW_PRE=$((PRE + 1))
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}-pre${NEW_PRE}"
elif [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    # Regular version - bump patch (e.g., 1.0.0 -> 1.0.1)
    MAJOR="${BASH_REMATCH[1]}"
    MINOR="${BASH_REMATCH[2]}"
    PATCH="${BASH_REMATCH[3]}"
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"
else
    echo -e "${RED}Error: Cannot parse version '${CURRENT_VERSION}'${NC}"
    echo "Expected format: X.Y.Z or X.Y.Z-preN"
    exit 1
fi

echo -e "New version: ${GREEN}v${NEW_VERSION}${NC}"
echo ""

read -p "Proceed with release? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Run tests BEFORE bumping version
echo ""
echo -e "${GREEN}🐍 Step 1: Lint and format Python${NC}"
if command -v uv &> /dev/null; then
    echo "  Running ruff format..."
    uv run ruff format custom_components/
    echo "  Running ruff check --fix..."
    uv run ruff check --fix custom_components/ || true
    echo "  Running ruff check..."
    uv run ruff check custom_components/
else
    echo -e "${RED}  Error: uv not found${NC}"
    echo "  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo ""
echo -e "${GREEN}📦 Step 2: Build frontend${NC}"
cd frontend
echo "  Installing dependencies..."
yarn install --silent
echo "  Type checking..."
yarn type-check
echo "  Building..."
yarn build
cd ..
echo "  Frontend built successfully"

# Only bump version AFTER tests pass
echo ""
echo -e "${GREEN}📝 Step 3: Update version in manifest.json${NC}"
sed -i.bak 's/"version": "[^"]*"/"version": "'"${NEW_VERSION}"'"/' custom_components/calendar_alarm_clock/manifest.json
rm -f custom_components/calendar_alarm_clock/manifest.json.bak
echo "  Updated manifest.json to ${NEW_VERSION}"

echo ""
echo -e "${GREEN}📤 Step 4: Commit and push${NC}"
git add -A
git commit -m "Release v${NEW_VERSION}"
echo "  Created commit"

git tag "v${NEW_VERSION}"
echo "  Created tag v${NEW_VERSION}"

git push origin mane
echo "  Pushed to origin/mane"

git push origin "v${NEW_VERSION}"
echo "  Pushed tag v${NEW_VERSION}"

echo ""
echo -e "${GREEN}✅ Release v${NEW_VERSION} complete!${NC}"
echo ""
echo "GitHub Actions will now:"
echo "  1. Build the frontend"
echo "  2. Create a release zip"
echo "  3. Publish to GitHub Releases"
echo ""
echo "View the release at:"
echo "  https://github.com/luckydonald/hoass_calendar-alarm-clock/releases/tag/v${NEW_VERSION}"
echo ""
echo "Install via HACS:"
echo "  https://my.home-assistant.io/redirect/hacs_repository/?owner=luckydonald&repository=hoass_calendar-alarm-clock&category=integration"

