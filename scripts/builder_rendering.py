"""A paired Builder and App with explicit, inspectable local changes."""
import json
from app_rendering import render_app_demo
from demo_rendering import text, template

CHANGE_IDS = {'board', 'priority', 'downtime'}


def render_builder(builder, lang, app_name, logo=None, app_id='builder-preview'):
    en = lang == 'en'
    changes = builder['changes']
    if not changes or len({c['id'] for c in changes}) != len(changes):
        raise ValueError('Builder changes require unique IDs')
    for change in changes:
        if change['id'] not in CHANGE_IDS: raise ValueError('Unsupported Builder change')
        for key in ('title', 'prompt', 'before', 'after'): text(change[key])
    if len({' '.join(c['prompt'].split()).lower() for c in changes}) != len(changes):
        raise ValueError('Builder example prompts must be unique')
    payload = json.dumps(changes,ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    heading = text(builder['heading'])
    if builder.get('highlight'):
        highlight=text(builder['highlight'])
        if highlight not in heading: raise ValueError('Builder highlight must appear in heading')
        heading=heading.replace(highlight,'<em>'+highlight+'</em>',1)
    return template('builder.html', {
        'heading':heading,'intro':text(builder['intro']),'app':text(app_name),
        'preview':render_app_demo(builder['preview'],lang,app_id),'app_id':app_id,
        'logo':('<img src="'+text(logo)+'" alt="Tier0" width="64" height="24">') if logo else '',
        'prompt':text(builder['prompt']),'change_prompt':text(changes[0]['prompt']),
        'changes':payload,
        'presets':''.join('<button type="button" disabled data-builder-control data-builder-preset="'+c['id']+'">'+text(c['title'])+'</button>' for c in changes),
        'prompt_label':'Describe a change' if en else '描述你想调整的地方',
        'builder_title':'Shape the app around your work' if en else '让应用按你的工作方式调整',
        'brief_label':'Application brief' if en else '应用构建需求',
        'copy_label':'Copy' if en else '复制',
        'local_label':'Local change preview' if en else '本地变更演示',
        'presets_label':'Try a change' if en else '试一条需求',
        'preview_label':'Preview change' if en else '预览改动',
        'before_label':'Current app' if en else '当前应用',
        'after_label':'After applying' if en else '应用后',
        'apply_label':'Apply to App' if en else '应用到 App',
        'undo_label':'Undo UI change' if en else '撤销界面改动',
        'inspect_label':'Try it in the App ↗' if en else '到 App 中试一下 ↗',
    })
