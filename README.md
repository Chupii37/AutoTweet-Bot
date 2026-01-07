# Auto Tweet Bot for X.com

⚠️ **DISCLAIMER** ⚠️

This software is provided for **educational and informational purposes only**. By using this bot, you agree to the following:

1. **Twitter/X Compliance**: You are responsible for ensuring your use complies with [Twitter's Terms of Service](https://twitter.com/en/tos) and [Automation Rules](https://help.twitter.com/en/rules-and-policies/twitter-automation).
2. **Account Risk**: Use of automation may result in account suspension or termination. The authors are **not responsible** for any account penalties.
3. **No Warranty**: This software is provided "as is" without warranty of any kind.
4. **No Financial Advice**: Content generated is for entertainment/educational purposes only, not financial advice.
5. **Legal Compliance**: You must comply with all applicable laws in your jurisdiction.

**USE AT YOUR OWN RISK. THE AUTHORS ASSUME NO LIABILITY.**

## Features

- 🕐 **Random Scheduling**: Posts exactly 2 times per week at random times
- 📊 **Multiple Categories**: Crypto, funny, finance, social, and sociology content
- 🤖 **Smart Content Generation**: Weighted random selection with validation
- 📝 **Tweet History**: Keeps track of all posted tweets
- 🔒 **Safety Features**: Content validation, profanity filtering, rate limiting
- 🧪 **Testing Mode**: Dry run mode for safe testing
- 📈 **Analytics**: Logging and monitoring capabilities

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Chupii37/AutoTweet-Bot.git
   cd AutoTweet-Bot
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```
    **Windows**
   ```bash
   venv\Scripts\activate
   ```
    **macOS/Linux**
   ```bash
   source venv/bin/activate
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   **Edit .env with your Twitter API credentials**
5. **Initialize data files:**
   **Create data directories**
   ```bash
   mkdir -p src/content/data storage/logs storage/images
   ```
   **Add sample data (copy from samples/)**
   ```bash
   cp samples/*.json src/content/data/
   
## Twitter API Setup
1. Apply for a Twitter Developer Account at developer.twitter.com
2. Create a new Project and App
3. Generate API Keys and Access Tokens
4. Enable OAuth 1.0a with "Read and Write" permissions
5. Copy credentials to your .env file

## Usage
**Basic Commands:**

  **Run a single test tweet (dry run by default)**
  ```bash
  python src/main.py --once
  ```
  **Start the scheduler**
  ```bash
  python src/main.py
  ```
  **List scheduled tweets**
  ```bash
  python src/main.py --list-scheduled
  ```
  **Run with dry mode (no actual posting)**
  ```bash
  DRY_RUN=True python src/main.py
  ```
  **Run validations**
  ```bash
  python -c "from src.utils.validators import run_validations; run_validations()"
  ```
