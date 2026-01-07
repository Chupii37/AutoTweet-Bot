Disclaimer
This bot is for educational purposes. Use responsibly and in compliance with Twitter's Terms of Service. The authors are not responsible for any account suspensions or violations.

## **5. Setup Script `setup.sh`**

```bash
#!/bin/bash
# Auto Tweet Bot Setup Script

set -e  # Exit on error

echo "🚀 Setting up Auto Tweet Bot for X.com"
echo "======================================"

# Check Python version
echo "Checking Python version..."
python --version || { echo "Python not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directory structure
echo "Creating directory structure..."
mkdir -p storage/logs storage/images src/content/data

# Create .gitkeep files
touch storage/.gitkeep
touch storage/logs/.gitkeep
touch storage/images/.gitkeep
touch src/content/data/.gitkeep

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your Twitter API credentials."
else
    echo "✅ .env file already exists."
fi

# Create sample data files
echo "Creating sample data files..."
if [ ! -f src/content/data/crypto_topics.json ]; then
    echo "Creating crypto_topics.json..."
    cat > src/content/data/crypto_topics.json << 'EOF'
{
  "topics": ["Bitcoin", "Ethereum", "DeFi", "NFTs", "Web3"],
  "templates": ["Thoughts on {topic} in 2024? 🤔 #Crypto"],
  "hashtags": ["#Crypto", "#Bitcoin", "#Ethereum"]
}
EOF
fi

# Run validations
echo "Running validations..."
python -c "
from src.utils.validators import run_validations
results = run_validations()
if not results['overall_valid']:
    print('❌ Setup validation failed!')
    for error in results['errors']:
        print(f'  - {error}')
    exit(1)
else:
    print('✅ All validations passed!')
"

echo ""
echo "======================================"
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Twitter API credentials"
echo "2. Test with: python src/main.py --once"
echo "3. Run the bot: python src/main.py"
echo ""
echo "For help: python src/main.py --help"
echo "======================================"
