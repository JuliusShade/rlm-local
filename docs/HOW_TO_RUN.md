# How to Run the RLM System

## Prerequisites

### Install uv (Recommended)

`uv` is a fast Python package and project manager. It's recommended for managing the virtual environment.

**Install uv:**

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Or via pip:**
```bash
pip install uv
```

Verify installation:
```bash
uv --version
```

**See [uv Quick Reference](UV_QUICK_REFERENCE.md) for more uv commands and tips.**

## Quick Start

### Step 0: Set Up Python Virtual Environment (Using uv)

**Create and activate virtual environment:**

```bash
# Navigate to project directory
cd local_llm

# Create virtual environment with uv
uv venv

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate
```

**Install dependencies with uv:**
```bash
# uv will install dependencies much faster than pip
uv pip install -r requirements.txt
```

**Alternative: Using standard Python venv**

If you prefer not to use uv:
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 1: Ensure Ollama is Running

Make sure Ollama is running with the Qwen2.5-Coder 14B model:

```bash
ollama serve
```

Verify the model is available:
```bash
ollama list
```

You should see `qwen2.5-coder:14b` in the list.

### Step 2: Run Basic Tests

Verify everything works:

```bash
uv run python test_basic.py
OR
python test_basic.py
```

Expected output:
```
================================================================================
RLM BASIC TESTS
================================================================================

Testing Ollama client connection...
[PASS] Client connection successful

Testing simple LLM completion...
Response: Hello, RLM!
[PASS] Simple completion successful

Testing full RLM pipeline with simple question...
(This will take a minute, the model is processing...)

Solution: ...
Critique Score: .../100
Complexity: SIMPLE
[PASS] RLM pipeline successful

================================================================================
TEST SUMMARY
================================================================================
Client Connection: [PASS]
Simple Completion: [PASS]
Full RLM Pipeline: [PASS]

[PASS] ALL TESTS PASSED
```

If all tests pass, you're ready to use the RLM system!

## Running Examples

### Example 1: Simple Query (No Recursion)

```bash
python examples/simple_query.py
```

This demonstrates a simple question that the model answers directly without recursive decomposition.

**What to expect:**
- Question assessed as SIMPLE
- Direct answer provided
- No recursion tree (depth 0)
- Fast execution (one main reasoning pass)

### Example 2: Complex Analysis (With Recursion)

```bash
python examples/complex_analysis.py
```

This demonstrates a complex code analysis task that triggers recursive decomposition.

**What to expect:**
- Question assessed as COMPLEX
- Decomposed into 2-5 sub-questions
- Each sub-question may trigger further recursion
- Recursion tree visualized in output
- Multiple LM calls visible in logs
- Slower execution (due to multiple passes)

### Example 3: Code Refactoring (Full Recursion Tree)

```bash
python examples/code_refactoring.py
```

Software engineering specific example showing full recursive reasoning.

**What to expect:**
- Complex refactoring task
- Multi-level recursion
- Detailed recursion tree in console
- Results saved to `refactoring_output.json`

## Using the RLM System in Your Own Code

### Basic Usage

Create a Python script:

```python
from src.rlm import RLMController

# Create controller
controller = RLMController()

# Your task
task = "Analyze this function and suggest improvements: ..."

# Run
result = controller.run(task)

# Access results
print("Solution:", result.solution)
print("Confidence:", result.critique.score, "/100")
```

### With Custom Configuration

```python
from src.rlm import RLMController

controller = RLMController(config={
    "rlm": {
        "max_recursion_depth": 4,  # Allow deeper recursion
    },
    "generation": {
        "reasoner_temp": 0.8,  # More creative
    },
    "logging": {
        "enable": True,
        "level": "DEBUG",  # Verbose logging
    },
})

result = controller.run(task)
```

### Accessing Detailed Results

```python
result = controller.run(task)

# Solution
print(result.solution)

# Critique
if result.critique:
    print(f"Score: {result.critique.score}")
    print(f"Gaps: {result.critique.gaps}")
    print(f"Uncertainties: {result.critique.uncertainties}")

# Recursion tree analysis
if result.recursion_tree:
    print(f"Complexity: {result.recursion_tree.complexity}")
    print(f"Sub-questions: {result.recursion_tree.sub_questions}")
```

## Understanding the Output

