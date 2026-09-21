#!/usr/bin/env python3
"""Static solution-page audit. Never certifies rendering, OCR or business truth."""
import argparse,json,re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote

class Node:
    def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[];self.data=[]
    def all(self):
        yield self
        for child in self.children:yield from child.all()
    def text(self):return ' '.join(self.data+[c.text() for c in self.children if c.tag not in ('script','style')])
    def cls(self,name):return name in self.attrs.get('class','').split()
class Document(HTMLParser):
    void={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,source):
        super().__init__(convert_charrefs=True);self.root=Node();self.current=self.root;self.feed(source)
    def handle_starttag(self,t,a):
        n=Node(t,a,self.current);self.current.children.append(n)
        if t not in self.void:self.current=n
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        p=self.current
        while p.parent:
            if p.tag==t:self.current=p.parent;return
            p=p.parent
    def handle_data(self,d):self.current.data.append(d)

def audit(page,manifest=None,forbidden=()):
    report={'page':str(page),'errors':[],'warnings':[],'manual_required':['Operate every demo: before/action/after/reset, keyboard, mobile and offline delivery','Visual inventory: every diagram or demo screenshot replaced by an interactive model; evidence exceptions reviewed','Translation of all demo states and evidence images','Business claims, UNS data sufficiency and analysis accuracy']}
    error=lambda code,msg:report['errors'].append({'code':code,'message':msg})
    warn=lambda code,msg:report['warnings'].append({'code':code,'message':msg})
    try:raw=page.read_text()
    except OSError as exc:error('page',str(exc));report['static_status']='fail';return report
    dom=Document(raw);nodes=list(dom.root.all());ids={n.attrs['id']:n for n in nodes if 'id' in n.attrs}
    lang=next((n.attrs.get('lang','') for n in nodes if n.tag=='html'),'')
    if lang not in ('zh-CN','en'):error('language','html lang must be zh-CN or en')
    if sum(n.tag=='h1' for n in nodes)!=1:error('heading','Exactly one H1 is required')
    if not any(n.tag=='title' and n.text().strip() for n in nodes):error('metadata','Missing title')
    if not any(n.tag=='meta' and n.attrs.get('name')=='description' and n.attrs.get('content') for n in nodes):error('metadata','Missing description')
    for id,count in Counter(n.attrs['id'] for n in nodes if 'id' in n.attrs).items():
        if count>1:error('duplicate-id',id)
    for id in ('namespace','builder','uns-agent','delivery'):
        if id not in ids:error('module','Missing required module #'+id)
    for id in ('namespace','builder','uns-agent'):
        if id in ids and not any(n.attrs.get('data-visual')=='interactive' and 'data-t0-demo' in n.attrs for n in ids[id].all()):
            error('interactive-demo','Required interactive model missing in #'+id)
    for n in nodes:
        if 'data-visual' in n.attrs:
            kind=n.attrs['data-visual']
            if kind not in ('interactive','evidence','brand','decoration'):error('visual-kind','Unknown visual classification: '+kind)
            if kind=='interactive':
                if 'data-t0-demo' not in n.attrs:error('demo-contract','Interactive visual needs a scoped data-t0-demo root')
                if not n.attrs.get('id','').strip():error('demo-id','Interactive visual needs a unique DOM id for its verification inventory')
                controls=[c for c in n.all() if c.tag in ('button','summary','input','select')]
                if not controls:error('demo-control','Interactive visual has no semantic controls')
            if kind=='evidence' and not n.attrs.get('data-evidence-reason','').strip():error('evidence-reason','Static evidence requires its source/use reason')
        if n.tag in ('img','svg','canvas','video') and n.attrs.get('alt')!='Tier0' and n.attrs.get('aria-hidden')!='true':
            parent=n;visual=None
            while parent:
                if 'data-visual' in parent.attrs:visual=parent.attrs['data-visual'];break
                parent=parent.parent
            if visual is None:error('visual-inventory','Unclassified visual; implement an interactive model or record an evidence/brand/decoration exception')
            if n.tag in ('img','video') and visual=='interactive':error('static-demo','A clickable image/video is not an interactive interface model')
    if 'namespace' in ids:
        nn=list(ids['namespace'].all())
        if not any((n.cls('eam-source') or 'data-uns-source' in n.attrs) and n.text().strip() for n in nn):error('uns-acquisition','Missing readable data sources and acquisition methods')
        if not any((n.cls('uns-model') or 'data-uns-model' in n.attrs) and n.text().strip() for n in nn):error('uns-model','Missing readable UNS business object model')
    if 'builder' in ids:
        bn=list(ids['builder'].all())
        if not any(n.attrs.get('data-t0-demo') for n in bn):error('builder-preview','Builder requires a clickable application preview')
        if not any(n.attrs.get('id')=='builder-prompt' and n.text().strip() for n in bn):error('builder-prompt','Builder prompt is missing')
        editors=[n for n in bn if n.attrs.get('data-t0-demo')=='builder']
        if not editors:error('builder-link','Builder needs an interactive editor paired with its App')
        for editor in editors:
            target=ids.get(editor.attrs.get('data-app-target'))
            if target not in bn or target.attrs.get('data-t0-demo')!='app':error('builder-link','Builder target must be an App in the same module')
            if not all(any(key in n.attrs for n in editor.all()) for key in ('data-builder-diff','data-builder-apply','data-builder-undo')):error('builder-changes','Builder requires preview, apply and undo controls')
    if 'uns-agent' in ids:
        an=list(ids['uns-agent'].all())
        if not any(n.tag=='code' and re.search(r'/(Metric|State|Action)/',n.text()) for n in an):error('agent-source','Missing UNS topic source')
        if not any(n.cls('t0-question') or n.cls('agent-user-request') for n in an):error('agent-question','Missing business question')
        if not any(n.cls('t0-answer') or n.cls('product-answer') for n in an):error('agent-answer','Missing Agent answer')
        if not any(n.cls('t0-analysis') or n.cls('product-card') for n in an):error('agent-result','Missing analysis result')
    if 'delivery' in ids:
        dn=list(ids['delivery'].all());routes=[n for n in dn if n.cls('route')]
        if len(routes)!=2 or any(sum(n.tag=='li' for n in r.all())!=3 for r in routes):error('delivery-structure','Fixed service module requires two routes, each with three items')
        for label,href in [('Apply for Trial ↗','https://tier0.dev/login'),('Talk to team ↗','https://tier0.app/talk-to-team')]:
            if not any(n.tag=='a' and n.text().strip()==label and n.attrs.get('href')==href for n in dn):error('delivery-cta','Missing or altered fixed CTA: '+label)
    visible=dom.root.text()
    # Attributes count too: untranslated alt/labels are user-facing content.
    readable=visible+' '+ ' '.join(v for n in nodes for k,v in n.attrs.items() if k in ('alt','aria-label','title','placeholder') and v)
    if lang=='en' and re.search('[\u4e00-\u9fff]',readable.replace('中文','')):error('untranslated-text','Chinese remains outside the language switch')
    if re.search(r'\{\{[^}]+\}\}|\$(?:heading|prompt|image|answer)\b',readable):error('placeholder','Unresolved content placeholder')
    for term in forbidden:
        if term.casefold() in readable.casefold():error('stale-project','Unexpected project term: '+term)
    for n in nodes:
        for key in ('aria-controls','aria-labelledby','aria-describedby'):
            for target in n.attrs.get(key,'').split():
                if target not in ids:error('aria-reference','Missing '+key+' target: '+target)
        if n.tag=='p':
            t=n.text()
            if len(re.findall('[\u4e00-\u9fff]',t))>120 or len(t.split())>85:warn('long-paragraph',t[:90])
    checked_css=set();referenced_images=[];language_link=False
    def resource(value,base,anchor=False):
        parts=urlsplit(value)
        if parts.scheme in ('https','http','mailto','tel','data'):return
        if parts.scheme or parts.netloc:error('resource-scheme',value);return
        if not parts.path:
            if parts.fragment and anchor and parts.fragment not in ids:error('anchor',value)
            return
        if parts.path.startswith('/'):
            warn('site-root-resource','Requires deployed site check: '+value);return
        dest=base/unquote(parts.path)
        if not dest.is_file():error('missing-resource',str(dest));return
        if dest.suffix=='.css' and dest.resolve() not in checked_css:
            checked_css.add(dest.resolve());css=dest.read_text()
            for m in re.finditer(r'url\(\s*[\'\"]?([^\'\"\)]+)[\'\"]?\s*\)|@import\s+[\'\"]([^\'\"]+)[\'\"]',css):resource((m[1] or m[2]).strip(),dest.parent)
        if anchor and parts.fragment and dest.suffix=='.html':
            target=Document(dest.read_text())
            if not any(n.attrs.get('id')==unquote(parts.fragment) for n in target.root.all()):error('anchor',value)
    for n in nodes:
        for key in ('src','href','poster'):
            if n.attrs.get(key):resource(n.attrs[key],page.parent,anchor=key=='href')
        if n.tag=='img':
            if 'alt' not in n.attrs:error('image-alt','Missing alt: '+n.attrs.get('src',''))
            if not all(str(n.attrs.get(k,'')).isdigit() and int(n.attrs[k])>0 for k in ('width','height')):warn('image-size','Missing image dimensions: '+n.attrs.get('src','')[:80])
            if n.attrs.get('alt')!='Tier0':referenced_images.append(n.attrs.get('src',''))
        if n.tag=='a' and n.attrs.get('lang') and n.attrs['lang']!=lang:
            language_link=True;value=n.attrs.get('href','');parts=urlsplit(value)
            if not parts.scheme and parts.path and not parts.path.startswith('/'):
                target=page.parent/unquote(parts.path)
                if target.is_file():
                    other=Document(target.read_text());on=list(other.root.all());ol=next((x.attrs.get('lang') for x in on if x.tag=='html'),None)
                    if ol!=n.attrs['lang']:error('language-link','Language target does not match link label')
                    back=[x.attrs.get('href','') for x in on if x.tag=='a' and x.attrs.get('lang')==lang]
                    if not any((target.parent/urlsplit(v).path).resolve()==page.resolve() for v in back):error('language-backlink','Other language does not link back')
    if not language_link:warn('language-link','No corresponding-language link detected; required for bilingual delivery')
    if manifest:
        images=manifest.get('images',[]);by_path={x['path']:x for x in images}
        for src in referenced_images:
            key=urlsplit(src).path
            entry=by_path.get(key)
            if not entry:error('image-mapping','Screenshot missing from language manifest: '+key[:100]);continue
            if entry.get('language')!=lang:error('image-language','Screenshot language mismatch: '+key)
            if entry.get('kind') not in ('original','localized'):error('image-provenance','Unknown screenshot kind: '+key)
            if entry.get('kind')=='localized':
                if not entry.get('source'):error('image-provenance','Localized image missing original: '+key)
                else:resource(entry['source'],page.parent)
    elif referenced_images:warn('image-manifest','No evidence-image language manifest; image pixels have not been checked')
    report['static_status']='fail' if report['errors'] else 'pass'
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pages',type=Path,nargs='+');p.add_argument('--manifest',type=Path);p.add_argument('--forbid',action='append',default=[]);p.add_argument('--output',type=Path);a=p.parse_args()
    try:m=json.loads(a.manifest.read_text()) if a.manifest else None
    except (OSError,ValueError) as exc:p.error(str(exc))
    if m is not None and (not isinstance(m,dict) or not isinstance(m.get('images'),list) or any(not isinstance(x,dict) or not isinstance(x.get('path'),str) for x in m['images'])):p.error('Manifest must contain an images array with path strings')
    reports=[audit(page,m,a.forbid) for page in a.pages];data=json.dumps(reports,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(data)
    print(data);return int(any(r['errors'] for r in reports))
if __name__=='__main__':raise SystemExit(main())
