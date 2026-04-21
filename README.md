# LLM Prisoner's Dilemma Simulation 🤖🤝🤖

Welcome to the **LLM Prisoner's Dilemma**, a game-theory simulation where two distinct AI agents, powered by Large Language Models (LLMs), negotiate and decide whether to COOPERATE or DEFECT.

🎯 **View the latest interactive simulation report here:**  
👉 **[Live HTML Report](https://lfzinho.github.io/llm-prisoners-dilemma/report.html)** 👈

## How it works

1. **DNA Generation**: Each agent is assigned a random "Psychological DNA" consisting of traits like Altruism, Risk, Honesty, Forgiveness, Transparency, and Planning.
2. **Persona Creation (Victor Frankenstein)**: A specialized LLM profiler converts these numeric traits into a descriptive psychological profile, which is then used to generate a strict, customized `System Prompt` for each agent.
3. **The Game Loop**: Over the course of multiple rounds, the two agents debate in a conversational format. They attempt to deceive, form alliances, or stay true to their nature based solely on their predefined personas.
4. **The Decision**: After the debate, agents make a final, secret choice to `COOPERATE` or `DEFECT`, and are scored based on the classic Prisoner's Dilemma payoff matrix.
5. **Report Generation**: The entire chat history, private reasoning, and scores are recorded in real-time to a `report.md` file. At the end of the simulation, this markdown is automatically compiled into a beautifully styled `report.html` dashboard.

## Requirements & Setup

This project uses `gemma4:e2b` running locally via **Ollama**.
It heavily utilizes `instructor` and `pydantic` to enforce structured JSON outputs ensuring the agents' final decisions never break the game rules.

```bash
# Clone the repository
git clone https://github.com/lfzinho/llm-prisoners-dilemma.git

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the simulation
python main.py
```

## Built With

- **Python 3**
- **[Ollama](https://ollama.ai/)** (Local LLM execution)
- **[Instructor](https://github.com/jxnl/instructor)** (Structured LLM outputs)
- **Pydantic** (Schema validation)
- **Markdown** (HTML parsing & generation)
