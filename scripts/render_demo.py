#!/usr/bin/env python3
"""Render a self-contained app reference, not a complete branded solution page."""
import argparse
import json
from pathlib import Path
from app_rendering import render_app_demo
from demo_rendering import ASSETS, text
from builder_rendering import render_builder


def render(config, with_builder=False):
    lang = config['language']
    if lang not in ('zh-CN', 'en'): raise ValueError('language must be zh-CN or en')
    css = (ASSETS/'app-demo.css').read_text()
    js = (ASSETS/'app-demo.js').read_text()
    model = render_app_demo(config['builder']['preview'],lang,'app-reference')
    if with_builder:
        model=render_builder(config['builder'],lang,config['app'],app_id='app-reference')
        css=(ASSETS/'components.css').read_text()+'\n'+css+'\n'+(ASSETS/'builder-demo.css').read_text()+'\n#builder.t0-module{width:100%;padding:0}'
        js+='\n'+(ASSETS/'components.js').read_text()+'\n'+(ASSETS/'builder-demo.js').read_text()
    return ('<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+text(config['builder']['preview']['title'])+'</title><style>*,*::before,*::after{box-sizing:border-box}body{margin:0;padding:56px 24px;background:#f4f6f2}main{max-width:1180px;margin:auto}@media(max-width:600px){body{padding:12px}}'+css+'</style></head><body><main>'+model+'</main><script>'+js+'</script></body></html>')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--with-builder',action='store_true');a=p.parse_args()
    try:
        html=render(json.loads(a.config.read_text()),a.with_builder);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);print(a.output)
    except (ValueError,KeyError,TypeError,OSError) as exc:p.error(str(exc))
