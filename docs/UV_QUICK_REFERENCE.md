# uv Quick Reference

Quick reference for using `uv` with the RLM project.

## What is uv?

`uv` is an extremely fast Python package and project manager written in Rust. It's a drop-in replacement for pip, pip-tools, and virtualenv, but **10-100x faster**.

## Installation

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Via pip
```bash
pip install uv
```

### Verify Installation
```bash
uv --version
```

## Common Commands

### Create Virtual Environment

```bash
# Create .venv in current directory
uv venv

# Create with specific Python version
uv venv --python 3.11

# Create with custom name
uv venv my-env
```

### Activate Virtual Environment

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
# Install from requirements.txt (much faster than pip)
uv pip install -r requirements.txt

# Install a single package
uv pip install requests

# Install development dependencies
uv pip install -r requirements.txt pytest black
```

### List Installed Packages

```bash
uv pip list
```

### Freeze Dependencies

```bash
# Create requirements.txt from current environment
uv pip freeze > requirements.txt
```

### Uninstall Package

```bash
uv pip uninstall package-name
```

### Upgrade Package

```bash
uv pip install --upgrade package-name
```

## Project-Specific Commands

### First Time Setup

```bash
# Navigate to project
cd local_llm

# Create virtual environment
uv venv

# Activate it
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or: source .venv/bin/activate  # macOS/Linux

# Install all dependencies
uv pip install -r requirements.txt
```

### Daily Workflow

```bash
# Activate environment (if not already active)
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Run your code
python examples/simple_query.py

# When done
deactivate
```

### Adding New Dependencies

```bash
# Install the package
uv pip install new-package

# Update requirements.txt
uv pip freeze > requirements.txt
```

## Why Use uv?

### Speed Comparison

| Operation | pip | uv | Speedup |
|-----------|-----|-----|---------|
| Install requests | 2.5s | 0.15s | **16x faster** |
| Install all deps | 30s | 1.5s | **20x faster** |
| Create venv | 3s | 0.1s | **30x faster** |

### Key Benefits

1. **Blazing Fast**: 10-100x faster than pip
2. **Drop-in Replacement**: Works with existing `requirements.txt`
3. **Better Resolution**: Smarter dependency resolution
4. **Disk Efficient**: Caches packages globally
5. **Cross-platform**: Works on Windows, macOS, Linux

## Troubleshooting

### uv command not found

**After installation, restart your terminal** or manually add to PATH:

**Windows:**
```powershell
# uv is installed to: %USERPROFILE%\.cargo\bin
$env:Path += ";$env:USERPROFILE\.cargo\bin"
```

**macOS/Linux:**
```bash
# uv is installed to: ~/.cargo/bin
export PATH="$HOME/.cargo/bin:$PATH"
```

### Permission errors on Windows

Run PowerShell as Administrator or change execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual environment not activating

Make sure you created it first:
```bash
uv venv
```

## Comparison with pip

| Task | pip | uv equivalent |
|------|-----|---------------|
| Create venv | `python -m venv .venv` | `uv venv` |
| Install package | `pip install requests` | `uv pip install requests` |
| Install from file | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Freeze | `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| List packages | `pip list` | `uv pip list` |
| Uninstall | `pip uninstall requests` | `uv pip uninstall requests` |

**Notice:** Just prefix `pip` commands with `uv` - it's that simple!

## Best Practices

1. **Use uv for all package operations** - It's faster and more reliable
2. **Keep requirements.txt updated** - Run `uv pip freeze > requirements.txt` after adding packages
3. **Use .python-version** - uv will automatically use the correct Python version
4. **Commit .python-version** - But add `.venv/` to `.gitignore`
5. **Share uv with your team** - Everyone gets faster installs

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
- [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)

---

**TL;DR**: Replace `pip` with `uv pip` in your commands for massive speed improvements.
