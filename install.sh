#!/bin/bash
set -e

echo "🚀 9Yards Agent Setup - Ubuntu 24+ Installation"
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Ubuntu 24+
if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}❌ This script is designed for Ubuntu 24+${NC}"
    exit 1
fi

UBUNTU_VERSION=$(lsb_release -rs | cut -d. -f1)
if [ "$UBUNTU_VERSION" -lt 24 ]; then
    echo -e "${YELLOW}⚠️  Warning: Ubuntu version < 24 detected. Some features may not work.${NC}"
fi

echo ""
echo "📦 Step 1: System Package Updates"
echo "-----------------------------------"
sudo apt update
sudo apt upgrade -y

echo ""
echo "📦 Step 2: Installing Base Dependencies"
echo "----------------------------------------"
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release \
    python3-pip \
    python3-venv \
    jq \
    bc

echo ""
echo "🐳 Step 3: Installing Docker"
echo "-----------------------------"
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add current user to docker group
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker installed. You may need to log out and back in for group changes.${NC}"
else
    echo -e "${GREEN}✅ Docker already installed: $(docker --version)${NC}"
fi

# Enable Docker BuildKit by default
if ! grep -q "DOCKER_BUILDKIT" ~/.bashrc; then
    echo "export DOCKER_BUILDKIT=1" >> ~/.bashrc
    echo "export COMPOSE_DOCKER_CLI_BUILD=1" >> ~/.bashrc
    echo -e "${GREEN}✅ Docker BuildKit enabled in ~/.bashrc${NC}"
fi

echo ""
echo "📦 Step 4: Installing Node.js (v20 LTS)"
echo "----------------------------------------"
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
    echo -e "${GREEN}✅ Node.js $(node -v) installed${NC}"
else
    echo -e "${GREEN}✅ Node.js $(node -v) already installed${NC}"
fi

# Install global npm packages
echo -e "${BLUE}📦 Installing global npm packages...${NC}"
npm install -g npm@latest

echo ""
echo "📦 Step 5: Installing Python 3.12+"
echo "-----------------------------------"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.12" | bc -l) )); then
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
    echo -e "${GREEN}✅ Python 3.12 installed${NC}"
else
    echo -e "${GREEN}✅ Python $(python3 --version) already installed${NC}"
fi

echo ""
echo "📦 Step 6: Installing uv (Python package manager)"
echo "--------------------------------------------------"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add to PATH
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✅ uv installed${NC}"
else
    echo -e "${GREEN}✅ uv already installed: $(uv --version)${NC}"
fi

echo ""
echo "📦 Step 7: Installing MCP Server Dependencies"
echo "----------------------------------------------"

# Chroma MCP (via uvx - installed with uv)
echo -e "${BLUE}→ Chroma MCP (will be invoked via uvx)${NC}"

# Node-based MCP servers (will be invoked via npx)
echo -e "${BLUE}→ Playwright MCP (will be invoked via npx)${NC}"
echo -e "${BLUE}→ Database MCP (will be invoked via npx)${NC}"
echo -e "${BLUE}→ Slack MCP (will be invoked via npx)${NC}"
echo -e "${BLUE}→ GitLab MCP (will be invoked via npx)${NC}"
echo -e "${GREEN}✅ MCP servers will be auto-installed on first use${NC}"

echo ""
echo "📦 Step 8: Installing Playwright Browsers"
echo "------------------------------------------"
npx -y playwright install chromium firefox
npx -y playwright install-deps
echo -e "${GREEN}✅ Playwright browsers installed${NC}"

echo ""
echo "📦 Step 9: Setting up Python Environment for Scripts"
echo "-----------------------------------------------------"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Python virtual environment created${NC}"
fi

source .venv/bin/activate

# Install Python dependencies for indexing scripts
pip install --upgrade pip
pip install \
    chromadb \
    requests \
    gitpython \
    python-gitlab

echo -e "${GREEN}✅ Python packages installed${NC}"

echo ""
echo "📦 Step 10: Creating Directory Structure"
echo "-----------------------------------------"
mkdir -p logs
mkdir -p ~/claude-code-data/chroma
mkdir -p /tmp/gitlab-index
echo -e "${GREEN}✅ Directory structure created${NC}"

echo ""
echo "📦 Step 11: Setting Permissions"
echo "--------------------------------"
chmod +x install.sh
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true
echo -e "${GREEN}✅ Script permissions set${NC}"

echo ""
echo "================================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "================================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Copy .env.example to .env and fill in your tokens:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Log out and back in (for Docker group changes)"
echo ""
echo "3. Test MCP servers:"
echo "   uvx chroma-mcp --help"
echo "   npx @playwright/mcp@latest --help"
echo ""
echo "4. Run initial indexing:"
echo "   source .venv/bin/activate"
echo "   python scripts/index-slack-knowledge.py"
echo "   python scripts/index-gitlab-repos.py"
echo ""
echo "5. Verify MCP configuration in ./.claude-plugin/plugin.json"
echo ""
echo "🚀 Ready to use enhanced agents!"
