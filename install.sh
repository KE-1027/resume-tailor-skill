#!/bin/sh
# install.sh — Install resume-tailor-skill to detected AI platforms
# Usage:
#   ./install.sh                      # Auto-detect and install
#   ./install.sh --platform claude    # Install for specific platform
#   ./install.sh --all                # Install to all detected platforms
#   ./install.sh --dry-run            # Show what would be installed without doing it

set -eu

SKILL_NAME="resume-tailor-skill"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m' YELLOW='\033[1;33m' BLUE='\033[0;34m' BOLD='\033[1m' NC='\033[0m'
else
    GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

info()    { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }

# Platform detection
detect_platform() {
    detected=""
    [ -d "$HOME/.claude" ]       && detected="$detected claude"
    [ -d "$HOME/.gemini" ]       && detected="$detected gemini"
    [ -d "$HOME/.config/goose" ] && detected="$detected goose"
    [ -d "$HOME/.config/opencode" ] && detected="$detected opencode"
    [ -d "$HOME/.copilot" ]      && detected="$detected copilot"
    echo "$detected"
}

# Install path for platform
install_path() {
    case "$1" in
        claude)   echo "$HOME/.claude/skills/$SKILL_NAME" ;;
        gemini)   echo "$HOME/.gemini/skills/$SKILL_NAME" ;;
        goose)    echo "$HOME/.config/goose/skills/$SKILL_NAME" ;;
        opencode) echo "$HOME/.config/opencode/skills/$SKILL_NAME" ;;
        copilot)  echo "$HOME/.copilot/skills/$SKILL_NAME" ;;
        universal) echo "$HOME/.agents/skills/$SKILL_NAME" ;;
    esac
}

platform_display() {
    case "$1" in
        claude) echo "Claude Code" ;;
        gemini) echo "Gemini CLI" ;;
        goose) echo "Goose" ;;
        opencode) echo "OpenCode" ;;
        copilot) echo "GitHub Copilot" ;;
        universal) echo "Universal (.agents/skills)" ;;
    esac
}

do_install() {
    platform="$1"
    dest="$(install_path "$platform")"
    name="$(platform_display "$platform")"

    info "Installing for $name → $dest"
    mkdir -p "$(dirname "$dest")"
    rm -rf "$dest"
    cp -R "$SKILL_DIR" "$dest"
    success "Installed: $name"
}

# --- Main ---
echo ""
printf "${BOLD}Resume Tailor Skill — Installer${NC}\n\n"

PLATFORM="${1:-auto}"
DRY_RUN=false

case "$PLATFORM" in
    --dry-run) DRY_RUN=true; PLATFORM="auto" ;;
    --platform) PLATFORM="${2:-auto}" ;;
    --all) PLATFORM="all" ;;
    --help|-h)
        echo "Usage: ./install.sh [--platform <name>] [--all] [--dry-run]"
        echo ""
        echo "Platforms: claude, gemini, goose, opencode, copilot, universal"
        exit 0
        ;;
esac

if [ "$PLATFORM" = "auto" ]; then
    platforms="$(detect_platform)"
    if [ -z "$platforms" ]; then
        warn "No platforms detected. Installing to universal path."
        platforms="universal"
    fi
elif [ "$PLATFORM" = "all" ]; then
    platforms="$(detect_platform) universal"
else
    platforms="$PLATFORM"
fi

if [ "$DRY_RUN" = true ]; then
    echo "Dry run — would install to:"
    for p in $platforms; do
        echo "  $(platform_display "$p"): $(install_path "$p")"
    done
    exit 0
fi

for p in $platforms; do
    do_install "$p"
done

echo ""
success "Installation complete!"
echo ""
printf "  To use, invoke: ${BOLD}/resume-tailor-skill${NC}\n"
echo ""
