import random
from typing import Literal, List
from pydantic import BaseModel
import instructor
from openai import OpenAI
from tqdm import tqdm
import os
import winsound
import export_html

# Configure the raw OpenAI client and the Instructor patched client
base_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)
instructor_client = instructor.from_openai(
    base_client,
    mode=instructor.Mode.JSON,
)

MODEL_NAME = "gemma4:e2b"
ROUNDS = 3
MESSAGES_PER_ROUND = 3

class PlayerDNA(BaseModel):
    altruism: int      # -100 (Egoísta) to 100 (Altruísta)
    forgiveness: int   # -100 (Vingativo) to 100 (Perdoa)
    transparency: int  # -100 (Misterioso) to 100 (Transparente)
    risk: int          # -100 (Cauteloso) to 100 (Arrisca)
    honesty: int       # -100 (Manipulador) to 100 (Honesto)
    planning: int      # -100 (Reativo) to 100 (Planejador)

    @classmethod
    def generate_random(cls):
        return cls(
            altruism=random.randint(-100, 100),
            forgiveness=random.randint(-100, 100),
            transparency=random.randint(-100, 100),
            risk=random.randint(-100, 100),
            honesty=random.randint(-100, 100),
            planning=random.randint(-100, 100),
        )

class Player:
    def __init__(self, name: str, dna: PlayerDNA):
        self.name = name
        self.dna = dna
        self.score = 0
        self.history = []

class Decision(BaseModel):
    decision: Literal["COOPERATE", "DEFECT"]
    reasoning: str

class VictorFrankenstein:
    @staticmethod
    def give_life(player: Player) -> tuple[str, str]:
        # Step 1: Turn numbers into words
        translation_prompt = f"""You are a psychological profiler. Convert the following numerical traits (-100 to 100) into short, descriptive phrases (e.g., 'extremely selfish', 'highly tolerant to taking risks', 'moderately honest').
REMINDER: A number close to 100 is very pronounced. A number close to 50 is somewhat pronounced. A number close to 0 is neutral. A number close to -100 is very pronounced in the opposite direction.
Do not write a full paragraph, just output a bulleted list of the 6 traits as descriptive phrases.

Traits:
- Altruism: {player.dna.altruism}
- Forgiveness: {player.dna.forgiveness}
- Transparency: {player.dna.transparency}
- Risk: {player.dna.risk}
- Honesty: {player.dna.honesty}
- Planning: {player.dna.planning}
"""
        translation_response = base_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": translation_prompt}],
        )
        word_description = translation_response.choices[0].message.content

        # Step 2: Use word description to generate persona
        system_prompt = f"""You are a model that creates the persona of a player based on their psychological profile.
Your job is to write a short, first-person system prompt that dictates their persona and strategy for playing the Prisoner's Dilemma. 
Start the prompt with 'You are {player.name}...'. 
Describe their traits through their expected behavior and mindset. Keep the instructions simple and clear.

Please strictly use the following Markdown structure for your response:
### Persona Summary
[A vivid description of their personality]
### Game Strategy
[How they plan to act in this game based on their traits]

Psychological Profile:
{word_description}
"""
        response = base_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": system_prompt}],
        )
        persona = response.choices[0].message.content
        
        # Append the game rules
        rules = """

This is a game of Prisoner's Dilemma with multiple rounds.
- In each round, you will exchange messages with the other player before making your final secret choice (COOPERATE or DEFECT).
- If you both cooperate, you both get 3 points. If you both defect, you both get 1 point. If one cooperates and the other defects, the defector gets 5 points and the cooperator gets 0 points.
- Your goal is to maximize your total score after all rounds.
- Stay in character at all times. Never break the fourth wall.
- Keep your responses under 200 words.
- Keep the tone light and informal, using simple vocabulary.
"""
        return persona + rules, word_description

def get_message(system_prompt: str, context_messages: List[dict]) -> str:
    messages = [{"role": "system", "content": system_prompt}] + context_messages
    try:
        response = base_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error generating message: {e}]"

