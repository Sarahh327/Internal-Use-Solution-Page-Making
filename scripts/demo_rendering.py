"""Escaped, pre-rendered interactive mockups. No network or third-party packages."""
import html
from pathlib import Path
from string import Template

ASSETS = Path(__file__).resolve().parents[1] / 'assets/components'


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Required text is empty or not a string')
    return html.escape(value, quote=True)


def template(name, values):
    return Template((ASSETS / name).read_text()).substitute(values)


def result_html(result):
    if result['type'] == 'table':
        cols, rows = result['columns'], result['rows']
        if not 1 <= len(cols) <= 5 or not rows or any(len(row) != len(cols) for row in rows):
            raise ValueError('Table requires 1–5 columns and consistent nonempty rows')
        return ('<div class="t0-table-scroll"><table><caption>' + text(result['title']) +
                '</caption><thead><tr>' + ''.join('<th scope="col">' + text(c) + '</th>' for c in cols) +
                '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + text(v) + '</td>' for v in row) +
                '</tr>' for row in rows) + '</tbody></table></div>')
    if result['type'] == 'list' and result['items']:
        return '<ul>' + ''.join('<li>' + text(v) + '</li>' for v in result['items']) + '</ul>'
    raise ValueError('Supported results: nonempty table or list; review custom interactive charts separately')


def render_namespace(config, sources, lang):
    en = lang == 'en'
    source_buttons, panels = [], []
    topics = {source['path']: source for source in sources}
    if not config['sources']:
        raise ValueError('Namespace acquisition sources are required')
    for i, source in enumerate(config['sources']):
        if source['topic'] not in topics:
            raise ValueError('Acquisition topic not found in Agent sources')
        target = f'namespace-source-{i}'
        source_buttons.append(f'<button type="button" disabled data-demo-control data-source-select="{i}" '
                              f'aria-controls="{target}" aria-pressed="{str(i == 0).lower()}">' + text(source['label']) + '</button>')
        panels.append(f'<div id="{target}" data-source-panel="{i}"' + (' hidden' if i else '') +
                      '><p data-uns-source>' + text(source['method']) + '</p><code>' + text(source['topic']) + '</code></div>')
    tree = {}
    for source in sources:
        branch = tree
        for part in source['path'].split('/'):
            if not part:
                raise ValueError('Empty UNS path segment')
            branch = branch.setdefault(part, {})

    def branches(nodes, prefix=''):
        body = ''
        for label, children in nodes.items():
            path = prefix + '/' + label if prefix else label
            if children:
                body += '<details open><summary>' + text(label) + '</summary>' + branches(children, path) + '</details>'
            else:
                body += '<details><summary>' + text(label) + '</summary><ul>' + ''.join(
                    '<li><code>' + text(field) + '</code></li>' for field in topics[path]['fields']) + '</ul></details>'
        return body
    return template('namespace.html', {
        'heading': text(config['heading']), 'intro': text(config['intro']),
        'sources': ''.join(source_buttons), 'panels': ''.join(panels), 'tree': branches(tree),
        'source_label': 'Data sources' if en else '数据来源',
        'model_label': 'Business objects' if en else '业务对象',
        'label': 'Connection design example' if en else '接入设计示例',
        'reset_label': 'Reset example' if en else '重置示例',
    })


def render_agent(agent, lang):
    en = lang == 'en'
    scenarios = [agent] + agent.get('examples', [])
    questions, panels = [], []
    result_label = ('Recorded result' if en else '记录结果') if agent['data_status'] == 'verified' else ('Illustrative analysis' if en else '分析示意')
    for i, scenario in enumerate(scenarios):
        used_paths = {ref.rsplit('#', 1)[0] for ref in scenario['field_refs']}
        source_text = ''.join('<code>' + text(s['path']) + '</code>' for s in agent['sources'] if s['path'] in used_paths)
        questions.append(f'<button type="button" disabled data-demo-control data-agent-preset="{i}">' + text(scenario['question']) + '</button>')
        panels.append(f'<div data-agent-scenario="{i}"' + (' hidden' if i else '') +
                      '><div class="t0-question">' + text(scenario['question']) + '</div><p class="t0-answer">' +
                      text(scenario['answer']) + '</p><details class="t0-source"><summary>Source</summary>' + source_text +
                      '</details><div class="t0-analysis"><div class="t0-bottom"><strong>' + text(scenario['result']['title']) +
                      '</strong><span>' + result_label + '</span></div>' + result_html(scenario['result']) +
                      f'</div><button type="button" disabled data-demo-control data-agent-save="{i}">' +
                      ('Add to Card List' if en else '加入 Card List') + '</button></div>')
    return template('agent.html', {
        **{key: text(agent[key]) for key in ('heading', 'intro', 'scenario', 'followup')},
        'questions': ''.join(questions), 'scenarios': ''.join(panels),
        'tabs_label': 'Agent views' if en else 'Agent 视图',
        'example_label': 'Prepared examples' if en else '预设示例',
        'followup_label': 'Question' if en else '业务问题',
        'run_label': 'Run example' if en else '运行示例',
        'reset_label': 'Reset example' if en else '重置示例',
        'empty_label': 'No example cards added.' if en else '尚未添加示例卡片。',
        'task_label': 'Add displayed analysis question to example tasks' if en else '将当前分析问题加入示例任务',
        'task_note': 'Local task preview; no schedule runs.' if en else '本页任务预览，不执行定时调度。',
        'preview_label': 'Interactive example · local data' if en else '交互示例 · 本地数据',
    })