### Console Output

When you run an example, you'll see:

1. **Pipeline Start**: Shows the task
2. **Stage Execution**: Each stage (Planner, Retriever, Reasoner, Critic) runs
3. **Recursion Logging** (inside Reasoner):
   - `[depth N]` shows recursion depth
   - `SIMPLE` or `COMPLEX` shows complexity assessment
   - Decomposition and composition steps logged
4. **Final Results**:
   - Recursion tree visualization
   - Final solution
   - Critique summary with score

### Recursion Tree

Example tree structure:

```
├─ [depth 0] [COMPLEX] Main question
│  → answer preview...
  ├─ [depth 1] [SIMPLE] Sub-question 1
  │  → answer...
  ├─ [depth 1] [COMPLEX] Sub-question 2
  │  ├─ [depth 2] [SIMPLE] Sub-sub-question
  │  └─ [depth 2] [SIMPLE] Sub-sub-question
  └─ [depth 1] [SIMPLE] Sub-question 3
```

Each node is an LM call. The tree shows how the question was decomposed and solved recursively.

## Configuration Options

Edit `src/rlm/config.py` or pass config dict:

```python
{
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:14b",
        "timeout": 120,
    },
    "rlm": {
        "max_recursion_depth": 3,  # Max recursion levels
    },
    "generation": {
        "reasoner_temp": 0.7,      # Reasoning temperature
        "decompose_temp": 0.4,     # Decomposition temperature
        "critic_temp": 0.3,        # Evaluation temperature
    },
    "logging": {
        "enable": True,
        "level": "INFO",           # DEBUG, INFO, WARNING, ERROR
        "show_recursion_tree": True,
    },
}
```

## Virtual Environment Management

### Deactivating the Virtual Environment

When you're done working:
```bash
deactivate
```

### Reactivating Later

```bash
cd local_llm

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### Python Version

This project uses Python 3.9+ (specified in `.python-version`). uv will automatically use the correct Python version if available on your system.

## Troubleshooting

### Virtual Environment Issues

**Problem**: Cannot activate virtual environment

**Fix**: Make sure you created it first
```bash
uv venv  # or: python -m venv .venv
```

**Problem**: `uv` command not found after installation

**Fix**: Restart your terminal or add uv to PATH:
```bash
# Windows: uv is typically installed to %USERPROFILE%\.cargo\bin
# macOS/Linux: uv is typically installed to ~/.cargo/bin
```

### Cannot Connect to Ollama

```
ConnectionError: Cannot connect to Ollama at http://localhost:11434/v1
```

**Fix**: Start Ollama
```bash
ollama serve
```

### Model Not Found

```
Error: model not found
```

**Fix**: Pull the model
```bash
ollama pull qwen2.5-coder:14b
```

### Import Errors

```
ModuleNotFoundError: No module named 'pydantic'
```

**Fix 1**: Make sure virtual environment is activated
```bash
# Check if activated (you should see (.venv) in prompt)
# If not, activate it:
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux
```

**Fix 2**: Install dependencies in the virtual environment
```bash
uv pip install -r requirements.txt
# or: pip install -r requirements.txt
```

### Timeout Errors

```
TimeoutError: Request timed out after 120s
```

**Fix**: Increase timeout in config
```python
config={"ollama": {"timeout": 300}}
```

## Next Steps

- Read the full [Usage Guide](usage_guide.md) for detailed information
- Read [Architecture Details](../goals/rlm_architecture.md) to understand the design
- Check out [uv Quick Reference](UV_QUICK_REFERENCE.md) for fast package management
- Try creating your own questions and tasks
- Experiment with different configuration settings
- Extend the system (add RAG, tools, etc.)

## Tips for Best Results

1. **Clear Questions**: Specific questions get better results
2. **Appropriate Depth**: Match `max_recursion_depth` to complexity
3. **Monitor LM Calls**: Watch the recursion tree to understand decomposition
4. **Tune Temperatures**: Adjust based on your use case
5. **Enable Logging**: Use DEBUG level to see everything

---

## Test Results

The system has been tested and verified:

| Test | Status |
|------|--------|
| Client Connection | ✓ PASS |
| Simple Completion | ✓ PASS |
| Full RLM Pipeline | ✓ PASS |

All core functionality is working correctly!
