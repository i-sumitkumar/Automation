import os
import re


def clean_text(text):
    """
    Cleans the input text by:
      • Removing unwanted markers like "Question <number>Answer"
      • Replacing multiple consecutive newlines with a single newline
      • Splitting the text into lines and trimming extra whitespace
      • Merging lines only when a line is exactly a bullet option (e.g. "a.")
        with the line immediately following it.
    """
    # Remove markers of the form "Question <number>Answer" (e.g., "Question 5Answer", "Question 10Answer")
    text = re.sub(r'Question\s*\d+\s*Answer', '', text)

    # Replace multiple newlines with a single newline
    text = re.sub(r'\n\s*\n+', '\n', text)

    # Split text into lines and trim extra spaces
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Merge bullet option lines only if a line is exactly a letter with a dot
    new_lines = []
    i = 0
    while i < len(lines):
        # If the current line is exactly a letter with a dot (e.g., "a."), merge it with the following line.
        if re.match(r'^[a-zA-Z]\.$', lines[i]):
            if i + 1 < len(lines):
                merged_line = lines[i] + " " + lines[i + 1]
                new_lines.append(merged_line)
                i += 2  # Skip the next line, as it has been merged
                continue
            else:
                new_lines.append(lines[i])
        else:
            new_lines.append(lines[i])
        i += 1

    return "\n".join(new_lines)

def build_prompts(question_text, context_text):
    # Clean the question and context text to fix spacing and remove extraneous parts
    question_text = clean_text(question_text)
    context_text = clean_text(context_text)

    def load_custom_or_default(custom_path, default_path):
        if os.path.exists(custom_path):
            with open(custom_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            with open(default_path, "r", encoding="utf-8") as f:
                return f.read().strip()

    prompt_a_tail = load_custom_or_default("prompts/prompt_a.txt", "prompts/default_prompt_a.txt")
    prompt_b_tail = load_custom_or_default("prompts/prompt_b.txt", "prompts/default_prompt_b.txt")

    prompt_a = f"""Task: Answer the following multiple-choice question by analyzing the provided research paper. Follow a strict step-by-step reasoning approach to ensure accuracy.
Question:
{question_text}
{prompt_a_tail}
Context:
{context_text}
"""

    prompt_b = f"""Task: Answer the following multiple-choice question by analyzing the provided research paper. Follow a strict step-by-step reasoning approach to ensure accuracy.
Question:
{question_text}
{prompt_b_tail}
Context:
{context_text}
"""

    return prompt_a, prompt_b
