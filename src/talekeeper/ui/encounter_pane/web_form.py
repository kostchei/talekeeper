# core
# category: core
# === File: web_ui.py ===
from flask import Flask, request, render_template_string, redirect
from campaign_frame import CampaignFrame

app = Flask(__name__)

FORM_TEMPLATE = '''
<!doctype html>
<title>Campaign Frame Editor</title>
<h1>Create/Edit Campaign Frame</h1>
<form method=post>
  Name: <input type=text name=name><br><br>
  Monster Type Weights (JSON):<br>
  <textarea name=monster_type_weights rows=4 cols=60>{"fiend": 0.4, "aberration": 0.4, "humanoid": 0.2}</textarea><br><br>
  Difficulty Distribution (JSON):<br>
  <textarea name=difficulty_distribution rows=3 cols=60>{"low": 0.5, "moderate": 0.4, "high": 0.1}</textarea><br><br>
  Rest Rules (JSON):<br>
  <textarea name=rest_rules rows=3 cols=60>{"wilderness_interrupt_chance": 0.5, "town_interrupt_chance": 0.0}</textarea><br><br>
  Campaign Style:<br>
  <textarea name=style rows=3 cols=60>Harsh, grimdark sword & sorcery.</textarea><br><br>
  <input type=submit value=Save>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
# POTENTIAL_DEAD_CODE: Function 'index' appears unused
def index():
    if request.method == 'POST':
        frame = CampaignFrame(
            name=request.form['name'],
            monster_type_weights=json.loads(request.form['monster_type_weights']),
            difficulty_distribution=json.loads(request.form['difficulty_distribution']),
            rest_rules=json.loads(request.form['rest_rules']),
            style=request.form['style']
        )
        frame.save_to_file(f"frames/{frame.name}.json")
        return redirect('/')
    return render_template_string(FORM_TEMPLATE)

if __name__ == '__main__':
    import os
    os.makedirs("frames", exist_ok=True)
    app.run(debug=True)
