#!/bin/bash

# Anti-Fraud Platform Setup Script
# Bootstrap all required CLIs and dependencies

set -e

echo "🚀 Setting up Anti-Fraud Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo -e "${YELLOW}Windows detected. Some commands may need to be run in PowerShell.${NC}"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Please install Node.js 20+ from https://nodejs.org${NC}"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}Node.js version 20+ required. Current: $(node --version)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3.12+ not found. Please install from https://python.org${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION < 3.12" | bc -l)" -eq 1 ]; then
    echo -e "${RED}Python 3.12+ required. Current: $(python3 --version)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $(python3 --version)${NC}"

# Install Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel@latest
    echo -e "${GREEN}✓ Vercel CLI installed${NC}"
else
    echo -e "${GREEN}✓ Vercel CLI already installed${NC}"
fi

# Install EAS CLI
if ! command -v eas &> /dev/null; then
    echo "Installing EAS CLI..."
    npm install -g @expo/eas-cli@latest
    echo -e "${GREEN}✓ EAS CLI installed${NC}"
else
    echo -e "${GREEN}✓ EAS CLI already installed${NC}"
fi

# Install Supabase CLI
if ! command -v supabase &> /dev/null; then
    echo "Installing Supabase CLI..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install supabase/tap/supabase
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://supabase.com/install.sh | sh
    else
        echo -e "${YELLOW}Please install Supabase CLI manually from https://supabase.com/docs/guides/cli${NC}"
    fi
    echo -e "${GREEN}✓ Supabase CLI installed${NC}"
else
    echo -e "${GREEN}✓ Supabase CLI already installed${NC}"
fi

# Install project dependencies
echo "Installing project dependencies..."

# Web dependencies
echo "Installing web dependencies..."
cd web
npm install
cd ..

# API dependencies
echo "Installing API dependencies..."
cd api
python3 -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Mobile dependencies
echo "Installing mobile dependencies..."
cd mobile
npm install
cd ..

echo -e "${GREEN}✓ All dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo -e "${YELLOW}⚠ Please update .env with your actual values${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Initialize Supabase (if not already done)
if [ ! -d "supabase" ]; then
    echo "Initializing Supabase..."
    supabase init
    echo -e "${GREEN}✓ Supabase initialized${NC}"
else
    echo -e "${GREEN}✓ Supabase already initialized${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual values"
echo "2. Run 'make dev' to start development servers"
echo "3. Run 'supabase start' to start local database"
echo "4. Run 'make test' to verify everything works"
echo ""
echo "For deployment:"
echo "- Web: 'make deploy-web'"
echo "- API: 'make deploy-api'"
echo "- Mobile: 'make deploy-mobile'"
echo ""
echo -e "${YELLOW}Remember to set up your Vercel and EAS accounts!${NC}"