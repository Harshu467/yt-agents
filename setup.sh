#!/bin/bash

# YT-Agents Setup Script
# Complete setup for zero-cost YouTube automation

echo "🚀 YT-Agents Setup Script"
echo "=========================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Install system dependencies
echo "🔧 Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    echo "  Installing via apt (Linux)..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    echo "✅ FFmpeg installed"
fi

if command -v brew &> /dev/null; then
    echo "  Installing via brew (Mac)..."
    brew install ffmpeg
    echo "✅ FFmpeg installed"
fi

echo ""
echo "📥 Installing Ollama..."
echo "   Download from: https://ollama.ai"
echo "   Then run: ollama pull llama2"
echo ""

echo "📥 Installing Piper TTS..."
pip install piper-tts
echo "✅ Piper TTS installed"
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env (edit with your API keys)"
else
    echo "⚠️  .env already exists (skipping)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your API keys (all optional)"
echo "2. Install Ollama: https://ollama.ai"
echo "3. Run: ollama pull llama2"
echo "4. Start: python main.py"
echo ""
echo "💡 Pro tip: Run without API keys for demo mode!"
