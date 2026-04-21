import markdown
import re
import os

def generate_html(report_path="report.md", output_path="report.html"):
    if not os.path.exists(report_path):
        print(f"Error: {report_path} not found.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_text, 
        extensions=['fenced_code', 'tables']
    )

    # Inject chat bubble styling via regex
    # Match from <p><strong>Agent A:</strong> until the next agent, heading, list, or end of file
    agent_a_pattern = r'<p><strong>Agent A:</strong>(.*?)(?=<p><strong>Agent [AB]:</strong>|<h[1-6]>|<ul>|<div|$)'
    html_content = re.sub(
        agent_a_pattern, 
        r'<div class="chat-container agent-a-container"><div class="chat-bubble agent-a"><strong>Agent A:</strong><p>\1</div></div>', 
        html_content, 
        flags=re.DOTALL
    )

    agent_b_pattern = r'<p><strong>Agent B:</strong>(.*?)(?=<p><strong>Agent [AB]:</strong>|<h[1-6]>|<ul>|<div|$)'
    html_content = re.sub(
        agent_b_pattern, 
        r'<div class="chat-container agent-b-container"><div class="chat-bubble agent-b"><strong>Agent B:</strong><p>\1</div></div>', 
        html_content, 
        flags=re.DOTALL
    )

    # Inject Decision Board
    decision_pattern = r'<h4>Decisions</h4>\s*<ul>\s*<li><strong>Agent A:</strong>\s*(.*?)\s*<em>\(Reasoning:\s*(.*?)\)</em></li>\s*<li><strong>Agent B:</strong>\s*(.*?)\s*<em>\(Reasoning:\s*(.*?)\)</em></li>\s*</ul>'
    decision_html = r"""
    <div class="decision-board">
        <h4>Decisions</h4>
        <div class="decision-cards">
            <div class="decision-card agent-a-card">
                <div class="agent-name">Agent A</div>
                <div class="choice choice-\1">\1</div>
                <div class="reason">\2</div>
            </div>
            <div class="decision-card agent-b-card">
                <div class="agent-name">Agent B</div>
                <div class="choice choice-\3">\3</div>
                <div class="reason">\4</div>
            </div>
        </div>
    </div>
    """
    html_content = re.sub(decision_pattern, decision_html, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Inject Score Board
    score_pattern = r'<p><strong>Score for this round:</strong>(.*?)</p>'
    score_html = r'<div class="score-board"><strong>Score for this round:</strong>\1</div>'
    html_content = re.sub(score_pattern, score_html, html_content, flags=re.DOTALL)

    # HTML Skeleton with clean Light Mode CSS
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prisoner's Dilemma Report</title>
    <style>
        :root {{
            --bg-color: #f0f2f5;
            --text-color: #1c1e21;
            --container-bg: #ffffff;
            --border-color: #dadce0;
            --primary-color: #0056b3;
            --agent-a-bg: #e3f2fd;
            --agent-a-text: #0d47a1;
            --agent-b-bg: #f3e5f5;
            --agent-b-text: #4a148c;
            --code-bg: #f8f9fa;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 850px;
            margin: 0 auto;
            background-color: var(--container-bg);
            padding: 40px 60px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        h1, h2, h3, h4 {{
            color: #202124;
            margin-top: 1.8em;
            margin-bottom: 0.6em;
            font-weight: 600;
        }}
        h1 {{
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 12px;
            font-size: 2.2em;
        }}
        h2 {{
            font-size: 1.6em;
            color: var(--primary-color);
        }}
        pre {{
            background-color: var(--code-bg);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--border-color);
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.02);
        }}
        code {{
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.9em;
        }}
        p code {{
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}
        .chat-container {{
            display: flex;
            margin-bottom: 16px;
            width: 100%;
        }}
        .agent-a-container {{
            justify-content: flex-start;
        }}
        .agent-b-container {{
            justify-content: flex-end;
        }}
        .chat-bubble {{
            max-width: 80%;
            padding: 14px 20px;
            border-radius: 20px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08);
            font-size: 1.05em;
        }}
        .agent-a {{
            background-color: var(--agent-a-bg);
            color: var(--agent-a-text);
            border-bottom-left-radius: 4px;
        }}
        .agent-b {{
            background-color: var(--agent-b-bg);
            color: var(--agent-b-text);
            border-bottom-right-radius: 4px;
        }}
        .chat-bubble strong {{
            display: block;
            margin-bottom: 6px;
            font-size: 0.85em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .chat-bubble p {{
            margin: 0 0 10px 0;
        }}
        .chat-bubble p:last-child {{
            margin-bottom: 0;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 6px;
        }}
        hr {{
            border: 0;
            height: 1px;
            background-color: var(--border-color);
            margin: 40px 0;
        }}
        .decision-board {{
            background-color: #f8f9fa;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }}
        .decision-board h4 {{
            margin-top: 0;
            text-align: center;
            color: #4a5568;
            font-size: 1.2em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }}
        .decision-cards {{
            display: flex;
            gap: 20px;
        }}
        .decision-card {{
            flex: 1;
            padding: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            text-align: center;
            border-top: 4px solid #ccc;
        }}
        .agent-a-card {{
            border-top-color: var(--primary-color);
        }}
        .agent-b-card {{
            border-top-color: var(--agent-b-text);
        }}
        .agent-name {{
            font-weight: bold;
            color: #718096;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        .choice {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
        }}
        .choice-COOPERATE {{
            background-color: #def7ec;
            color: #03543f;
        }}
        .choice-DEFECT {{
            background-color: #fde8e8;
            color: #9b1c1c;
        }}
        .reason {{
            font-size: 0.9em;
            color: #4a5568;
            text-align: left;
            font-style: italic;
            background: #f1f5f9;
            padding: 12px;
            border-radius: 6px;
        }}
        .score-board {{
            text-align: center;
            font-size: 1.2em;
            font-weight: 600;
            color: #2d3748;
            background: #ebf4ff;
            border: 1px solid #bee3f8;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Sleek HTML report generated at: {output_path}")

if __name__ == "__main__":
    generate_html()
