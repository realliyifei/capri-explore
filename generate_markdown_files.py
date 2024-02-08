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

def get_filter_survey_df():
    filter_survey_file = data_folder / 'filter_survey' / 'filter_survey_s2orc_part1_annotated.csv'
    filter_survey_df = pd.read_csv(filter_survey_file)
    return filter_survey_df

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

def add_markdown_format_to_header(text, annotations):
    # Initialize an empty list to hold text pieces
    new_text_pieces = []
    last_end = 0  # Keep track of the end of the last annotation
    
    # Iterate over annotations in the 'sectionheader' key
    for anno in annotations.get('sectionheader', []):
        num_hash = 2  # Default number of hashes
        
        if 'attributes' in anno and 'n' in anno['attributes']:
            # print(anno['attributes']['n'], anno['attributes']['n'].count('.'))
            num_hash = anno['attributes']['n'].count('.') + 1
        
        new_text_pieces.append(text[last_end:anno['start']])
        
        formatted_header = f"{'#'*num_hash} {text[anno['start']:anno['end']]}"
        new_text_pieces.append(formatted_header)
        
        last_end = anno['end']
    
    new_text_pieces.append(text[last_end:])
    
    return ''.join(new_text_pieces)

def generate_markdown_files():
    # ref: https://mdutils.readthedocs.io/en/latest/examples/Example_Python.html
    json_folder = data_folder / 'sample_survey' / 's2orc_part1'
    
    filter_survey_df = get_filter_survey_df()

    json_files = glob.glob(os.path.join(json_folder, '*.json'))

    for idx, json_file in enumerate(tqdm(json_files)):
        with open(json_file) as f:
            json_data = json.load(f)
        s2orc_data, metadata = json_data['s2orc'], json_data['metadata'] 
        corpusid, externalids, source, text, annotations = get_s2_paper(s2orc_data)
        title = text_of(annotations, text, 'title')[0].strip()
        text = add_markdown_format_to_header(text, annotations)
        url = metadata['url'] if 'url' in metadata.keys() else 'N/A'

        s2FieldsOfStudy_unique = list(set([item['category'].title() for item in metadata['s2FieldsOfStudy']]))
        s2FieldsOfStudy_unique_tag = [f"#{item.replace(' ', '_')}" for item in s2FieldsOfStudy_unique]

        filter_survey_df_temp = filter_survey_df[filter_survey_df['corpusid'] == corpusid]
        is_survey_by_classifier = bool(filter_survey_df_temp['is_survey_by_classifier'].values[0])
        is_survey_by_annotator = bool(filter_survey_df_temp['is_survey_by_annotator'].values[0]) if not pd.isna(filter_survey_df_temp['is_survey_by_annotator'].values[0]) else '(Not Annotated)'

        markdown_output = f"""# {title}\n
CorpusID: {corpusid}\n 
tags: {', '.join(s2FieldsOfStudy_unique_tag)}\n
URL: [{url}]({url})\n 
| Is Survey?        | Result          |
| ----------------- | --------------- |
| By Classifier     | {is_survey_by_classifier} |
| By Annotator      | {is_survey_by_annotator} |

---
{text}
"""
        markdown_filename = json_file.split('-')[-1].replace('.json', '.md')
        
        #TODO: temporary fix to add 'annotated' to the filename so that we can differentiate between annotated and non-annotated files
        if is_survey_by_annotator != '(Not Annotated)': 
            markdown_filename = f"a_{markdown_filename}"

        with open(markdown_filename, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_output.strip()) 

        if idx == 2:
            break


if __name__ == "__main__":
    generate_markdown_files()