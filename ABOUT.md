# RLM-Local: Recursive Language Model

A **true Recursive Language Model (RLM)** implementation using local Qwen2.5-Coder 14B via Ollama.

## What is a Recursive Language Model?

Unlike traditional LLMs that try to answer complex questions in one pass, RLMs **recursively decompose** complex questions into simpler sub-questions, solving each recursively, then composing the results. This mirrors how humans break down difficult problems into manageable subtasks.

**Key Principle**: "RLMs defer reasoning over large context by making recursive LM calls."

## Architecture

```
User Task → Planner → Retriever → RecursiveReasoner → Critic
                                        ↓
                                [Recursively calls LM
                                 for sub-questions,
                                 composes results]
```

The magic happens inside the **RecursiveReasoner** stage, which:
1. Assesses if a question is SIMPLE or COMPLEX
2. If COMPLEX: decomposes into sub-questions
3. Recursively solves each sub-question
4. Composes sub-answers into a final answer

## Quick Start

### Prerequisites

1. **Ollama running locally** with Qwen2.5-Coder 14B:
   ```bash
   ollama pull qwen2.5-coder:14b
   ollama serve
   ```

2. **Python 3.9+** with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Examples

```bash
# Simple question (no recursion)
python examples/simple_query.py

# Complex analysis (triggers recursion)
python examples/complex_analysis.py

# Code refactoring (SE-specific)
python examples/code_refactoring.py
```

## Basic Usage

```python
from src.rlm import RLMController

# Create controller
controller = RLMController()

# Run RLM on a task
result = controller.run("Your question or task here")

# Access results
print(result.solution)  # Final answer
print(result.critique.score)  # Confidence score (0-100)
print(result.recursion_tree)  # Recursion structure
```

## Example: Simple vs Complex Questions

### Simple Question (Answered Directly)
```python
task = "Explain the difference between deep copy and shallow copy in Python."
result = controller.run(task)
# → Assessed as SIMPLE, answered directly (no recursion)
```

### Complex Question (Triggers Recursion)
```python
task = """
Analyze this code and identify issues, suggest improvements,
and explain design patterns used:

class UserManager:
    def create_user(self, name, email):
        self.db.save({"name": name, "email": email})
        self.send_welcome_email(email)
        self.log_creation(name)
"""

result = controller.run(task)
# → Assessed as COMPLEX
# → Decomposed into sub-questions like:
#    - "What are the issues in this code?"
#    - "What improvements can be made?"
#    - "What design patterns are used?"
# → Each sub-question answered recursively
# → Results composed into final answer
```

## Recursion Tree Example

For the complex question above, the RLM might create:

```
"Analyze this code..." [COMPLEX]
├─ "What issues exist?" [depth 1] → answer
├─ "What improvements?" [depth 1] → [COMPLEX]
│  ├─ "How to fix SRP violation?" [depth 2] → answer
│  └─ "How to apply DI?" [depth 2] → answer
└─ "What patterns are used?" [depth 1] → answer
```

Each node represents an LM call. The system automatically decides whether to recurse or answer directly.

## Configuration

Customize behavior in `src/rlm/config.py` or pass config overrides:

```python
controller = RLMController(config={
    "rlm": {
        "max_recursion_depth": 4,  # Default: 3
    },
    "generation": {
        "reasoner_temp": 0.8,      # Default: 0.7
    },
})
```

### Key Settings

- `max_recursion_depth`: Maximum recursion levels (default: 3)
- `reasoner_temp`: Temperature for reasoning (default: 0.7)
- `decompose_temp`: Temperature for decomposition (default: 0.4)
- `critic_temp`: Temperature for evaluation (default: 0.3)

## Project Structure

```
src/
├── rlm/
│   ├── client.py          # Ollama API wrapper
│   ├── controller.py      # Main orchestrator
│   ├── state.py           # State management
│   ├── config.py          # Configuration
│   ├── stages/            # Pipeline stages
│   │   ├── planner.py     # Task decomposition
│   │   ├── retriever.py   # Context retrieval (stubbed)
│   │   ├── reasoner.py    # RECURSIVE reasoning (core RLM)
│   │   └── critic.py      # Self-evaluation
│   └── prompts/           # Prompts for each stage
└── utils/
    └── logging.py         # Structured logging

examples/                  # Example scripts
docs/                      # Documentation
tests/                     # Tests
```

## How It Works

### 1. Planner Stage
Analyzes the task and creates a structured plan with key questions and success criteria.

### 2. Retriever Stage
Retrieves relevant context (currently stubbed, ready for RAG integration).

### 3. RecursiveReasoner Stage (Core RLM Logic)
This is where the recursion happens:

```python
def recursive_reason(question, context, depth):
    # Base case: max depth or simple question
    if depth >= max_depth or is_simple(question):
        return direct_answer(question)

    # Recursive case: decompose and recurse
    sub_questions = decompose(question)
    sub_answers = [recursive_reason(sq, context, depth+1)
                   for sq in sub_questions]

    # Compose sub-answers
    return compose(question, sub_answers)
```

### 4. Critic Stage
Evaluates the final solution, assigns a confidence score (0-100), and identifies gaps/uncertainties.

## Key Features

- **True Recursive Reasoning**: Recursion happens inside the reasoner, not at the pipeline level
- **Automatic Complexity Assessment**: LM decides whether to recurse or answer directly
- **Depth-Limited**: Prevents infinite recursion (configurable max depth)
- **Transparent**: Logs entire recursion tree for debugging
- **Extensible**: Easy to add RAG, tools, or multi-model support
- **Local-First**: Runs entirely on your local Ollama instance

## Future Extensions

- **RAG Integration**: Replace stubbed retriever with vector DB
- **Tool Calling**: Add tool execution stage for code execution, API calls
- **Multi-Model**: Route different stages to different models
- **Persistent Memory**: Maintain context across multiple queries

## Requirements

- Python 3.9+
- Ollama running locally
- Qwen2.5-Coder 14B model (or compatible model)
- Dependencies: `requests`, `pydantic`

## Troubleshooting

**"Cannot connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check the endpoint: http://localhost:11434/v1

**"Model not found"**
- Pull the model: `ollama pull qwen2.5-coder:14b`
- Or change model in config

**Recursion too shallow/deep**
- Adjust `max_recursion_depth` in config
- Tune `decompose_temp` (lower = more consistent decomposition)

## Documentation

- [Architecture Details](goals/rlm_architecture.md) - Detailed architecture explanation
- [Usage Guide](docs/usage_guide.md) - Comprehensive usage guide with examples

## License

MIT

## Contributing

This is a research implementation. Feel free to extend and experiment!

---

**Built with local LLMs for true privacy and control.**
