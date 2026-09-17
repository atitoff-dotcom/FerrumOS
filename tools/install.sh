#!/usr/bin/env bash
# ==============================================================================
#  🛡️  FerrumOS Fast Installer for Linux & macOS
# ==============================================================================
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/atitoff-dotcom/FerrumOS/main/tools/install.sh | bash
#   ./install.sh --uninstall
# ==============================================================================

set -euo pipefail

REPO="atitoff-dotcom/FerrumOS"
INSTALL_DIR="${FERRUM_INSTALL_DIR:-$HOME/.ferrum/bin}"
VERSION="latest"
UNINSTALL=0
DRY_RUN=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --uninstall)
            UNINSTALL=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ================================================================"
echo "   🛡️  FerrumOS — Reactive Embedded OS & Studio Suite for IoT"
echo "  ================================================================"
echo -e "${NC}"

if [ "$UNINSTALL" -eq 1 ]; then
    echo -e "${YELLOW}🗑️  Removing FerrumOS from '$INSTALL_DIR'...${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}   [OK] Deleted directory: $INSTALL_DIR${NC}"
    fi
    if [ -L "$HOME/.local/bin/ferrum" ]; then
        rm -f "$HOME/.local/bin/ferrum"
        echo -e "${GREEN}   [OK] Removed symlink $HOME/.local/bin/ferrum${NC}"
    fi
    echo -e "\n${GREEN}✅ FerrumOS has been successfully uninstalled.${NC}\n"
    exit 0
fi

# 1. OS & Architecture Detection
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

if [ "$OS" != "linux" ] && [ "$OS" != "darwin" ]; then
    echo "❌ Unsupported operating system: $OS"
    exit 1
fi

case "$ARCH" in
    x86_64|amd64)
        ARCH="x86_64"
        ;;
    aarch64|arm64)
        ARCH="aarch64"
        ;;
    *)
        echo "❌ Unsupported architecture: $ARCH (supported: x86_64, aarch64)"
        exit 1
        ;;
esac

BINARY_NAME="ferrum-${OS}-${ARCH}"
if [ "$OS" = "darwin" ]; then
    BINARY_NAME="ferrum-macos-${ARCH}"
fi

echo -e "🔍 Detected system: ${GRAY}${OS} (${ARCH})${NC}"

# 2. Download URL
if [ "$VERSION" = "latest" ]; then
    DOWNLOAD_URL="https://github.com/${REPO}/releases/latest/download/${BINARY_NAME}"
else
    DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${VERSION}/${BINARY_NAME}"
fi

echo -e "📦 Target binary:   ${GRAY}${BINARY_NAME}${NC}"
echo -e "📂 Install folder:  ${GRAY}${INSTALL_DIR}${NC}"

if [ "$DRY_RUN" -eq 1 ]; then
    echo -e "\n${YELLOW}[DryRun] Would download '${DOWNLOAD_URL}' to '${INSTALL_DIR}/ferrum' and add to PATH.${NC}\n"
    exit 0
fi

# 3. Create Directory
mkdir -p "$INSTALL_DIR"
TARGET_EXE="${INSTALL_DIR}/ferrum"
TEMP_EXE="${INSTALL_DIR}/ferrum.tmp"

# 4. Download
echo -e "${CYAN}⬇️  Downloading FerrumOS executable...${NC}"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$DOWNLOAD_URL" -o "$TEMP_EXE"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TEMP_EXE" "$DOWNLOAD_URL"
else
    echo "❌ Neither curl nor wget found in PATH."
    exit 1
fi

mv "$TEMP_EXE" "$TARGET_EXE"
chmod +x "$TARGET_EXE"
echo -e "${GREEN}   [OK] Downloaded and installed: $TARGET_EXE${NC}"

# Optional symlink to ~/.local/bin
if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    ln -sf "$TARGET_EXE" "$HOME/.local/bin/ferrum"
    echo -e "${GREEN}   [OK] Created symlink in ~/.local/bin/ferrum${NC}"
fi

# 5. Shell Profile PATH configuration
add_to_profile() {
    local PROFILE_FILE="$1"
    local LINE="export PATH=\"\$PATH:${INSTALL_DIR}\""
    if [ -f "$PROFILE_FILE" ] && ! grep -qs "$INSTALL_DIR" "$PROFILE_FILE"; then
        echo "" >> "$PROFILE_FILE"
        echo "# FerrumOS CLI" >> "$PROFILE_FILE"
        echo "$LINE" >> "$PROFILE_FILE"
        echo -e "${GREEN}   [OK] Added to $PROFILE_FILE${NC}"
    fi
}

CURRENT_SHELL="$(basename "${SHELL:-bash}")"
if [ "$CURRENT_SHELL" = "zsh" ]; then
    add_to_profile "$HOME/.zshrc"
else
    add_to_profile "$HOME/.bashrc"
    add_to_profile "$HOME/.profile"
fi

# 6. USB / Serial permissions check (for Linux ESP32 flashing)
if [ "$OS" = "linux" ]; then
    USER_GROUPS="$(groups 2>/dev/null || true)"
    if [[ "$USER_GROUPS" != *"dialout"* ]] && [[ "$USER_GROUPS" != *"uucp"* ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Notice for USB device flashing:${NC}"
        echo -e "   Your user is not in the 'dialout' group."
        echo -e "   To allow flashing ESP32 nodes via USB serial, run:"
        echo -e "   ${CYAN}sudo usermod -aG dialout \$USER${NC}"
    fi
fi

# 7. Done
echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo -e "  To get started, reload your shell or run:"
echo -e "    ${YELLOW}export PATH=\"\$PATH:${INSTALL_DIR}\"${NC}"
echo ""
echo -e "  Commands:"
echo -e "    ${YELLOW}ferrum --help${NC}   ${GRAY}- View all CLI commands${NC}"
echo -e "    ${YELLOW}ferrum studio${NC}   ${GRAY}- Launch Web Control Center${NC}"
echo -e "    ${YELLOW}ferrum scan${NC}     ${GRAY}- Scan local network for active ESP32 nodes${NC}"
echo ""
