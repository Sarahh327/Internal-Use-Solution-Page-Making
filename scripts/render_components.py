#!/usr/bin/env python3
"""Render approved components from a JSON config. Python standard library only."""
import argparse, json, re, shutil
from pathlib import Path
from demo_rendering import text, render_namespace, render_agent
from builder_rendering import render_builder
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]

def url(value):
    text(value)
    parsed=urlsplit(value)
    if parsed.scheme not in ('','https') or value.startswith('//') or '\\' in value or any(ord(c)<32 for c in value):
        raise ValueError('Only relative paths or HTTPS URLs are allowed')
    return text(value)

def render(config):
    lang=config['language']
    if lang not in ('zh-CN','en'): raise ValueError('language must be zh-CN or en')
    en=lang=='en'; app=text(config['app']); b=config['builder']; a=config['agent']; d=config['delivery']
    sources=a['sources']
    if not sources: raise ValueError('UNS sources required')
    available=set()
    for source in sources:
        path=source['path'];text(path)
        if not re.search(r'/(Metric|State|Action)/[^/]+$',path): raise ValueError('Topic must be below Metric, State or Action')
        if not source['fields']: raise ValueError('UNS fields required')
        for field in source['fields']: text(field);available.add(path+'#'+field)
    questions=set()
    for scenario in [a]+a.get('examples',[]):
        if not scenario['field_refs'] or not set(scenario['field_refs'])<=available: raise ValueError('Analysis field_refs not found in UNS source mapping')
        question=' '.join(scenario['question'].split()).casefold()
        if question in questions: raise ValueError('Prepared questions must be unique')
        questions.add(question)
    if ' '.join(a['followup'].split()).casefold() not in questions: raise ValueError('Follow-up must match a prepared example question')
    if a['data_status'] not in ('illustrative','verified'): raise ValueError('Specify illustrative or verified data')
    if a['data_status']=='verified': text(a['evidence'])
    url(config['logo'])
    parts=[render_namespace(config['namespace'],sources,lang),
           render_builder(b,lang,config['app'],config['logo']),
           render_agent(a,lang)]
    service=(ROOT/'assets/service-modes/ems-original.html').read_text()
    replacements={'先验证一个车间，再扩展到更多设备和能源介质。':d['scope'],'自主组织 UNS 数据与计量关系':d['organize'],'自主生成、修改和迭代完整 EMS 应用':('Generate, modify and iterate your complete '+config['app']+' application') if en else ('自主生成、修改和迭代完整 '+config['app']+' 应用'),'梳理仪表、系统接口和 UNS 模型':d['integration'],'定制指标计算、应用页面与处理流程':d['customize']}
    if en:
        replacements.update({'自主构建，或购买':'Build it yourself, or use ','工程服务':'engineering services','团队自主构建':'Build with your team','适合愿意自己上手、希望 100% 掌控自己数字化项目的团队。':'For hands-on teams that want 100% control over their digital project.','掌握功能规划、业务流程与项目推进':'Own feature planning, workflows and project delivery','购买工程定制服务':'Purchase custom engineering services','按约定范围完成接入、定制与交付。':'Integration, customization and delivery within an agreed scope.','按约定范围完成验证与交付':'Validate and deliver within the agreed scope'})
    pattern=re.compile('|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True)))
    service=pattern.sub(lambda m:text(replacements[m[0]]),service)
    parts.append(service)
    return '\n'.join(parts)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('config',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--force',action='store_true');args=ap.parse_args()
    try:
        config=json.loads(args.config.read_text()); content=render(config)
        assets=['components.css','components.js','app-demo.css','app-demo.js','builder-demo.css','builder-demo.js','service-modes.css']
        destinations=[args.output]+[args.output.parent/n for n in assets]
        if not args.force and any(x.exists() for x in destinations): raise ValueError('Output exists; choose a new directory or use --force after reviewing changes')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text('<!-- Fragment: insert into an existing semantic page, not a complete website. -->\n<link rel="stylesheet" href="components.css">\n<link rel="stylesheet" href="service-modes.css">\n<link rel="stylesheet" href="app-demo.css">\n<link rel="stylesheet" href="builder-demo.css">\n'+content+'\n<script src="app-demo.js"></script>\n<script src="components.js"></script>\n<script src="builder-demo.js"></script>\n')
        for name in assets:shutil.copy2(ROOT/('assets/service-modes' if name=='service-modes.css' else 'assets/components')/name,args.output.parent/name)
        print(args.output)
    except (ValueError,KeyError,TypeError,OSError) as exc:ap.error(str(exc))
if __name__=='__main__':main()
