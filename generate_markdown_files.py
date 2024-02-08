from tqdm import tqdm
from tqdm.contrib import tzip
import os 
import sys
import json
import time
from pathlib import Path
import pickle
import pandas as pd
import requests
import os
import glob

data_folder = Path('/nlp') / 'data' / 'S2'

def text_of(annotations, text, type_):
    return [text[a['start']:a['end']] for a in annotations.get(type_, '')]

def get_s2_paper(s2orc_data):
    corpusid = s2orc_data['corpusid']
    externalids = s2orc_data['externalids']
    content = s2orc_data['content']
    source = content['source']
    text = content['text']
    annotations = {k: json.loads(v) for k, v in content['annotations'].items() if v}
    return corpusid, externalids, source, text, annotations

def generate_markdown_files():
    # ref: https://mdutils.readthedocs.io/en/latest/examples/Example_Python.html
    json_folder = data_folder / 'sample_survey' / 's2orc_part1'
    json_files = glob.glob(os.path.join(json_folder, '*.json'))

    for idx, json_file in enumerate(tqdm(json_files)):
        with open(json_file) as f:
            json_data = json.load(f)
        s2orc_data, metadata = json_data['s2orc'], json_data['metadata'] 
        corpusid, externalids, source, text, annotations = get_s2_paper(s2orc_data)
        title = text_of(annotations, text, 'title')[0].strip()
        url = metadata['url'] if 'url' in metadata.keys() else 'N/A'
        s2FieldsOfStudy_unique = list(set([item['category'].title() for item in metadata['s2FieldsOfStudy']]))
        markdown_output = f"""# {title}\n
Field(s): {', '.join(s2FieldsOfStudy_unique)}\n 
URL: [{url}]({url})
{text}
"""
        markdown_filename = json_file.split('-')[-1].replace('.json', '.md')
        with open(markdown_filename, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_output.strip()) 

        if idx == 2:
            break


if __name__ == "__main__":
    generate_markdown_files()