"""Export tokens and provenance to JSON"""
import json




def export_tokens(path: str, data: dict):
with open(path, 'w', encoding='utf-8') as f:
json.dump(data, f, indent=2)
