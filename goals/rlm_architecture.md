# RLM Architecture - True Recursive Reasoning Implementation

## Overview
This document describes the architecture for a **Recursive Language Model (RLM)** orchestration layer using local Qwen2.5-Coder 14B via Ollama.

The system implements **true recursive reasoning** as described in RLM research: the model makes recursive LM calls to decompose complex questions into simpler sub-questions, solving each recursively, then composing the results.

## Core Principle

**"RLMs defer reasoning over large context by querying recursive LM calls"**

Unlike traditional approaches that try to solve everything in one pass, RLMs break down complex problems recursively, similar to how humans decompose difficult tasks into manageable subtasks.

## Architecture

### Pipeline Flow

```
User Task → Planner → Retriever → Reasoner (RECURSIVE) → Critic
                                      ↓
                              [Recursively calls LM
                               for sub-questions,
                               composes results]
```

**Key Insight**: Recursion happens INSIDE the Reasoner stage, not at the pipeline level.

### Core Components

1. **OllamaClient** - Clean API wrapper for OpenAI-compatible endpoint
   - Handles HTTP communication with Ollama
   - Manages retries, timeouts, error handling
   - Provides simple interface for LM calls

2. **RLMController** - Orchestrates the pipeline
   - Runs: Planner → Retriever → RecursiveReasoner → Critic
   - Manages state passing between stages
   - Logs execution flow and results

3. **Stage Pipeline**:
   - **Planner**: Decomposes task into structured plan with sub-questions
   - **Retriever**: Pluggable hook for context (stubbed initially, ready for RAG)
   - **Reasoner (RECURSIVE)**: **This is where the magic happens**
     - Analyzes task complexity
     - If complex: recursively calls LM for each sub-question
     - If simple: answers directly
     - Composes sub-answers into final solution
   - **Critic**: Self-evaluates output, assigns confidence score (0-100)

### State Management

Each stage receives and updates a state dictionary:

```python
state = {
    "task": str,              # Original user task
    "plan": str,              # Structured plan from Planner
    "context": list[str],     # Retrieved context (empty for now)
    "solution": str,          # Final solution from Reasoner
    "critique": {
        "score": int,         # 0-100 confidence
        "gaps": list[str],    # Missing information
        "uncertainties": list[str],
        "reasoning": str
    },
    "recursion_tree": dict,   # Nested structure of recursive calls
    "metadata": dict          # Execution metadata
}
```

## Recursive Reasoner Design (Core RLM Logic)

This is the heart of the system - implementing true recursive reasoning.

### Algorithm

```python
def recursive_reason(question, context, depth=0, max_depth=3):
    """
    Recursively solve questions by decomposing complex ones.
    """
    # Base cases
    if depth >= max_depth:
        return direct_answer(question, context)

    if is_simple_question(question):
        return direct_answer(question, context)

    # Recursive case: decompose and recurse
    sub_questions = decompose_question(question)  # LM call 1

    sub_answers = []
    for sub_q in sub_questions:
        # RECURSIVE LM CALLS - This is the key!
        sub_answer = recursive_reason(sub_q, context, depth+1, max_depth)
        sub_answers.append(sub_answer)

    # Compose sub-answers into final answer
    final_answer = compose_answers(question, sub_answers)  # LM call 2

    return final_answer
```

### Key Operations

1. **Complexity Assessment** (`assess_complexity`)
   - LM decides if question is SIMPLE or COMPLEX
   - Simple → answer directly
   - Complex → decompose into sub-questions

2. **Question Decomposition** (`decompose_question`)
   - LM breaks complex question into 2-5 simpler sub-questions
   - Each sub-question should be simpler than parent
   - Sub-questions should be independent when possible

3. **Recursive Calls**
   - Each sub-question triggers a new recursive call
   - Depth tracking prevents infinite recursion
   - Each call has access to original context

4. **Answer Composition** (`compose_answers`)
   - LM synthesizes sub-answers into coherent final answer
   - Must address the original question
   - Should integrate all sub-answer insights

### Example Recursion Tree

```
"Refactor this UserManager class to follow SOLID principles"
├─ "What SOLID principles are violated?" (depth 1)
│  ├─ "Is Single Responsibility violated?" (depth 2) → "Yes: DB, email, logging"
│  ├─ "Is Open/Closed violated?" (depth 2) → "No major violations"
│  └─ "Is Dependency Inversion violated?" (depth 2) → "Yes: concrete Database"
├─ "How should we separate responsibilities?" (depth 1)
│  ├─ "What should UserRepository handle?" (depth 2) → "DB operations only"
│  ├─ "What should EmailService handle?" (depth 2) → "Email sending only"
│  └─ "What should Logger handle?" (depth 2) → "Logging only"
└─ "Compose refactored code" (depth 1) → Final refactored implementation
```

Each arrow (→) represents an LM call. Complex questions trigger further recursion.

## Prompting Strategy

### Design Principles

- **Structured outputs**: Require explicit formats (easier parsing, more deterministic)
- **Anti-hallucination**: Force explicit uncertainty markers
- **Different temperatures**: Lower for planning/critique (0.3-0.5), moderate for reasoning (0.7)
- **Recursion-aware**: Prompts must handle both direct answering and decomposition

### Reasoner Prompts (4 Types)

#### 1. Complexity Assessment Prompt

```
Is this question SIMPLE or COMPLEX?
- SIMPLE: Can be answered directly in 1-2 paragraphs
- COMPLEX: Requires breaking down into sub-questions

Question: {question}
Answer: [SIMPLE or COMPLEX]
```

#### 2. Decomposition Prompt (if complex)