def get_decision(system_prompt: str, context_messages: List[dict]) -> Decision:
    messages = [{"role": "system", "content": system_prompt}] + context_messages
    messages.append({
        "role": "user", 
        "content": "The debate is over. Based on the conversation and your personality, what is your final decision for this round? Return JSON with your 'decision' (exactly COOPERATE or DEFECT) and a brief 'reasoning'."
    })
    
    try:
        response = instructor_client.chat.completions.create(
            model=MODEL_NAME,
            response_model=Decision,
            messages=messages,
            max_retries=3
        )
        return response
    except Exception as e:
        print(f"\n[Warning] Failed to extract structured decision: {e}")
        return Decision(decision="DEFECT", reasoning="Defaulted to DEFECT due to an error.")

def calculate_scores(decision_a: str, decision_b: str):
    if decision_a == "COOPERATE" and decision_b == "COOPERATE":
        return 3, 3
    elif decision_a == "COOPERATE" and decision_b == "DEFECT":
        return 0, 5
    elif decision_a == "DEFECT" and decision_b == "COOPERATE":
        return 5, 0
    elif decision_a == "DEFECT" and decision_b == "DEFECT":
        return 1, 1
    return 0, 0

def save_report(report_lines: List[str]):
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

def main():
    print("--- Prisoner's Dilemma Simulation ---")
    
    print("\n[1/4] Generating Random DNA profiles...")
    player_a = Player("Agent A", PlayerDNA.generate_random())
    player_b = Player("Agent B", PlayerDNA.generate_random())

    print("Agent A DNA:", player_a.dna.model_dump())
    print("Agent B DNA:", player_b.dna.model_dump())

    reroll = input("Do you want a re-roll? (y/n): ")
    while reroll == "y":
        player_a = Player("Agent A", PlayerDNA.generate_random())
        player_b = Player("Agent B", PlayerDNA.generate_random())
        print("Agent A DNA:", player_a.dna.model_dump())
        print("Agent B DNA:", player_b.dna.model_dump())
        reroll = input("Do you want a re-roll? (y/n): ")
    
    print("\n[2/4] Victor Frankenstein is creating the personas...")
    sys_prompt_a, word_desc_a = VictorFrankenstein.give_life(player_a)
    print("-> Agent A's persona generated!")
    sys_prompt_b, word_desc_b = VictorFrankenstein.give_life(player_b)
    print("-> Agent B's persona generated!")

    report_lines = []
    report_lines.append("# Prisoner's Dilemma Simulation Report\n")
    report_lines.append(f"## Model: {MODEL_NAME}\n")
    report_lines.append("## DNA Profiles & Personas\n")
    
    report_lines.append("### Agent A")
    report_lines.append(f"```json\n{player_a.dna.model_dump_json(indent=2)}\n```\n")
    report_lines.append("**Psychological Profile:**\n\n" + word_desc_a + "\n")
    report_lines.append("**System Prompt:**\n```text\n" + sys_prompt_a + "\n```\n")
    
    report_lines.append("### Agent B")
    report_lines.append(f"```json\n{player_b.dna.model_dump_json(indent=2)}\n```\n")
    report_lines.append("**Psychological Profile:**\n\n" + word_desc_b + "\n")
    report_lines.append("**System Prompt:**\n```text\n" + sys_prompt_b + "\n```\n")

    report_lines.append("## Game Log\n")
    save_report(report_lines)

    history_a = []
    history_b = []

    num_rounds = ROUNDS
    messages_per_round = MESSAGES_PER_ROUND
    total_messages = num_rounds * messages_per_round * 2
    
    print("\n[3/4] Simulating Game Rounds...")
    
    message_counter = 0
    with tqdm(total=total_messages, desc="Exchanging Messages") as pbar:
        for round_num in range(1, num_rounds + 1):
            report_lines.append(f"### Round {round_num}\n")
            
            dialogue_a = history_a.copy()
            dialogue_b = history_b.copy()

            dialogue_a.append({"role": "user", "content": f"Round {round_num} has started. You may now speak to Agent B. You have {messages_per_round} messages to send before the final decision."})
            dialogue_b.append({"role": "user", "content": f"Round {round_num} has started. Wait for Agent A to speak. You have {messages_per_round} messages to send before the final decision."})

            report_lines.append("#### Debate\n")
            save_report(report_lines)
            
            for i in range(messages_per_round):
                messages_left = messages_per_round - i - 1
                
                # Agent A speaks
                msg_a = get_message(sys_prompt_a, dialogue_a)
                report_lines.append(f"**Agent A:** {msg_a}\n")
                dialogue_a.append({"role": "assistant", "content": msg_a})
                
                b_prompt = f"Agent A says: {msg_a}"
                if messages_left > 0:
                    b_prompt += f" (You have {messages_left + 1} messages left to send before the final decision)"
                else:
                    b_prompt += f" (This is your final message before the decision)"
                dialogue_b.append({"role": "user", "content": b_prompt})
                save_report(report_lines)
                
                message_counter += 1
                pbar.update(1)
                pbar.set_postfix({"Round": round_num, "Speaker": "A"})

                # Agent B replies
                msg_b = get_message(sys_prompt_b, dialogue_b)
                report_lines.append(f"**Agent B:** {msg_b}\n")
                dialogue_b.append({"role": "assistant", "content": msg_b})
                
                a_prompt = f"Agent B says: {msg_b}"
                if messages_left > 0:
                    a_prompt += f" (You have {messages_left} messages left to send before the final decision)"
                else:
                    a_prompt += f" (The debate is over. Prepare for your final decision.)"
                dialogue_a.append({"role": "user", "content": a_prompt})
                save_report(report_lines)
                
                message_counter += 1
                pbar.update(1)
                pbar.set_postfix({"Round": round_num, "Speaker": "B"})

            # Decisions
            decision_a = get_decision(sys_prompt_a, dialogue_a)
            decision_b = get_decision(sys_prompt_b, dialogue_b)

            score_a, score_b = calculate_scores(decision_a.decision, decision_b.decision)
            player_a.score += score_a
            player_b.score += score_b

            report_lines.append("#### Decisions\n")
            report_lines.append(f"- **Agent A:** {decision_a.decision} *(Reasoning: {decision_a.reasoning})*")
            report_lines.append(f"- **Agent B:** {decision_b.decision} *(Reasoning: {decision_b.reasoning})*\n")
            report_lines.append(f"**Score for this round:** Agent A got {score_a}, Agent B got {score_b}\n")
            save_report(report_lines)

            round_summary = f"In round {round_num}, you chose {decision_a.decision} and Agent B chose {decision_b.decision}. You received {score_a} points, and Agent B received {score_b} points."
            history_a.append({"role": "system", "content": round_summary})
            
            round_summary_b = f"In round {round_num}, you chose {decision_b.decision} and Agent A chose {decision_a.decision}. You received {score_b} points, and Agent A received {score_a} points."
            history_b.append({"role": "system", "content": round_summary_b})

    print("\n[4/4] Calculating Final Results...")
    report_lines.append("## Final Results\n")
    report_lines.append(f"- **Agent A Total Score:** {player_a.score}")
    report_lines.append(f"- **Agent B Total Score:** {player_b.score}")
    
    if player_a.score > player_b.score:
        report_lines.append("\n**Agent A Wins!**")
    elif player_b.score > player_a.score:
        report_lines.append("\n**Agent B Wins!**")
    else:
        report_lines.append("\n**It's a Tie!**")

    save_report(report_lines)
    print("Simulation complete! Check report.md for details.")
    
    print("\nGenerating HTML report...")
    export_html.generate_html()
    
    # Play a sound to notify completion (frequency: 1000Hz, duration: 500ms)
    winsound.MessageBeep(winsound.MB_OK)

if __name__ == "__main__":
    main()
