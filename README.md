
# AI Terminal Assistant

![Python](https://img.shields.io/badge/pythone/License?** 🌊  
Stop memorizing hundreds of cryptic lines across CMD, PowerShell & Bash!  
**AI Terminal Assistant (AIT)** transforms your plain English into safe, instant shell commands – smart, cross-platform, and productivity-boosting. 🚀

***

## ✨ Features

- **AI-Powered Command Generation**: Convert natural language to shell commands instantly.[1]
- **Safety First**: Built-in safety filters prevent destructive operations.[3]
- **Cross-Platform**: Supports CMD, PowerShell, and Unix-like shells (Bash, Zsh, Fish).[1]
- **Python Environment Detection**: Detects venv, Conda, Pipenv, and Poetry environments.[1]
- **Run or Preview Mode**: Choose to execute commands or preview them first.[1]
- **Clean & Modular Architecture**: Ready for enhancements like LangChain or RAG.[3]

***

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SidduJadhav/Terminal-Assitant.git
   cd Terminal-Assitant
   ```
2. **Install in development mode**
   ```bash
   pip install -e .
   ```
3. **(Optional) Install globally**
   ```bash
   pip install .
   ```

***

## 🚀 Usage

Once installed, simply use:

```bash
ait "list all files"
```

**Example commands:**
```bash
ait "show current directory"
ait "create a folder named test"
ait "search for text 'hello' in all files"
ait "clear the terminal screen"
```

### Suggest-Only Mode

Preview commands without executing them:
```bash
ait --suggest-only "delete all temporary files"
```

***

## 🛡️ Safety & Permissions

- Commands are validated before running.[3]
- High-risk commands are flagged or blocked.[3]
- Confirmation prompts before destructive actions.[3]

***

## 🗂 Project Structure

```
Terminal-Assitant/
├── ai_terminal/         # Core source code
│   ├── assistant.py     # Main orchestration
│   ├── ai_engine.py     # AI command generation
│   ├── executor.py      # Command executor
│   ├── shell_utils.py   # Shell detection & utilities
│   ├── safety.py        # Safety filters
│   └── config.py        # Config settings
├── tests/               # (Optional) Tests
├── setup.py             # Package setup
└── README.md            # Project documentation
```

***

## 🧪 Testing

Run tests with:
```bash
pytest tests/
```

***



## 📜 License

Licensed under the **MIT License** – free to use, modify, and share.[2]

---

[1] https://img.shields.io/badge/python-3.11-blue
[2] https://img.shields.io/badge/License-MIT-green
[3] https://img.shields.io/badge/ps