```
Break this complex question into 2-5 simpler sub-questions.

Question: {question}
Context: {context}

Output format:
SUB-QUESTION 1: [question]
SUB-QUESTION 2: [question]
...
```

#### 3. Direct Answer Prompt (if simple or max depth)

```
Answer this question directly.

Question: {question}
Context: {context}

Output format:
ANSWER: [your answer]
ASSUMPTIONS: [any assumptions made]
```

#### 4. Composition Prompt (after recursion)

```
Synthesize these sub-answers into a coherent final answer.

Original Question: {question}
Sub-answers: {sub_answers}

Output format:
FINAL ANSWER: [integrated solution]
```

### Other Stage Prompts

**Planner**: Forces structured output (TASK DECOMPOSITION, KEY QUESTIONS, REQUIRED INFORMATION, SUCCESS CRITERIA)

**Critic**: Strict format requiring CONFIDENCE_SCORE (0-100), GAPS, UNCERTAINTIES, REASONING. Uses harsh evaluation to calibrate scores appropriately.

## File Structure

```
local_llm/
├── src/
│   ├── rlm/
│   │   ├── __init__.py
│   │   ├── client.py              # Ollama API wrapper
│   │   ├── controller.py          # Main RLM orchestrator
│   │   ├── state.py               # State management utilities
│   │   ├── config.py              # Configuration settings
│   │   ├── stages/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Abstract Stage interface
│   │   │   ├── planner.py         # Task decomposition
│   │   │   ├── retriever.py       # Retrieval hook (stubbed)
│   │   │   ├── reasoner.py        # RECURSIVE solution generation
│   │   │   └── critic.py          # Self-evaluation
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── planner_prompts.py
│   │       ├── reasoner_prompts.py
│   │       └── critic_prompts.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py             # Structured logging
│       └── validation.py          # Response validation
├── examples/
│   ├── simple_query.py            # Simple question (direct answer)
│   ├── complex_analysis.py        # Complex task (recursive decomposition)
│   └── code_refactoring.py        # SE-specific example with recursion
├── tests/
│   ├── test_client.py
│   ├── test_controller.py
│   └── test_stages/
├── docs/
│   └── (usage guide will be added)
├── goals/
│   ├── claude_code_rlm_prompt.md
│   ├── RLM_Code_snippets.png
│   └── rlm_architecture.md        # This file
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Configuration

```python
{
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:14b",
        "timeout": 120
    },
    "rlm": {
        "max_recursion_depth": 3,        # Max depth for recursive decomposition
        "complexity_threshold": "auto"   # Let LM decide if simple/complex
    },
    "generation": {
        "planner_temp": 0.5,
        "reasoner_temp": 0.7,      # Moderate for reasoning
        "decompose_temp": 0.4,     # Lower for consistent decomposition
        "critic_temp": 0.3         # Lowest for consistent scoring
    }
}
```

## Key Design Decisions

1. **Recursive LM calls within reasoner** (vs pipeline-level iteration)
   - True RLM approach from research paper
   - Recursion happens during reasoning, not between pipeline runs

2. **LM-driven complexity assessment** (vs hardcoded rules)
   - Leverages model's understanding of question difficulty
   - More flexible than rule-based heuristics

3. **Structured prompts** (vs free-form)
   - More deterministic with local models
   - Easier to parse and validate responses

4. **Depth-limited recursion** (default 3 levels)
   - Prevents infinite loops
   - Allows meaningful decomposition while staying practical

5. **Composition step** (vs concatenation)
   - LM synthesizes sub-answers coherently
   - Results in better quality final answers

6. **Stubbed retrieval** (extensibility point)
   - Ship core RLM first
   - Easy to plug in RAG later

## Extensibility

The architecture is designed for easy extension:

### Future RAG Integration

Replace `RetrieverStage` stub with `VectorRetrieverStage`:
- Embeds query from plan
- Searches vector DB (ChromaDB)
- Returns relevant chunks to enhance context

### Future Tool Calling

Add `ToolExecutorStage` between Reasoner and Critic:
- Parses tool requests from reasoner output
- Executes tools (code execution, API calls, etc.)
- Appends results to context

### Future Multi-Model Support

Create `MultiModelClient` that routes stages to different models:
- Fast model for planning and complexity assessment
- Powerful model for reasoning and composition
- Consistent model for critique

## Dependencies

Minimal:
- `requests` - HTTP client for Ollama API
- `pydantic` - State validation (optional but recommended)
- `pytest` - Testing framework

## Summary: What Makes This "True RLM"

This implementation follows the research paper approach where:

**Core Mechanism**: The Reasoner makes **recursive LM calls** to decompose complex questions into simpler sub-questions, solving each recursively, then composing the results.

**Key Difference from Traditional Approaches**:
- ❌ OLD: Try to solve everything in one pass (or iterate the whole pipeline)
- ✅ NEW: Recursively decompose within reasoning stage

**Why This Matters**:
This approach "defers reasoning over large context by querying recursive LM calls" - exactly as described in RLM research. The LM doesn't try to answer complex questions in one shot; it breaks them down recursively, just like humans decompose difficult problems into manageable subtasks.

**Recursion Flow Example**:
```
"Refactor UserManager class"
├─ decompose → ["What violations?", "How to fix?", "Show code"]
│  ├─ "What violations?" → [recurse on sub-questions...]
│  ├─ "How to fix?" → [recurse on sub-questions...]
│  └─ "Show code" → [direct answer]
└─ compose → Final refactored code with explanation
```

Each arrow (→) is an LM call. Complex questions trigger recursion; simple ones get direct answers.
