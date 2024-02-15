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

import gradio as gr

from constants import s2FieldsOfStudy_list

data_folder = Path('/nlp') / 'data' / 'S2'
markdown_folder = Path('markdown_files')

################################# helper #################################
def get_filter_survey_df():
    filter_survey_file = data_folder / 'survey_papers_by_domain_annotated.csv'
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


def get_text_by_corpusid(corpusid):
    filter_survey_df = get_filter_survey_df()
    filter_data = filter_survey_df[filter_survey_df['corpusid'] == corpusid].iloc[0].to_dict()
    survey_data = data_folder / 'sample_survey' / 's2orc_part1' / f"survey-{corpusid}.json"
    survey_data = json.load(open(survey_data))
    s2orc_data = survey_data['s2orc']
    return get_s2_paper(s2orc_data)


def get_df_filter_by_field(s2FieldsOfStudy):
    filter_survey_df = get_filter_survey_df()
    filter_survey_df_filter = filter_survey_df[filter_survey_df['domain'] == s2FieldsOfStudy]
    return filter_survey_df_filter

# ################################# gradio two-staged input #################################
filter_survey_df = get_filter_survey_df()
title2corpusid = filter_survey_df.set_index('title')['corpusid'].to_dict()

# First stage: Outputs titles based on field of study
def output_titles(s2FieldsOfStudy):
    filter_survey_df_filter = get_df_filter_by_field(s2FieldsOfStudy)
    corpusids = filter_survey_df_filter['corpusid'].tolist()
    titles = filter_survey_df_filter['title'].tolist()
    return titles

def change_dropdown(s2FieldsOfStudy):
    filter_survey_df_filter = get_df_filter_by_field(s2FieldsOfStudy)
    titles = filter_survey_df_filter['title'].tolist()
    titles_trimmed = [title[:200] + '...' if len(title) > 200 else title for title in titles]
    return gr.Dropdown(label=f"Select a paper from {s2FieldsOfStudy}", choices=titles_trimmed) 

# Second stage: Outputs content of selected paper
def change_markdown(title):
    try:
        corpusid = title2corpusid[title]
    except KeyError:
        return gr.Markdown(value=f'(The title "{title}" is not found)', label="Paper", line_breaks=True, header_links=True)
    markdown_file = markdown_folder / f"{corpusid}.md"
    if markdown_file.exists():
        text = markdown_file.read_text()
    else:
        text = f"(Content not found via {markdown_file})"
    return gr.Markdown(value=text, label="Paper", line_breaks=True, header_links=True)

# Create a Gradio interface
with gr.Blocks() as demo:
    # ref. https://www.gradio.app/guides/blocks-and-event-listeners#updating-component-configurations
    with gr.Row():
        field_of_study = gr.Radio(choices=s2FieldsOfStudy_list, label="Select a field of study",)
    with gr.Row():
        paper_titles = gr.Dropdown(choices=[''], label="Select a paper", interactive=True) 
        field_of_study.change(fn=change_dropdown, inputs=field_of_study, outputs=paper_titles)
    with gr.Row():
        gr.Textbox(label="Q&A", value=f"Dummy question: ?\n\nDummy answer: .")
    with gr.Row():
        display_content = gr.Markdown(value='(Please select a paper)', label="Paper",  line_breaks=True, header_links=True)
        paper_titles.change(fn=change_markdown, inputs=paper_titles, outputs=display_content)


if __name__ == "__main__":
    demo.launch()
    # demo.launch(share=True)