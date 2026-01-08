# RLM Usage Guide

Complete guide to running and using the Recursive Language Model system.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Running Examples](#running-examples)
4. [Understanding the Output](#understanding-the-output)
5. [Custom Usage](#custom-usage)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Install Ollama

If you haven't already, install Ollama from https://ollama.ai

### Step 2: Pull the Model

```bash
ollama pull qwen2.5-coder:14b
```

### Step 3: Start Ollama

```bash
ollama serve
```

Leave this running in a terminal.

### Step 4: Install Python Dependencies

```bash
cd local_llm
pip install -r requirements.txt
```

## Quick Start

### Verify Connection

Test that everything is working:

```bash
python -c "from src.rlm.client import OllamaClient; OllamaClient().validate_connection(); print('✓ Connected successfully')"
```

If you see "✓ Connected successfully", you're ready to go!

## Running Examples

### Example 1: Simple Query

This demonstrates a simple question that should NOT trigger recursion:

```bash
cd local_llm
python examples/simple_query.py
```

**Expected behavior:**
- Question assessed as SIMPLE
- Answered directly without decomposition
- No recursion tree (depth 0)

### Example 2: Complex Analysis

This demonstrates a complex question that SHOULD trigger recursive decomposition:

```bash
python examples/complex_analysis.py
```

**Expected behavior:**
- Question assessed as COMPLEX
- Decomposed into 2-5 sub-questions
- Each sub-question may trigger further recursion
- Recursion tree shown in logs
- Final answer composed from sub-answers

### Example 3: Code Refactoring

Software engineering specific example:

```bash
python examples/code_refactoring.py
```

**Expected behavior:**
- Complex refactoring task decomposed
- Multiple levels of recursion
- Detailed output saved to `refactoring_output.json`

## Understanding the Output

### Console Output Structure

The RLM system provides detailed logging:

```
================================================================================
RLM PIPELINE STARTING
================================================================================

Task: [Your task here]

============================================================
▶ Planner
============================================================
[Planner execution]
✓ Planner complete

============================================================
▶ Retriever
============================================================
[Retriever execution]
✓ Retriever complete

============================================================
▶ RecursiveReasoner
============================================================
[depth 0] Processing: [Main question]
→ Assessed as COMPLEX, decomposing...
→ Decomposed into 3 sub-questions
→ Sub-question 1/3
  [depth 1] Processing: [Sub-question 1]
  → Assessed as SIMPLE, answering directly
→ Sub-question 2/3
  [depth 1] Processing: [Sub-question 2]
  → Assessed as COMPLEX, decomposing...
  ... [further recursion]
→ Composing 3 sub-answers
✓ RecursiveReasoner complete

============================================================
▶ Critic
============================================================
[Critic evaluation]
✓ Critic complete

================================================================================
FINAL RESULTS
================================================================================

Recursion Tree:
├─ [depth 0] [COMPLEX] Main question
│  → [answer preview...]
  ├─ [depth 1] [SIMPLE] Sub-question 1
  │  → [answer...]
  ├─ [depth 1] [COMPLEX] Sub-question 2
  │  ├─ [depth 2] [SIMPLE] Sub-sub-question 1
  │  └─ [depth 2] [SIMPLE] Sub-sub-question 2
  └─ [depth 1] [SIMPLE] Sub-question 3

Solution:
[Final composed solution]

Critique Summary:
  Score: 85/100
  Gaps identified:
    - [Gap 1]
  Uncertainties:
    - [Uncertainty 1]
```

### Recursion Tree Explanation

Each node in the tree represents an LM call:

- `[depth N]`: Recursion depth (0 = root question)
- `[SIMPLE]` or `[COMPLEX]`: Complexity assessment
- Question text
- `→ answer preview`: Brief preview of the answer

**Tree Structure:**
- Parent → Child relationships show decomposition
- Depth increases as questions are decomposed
- SIMPLE questions get direct answers
- COMPLEX questions trigger further decomposition

### Critique Scores

- **90-100**: Excellent, comprehensive, no significant gaps
- **75-89**: Good, minor gaps or uncertainties
- **60-74**: Adequate, but has notable gaps
- **40-59**: Incomplete, significant gaps
- **0-39**: Poor, major gaps or incorrect

## Custom Usage

### Basic Custom Script

```python
from src.rlm import RLMController

# Create controller
controller = RLMController()

# Your task
task = "Analyze this function and suggest improvements..."

# Run
result = controller.run(task)

# Access results
print(f"Solution: {result.solution}")
print(f"Confidence: {result.critique.score}/100")

# Check if recursion occurred
if result.recursion_tree:
    print(f"Complexity: {result.recursion_tree.complexity}")
    print(f"Sub-questions: {len(result.recursion_tree.sub_questions)}")
```

### With Custom Configuration

```python
from src.rlm import RLMController

controller = RLMController(config={
    "rlm": {
        "max_recursion_depth": 4,  # Allow deeper recursion
    },
    "generation": {
        "reasoner_temp": 0.8,  # More creative reasoning
        "decompose_temp": 0.3,  # More deterministic decomposition
    },
    "logging": {
        "enable": True,
        "level": "DEBUG",  # More verbose logging
    },
})

result = controller.run("Your task...")
```

### Accessing Detailed Results

```python
result = controller.run(task)

# Solution
print(result.solution)

# Critique details
if result.critique:
    print(f"Score: {result.critique.score}")
    print(f"Gaps: {result.critique.gaps}")
    print(f"Uncertainties: {result.critique.uncertainties}")
    print(f"Reasoning: {result.critique.reasoning}")

# Recursion tree analysis
if result.recursion_tree:
    def count_nodes(node):
        return 1 + sum(count_nodes(child) for child in node.children)

    total_lm_calls = count_nodes(result.recursion_tree)
    print(f"Total LM calls made: {total_lm_calls}")

# Plan from planner
print(f"Plan: {result.plan}")
```

## Configuration

### Configuration Options

Edit `src/rlm/config.py` or pass config dict to `RLMController`:

#### Ollama Settings

```python
{
    "ollama": {
        "base_url": "http://localhost:11434/v1",  # Ollama endpoint
        "model": "qwen2.5-coder:14b",             # Model name
        "timeout": 120,                           # Request timeout (seconds)
        "max_retries": 3,                         # Retry attempts
    }
}
```

#### RLM Behavior

```python
{
    "rlm": {
        "max_recursion_depth": 3,      # Max depth (prevents infinite loops)
        "complexity_threshold": "auto", # Let LM decide complexity
    }
}
```

#### Generation Parameters

```python
{
    "generation": {
        "planner_temp": 0.5,    # Planning temperature (0.0-1.0)
        "reasoner_temp": 0.7,   # Reasoning temperature
        "decompose_temp": 0.4,  # Decomposition temperature (lower = more consistent)
        "critic_temp": 0.3,     # Evaluation temperature (lower = more consistent)
        "max_tokens": 2048,     # Max tokens per response
    }
}
```

#### Logging

```python
{
    "logging": {
        "enable": True,               # Enable/disable logging
        "level": "INFO",              # DEBUG, INFO, WARNING, ERROR
        "show_recursion_tree": True,  # Show tree visualization
    }
}
```

### Using a Different Model

To use a different Ollama model:

```python
controller = RLMController(config={
    "ollama": {
        "model": "llama3.1:70b",  # Different model
    }
})
```

Make sure the model is pulled: `ollama pull llama3.1:70b`

### Adjusting Recursion Depth

For very complex tasks, increase max depth:

```python
controller = RLMController(config={
    "rlm": {
        "max_recursion_depth": 5,  # Allow up to 5 levels
    }
})
```

**Trade-off**: Deeper recursion = more LM calls = slower execution

## Troubleshooting

### Connection Errors

**Problem**: `ConnectionError: Cannot connect to Ollama`

**Solutions**:
1. Check Ollama is running: `ollama list`
2. Start Ollama: `ollama serve`
3. Verify endpoint: `curl http://localhost:11434/v1/models`
4. Check firewall settings

### Model Not Found

**Problem**: `Error: model not found`

**Solutions**:
1. Pull the model: `ollama pull qwen2.5-coder:14b`
2. List available models: `ollama list`
3. Use a different model in config

### Timeout Errors

**Problem**: `TimeoutError: Request timed out`

**Solutions**:
1. Increase timeout in config:
   ```python
   config={"ollama": {"timeout": 300}}
   ```
2. Use a smaller/faster model
3. Reduce `max_recursion_depth` to make fewer LM calls

### No Recursion Occurring

**Problem**: Questions assessed as SIMPLE when they should be COMPLEX

**Solutions**:
1. Rephrase question to be more explicitly complex
2. Lower `decompose_temp` for more aggressive decomposition:
   ```python
   config={"generation": {"decompose_temp": 0.2}}
   ```
3. The model may genuinely assess it as simple - check the logs

### Too Much Recursion

**Problem**: Simple questions being over-decomposed

**Solutions**:
1. Reduce `max_recursion_depth`:
   ```python
   config={"rlm": {"max_recursion_depth": 2}}
   ```
2. Increase `decompose_temp` for less aggressive decomposition:
   ```python
   config={"generation": {"decompose_temp": 0.6}}
   ```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solutions**:
1. Run from project root: `cd local_llm`
2. Add to PYTHONPATH:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```
3. Or use absolute imports in custom scripts

### Low Critique Scores

**Problem**: Critique scores consistently low

**Explanation**: The critic is intentionally harsh to provide honest assessment.

**If scores seem unfairly low**:
- Increase `critic_temp` for less harsh evaluation:
  ```python
  config={"generation": {"critic_temp": 0.5}}
  ```

## Tips for Best Results

1. **Clear Questions**: More specific questions get better decomposition
2. **Appropriate Depth**: Match `max_recursion_depth` to task complexity
3. **Monitor LM Calls**: Check recursion tree to see if decomposition makes sense
4. **Iterate**: Adjust temperatures based on results
5. **Use Logging**: Set `level: "DEBUG"` to see detailed execution

## Next Steps

- Read [Architecture Details](../goals/rlm_architecture.md) for deeper understanding
- Experiment with different questions and configurations
- Try modifying prompts in `src/rlm/prompts/`
- Extend with RAG by implementing `RetrieverStage`

---

Happy recursing! 🚀
