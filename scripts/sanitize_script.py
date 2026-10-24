with open('scripts/generate_visual_presentation.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    '➔': '->',
    '⬇': 'v',
    '🔁': '[Loop]',
    '·': '-',
    '•': '*',
    'Δ': 'Delta',
    'α': 'alpha',
    '—': '--',
    '“': '"',
    '”': '"',
    '‘': "'",
    '’': "'"
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open('scripts/generate_visual_presentation.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Sanitization complete!')
