# How to Run the RLM System

## Quick Start

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

### Step 2: Install Dependencies

```bash
cd local_llm
pip install -r requirements.txt
```

### Step 3: Run Basic Tests

Verify everything works:

```bash
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

## Troubleshooting

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

**Fix**: Install dependencies
```bash
pip install -r requirements.txt
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
