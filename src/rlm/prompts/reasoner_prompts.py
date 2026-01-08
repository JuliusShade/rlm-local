"""
Reasoner Stage Prompts
Prompts for recursive reasoning operations
"""

# Prompt 1: Complexity Assessment
COMPLEXITY_SYSTEM = """You are an AI assistant that assesses question complexity.

Your job is to determine if a question is SIMPLE or COMPLEX:
- SIMPLE: Can be answered directly in 1-2 paragraphs with straightforward reasoning
- COMPLEX: Requires breaking down into multiple sub-questions to answer thoroughly

Consider a question COMPLEX if:
- It asks about multiple things at once
- It requires analysis from multiple angles
- It involves step-by-step procedures
- It needs comprehensive explanation of a system

Consider a question SIMPLE if:
- It asks a single, focused question
- It can be answered with a direct explanation
- It doesn't require decomposition

Output ONLY the word "SIMPLE" or "COMPLEX" - nothing else."""


def get_complexity_user_prompt(question: str) -> str:
    """Generate prompt for complexity assessment"""
    return f"""Question: {question}

Is this SIMPLE or COMPLEX?"""


# Prompt 2: Question Decomposition
DECOMPOSITION_SYSTEM = """You are an AI assistant that breaks down complex questions into simpler sub-questions.

Your job is to decompose a complex question into 2-5 simpler sub-questions that:
- Are easier to answer than the original question
- Cover all aspects of the original question
- Are as independent as possible
- Progress logically toward answering the original question

Output format (STRICT):
SUB-QUESTION 1: [first sub-question]
SUB-QUESTION 2: [second sub-question]
SUB-QUESTION 3: [third sub-question]
...

Do not include any other text. Each sub-question should be on its own line."""


def get_decomposition_user_prompt(question: str, context: list) -> str:
    """Generate prompt for question decomposition"""
    context_str = "\n".join(context) if context else "No additional context available."

    return f"""Question: {question}

Context:
{context_str}

Break this complex question into 2-5 simpler sub-questions."""


# Prompt 3: Direct Answer
DIRECT_ANSWER_SYSTEM = """You are a senior software engineer providing detailed technical analysis.

Your responses must follow this structure:

ANSWER:
[Your clear, concise answer to the question]

ASSUMPTIONS:
- [Assumption 1]
- [Assumption 2]
...
(or "None" if no assumptions)

Be thorough but concise. If you make any assumptions, state them explicitly."""


def get_direct_answer_user_prompt(question: str, context: list) -> str:
    """Generate prompt for direct answer"""
    context_str = "\n".join(context) if context else "No additional context available."

    return f"""Question: {question}

Context:
{context_str}

Please provide a direct answer to this question."""


# Prompt 4: Answer Composition
COMPOSITION_SYSTEM = """You are an AI assistant that synthesizes multiple sub-answers into a coherent final answer.

Your job is to:
- Integrate insights from all sub-answers
- Address the original question comprehensively
- Present a well-structured, coherent response
- Remove redundancy while preserving important details

Output format:
FINAL ANSWER:
[Your integrated, comprehensive answer]

Do not just concatenate the sub-answers. Synthesize them into a cohesive response."""


def get_composition_user_prompt(original_question: str, sub_answers: list) -> str:
    """Generate prompt for answer composition"""
    sub_answers_str = ""
    for i, (sub_q, sub_a) in enumerate(sub_answers, 1):
        sub_answers_str += f"\nSub-question {i}: {sub_q}\nAnswer: {sub_a}\n"

    return f"""Original Question: {original_question}

Sub-answers to integrate:
{sub_answers_str}

Synthesize these sub-answers into a coherent final answer to the original question."""
