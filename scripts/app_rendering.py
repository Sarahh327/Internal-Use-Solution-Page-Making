"""Product-quality local app model: one dataset for work, assets and metrics."""
import json
import re
from datetime import date, timedelta
from demo_rendering import text, template


def labels(lang):
    en = lang == 'en'
    pairs = {
        'overview': ('维护工作台', 'Maintenance desk'), 'orders': ('维护工单', 'Work orders'),
        'assets': ('设备台账', 'Assets'), 'navigation': ('应用导航', 'Application navigation'),
        'local': ('交互示例', 'Interactive example'), 'reset': ('重置', 'Reset'),
        'location': ('区域', 'Area'), 'all_locations': ('全部区域', 'All areas'),
        'total': ('工单总数', 'Total orders'), 'open': ('待处理', 'Open orders'),
        'urgent': ('紧急', 'Urgent'), 'urgent_open': ('紧急待办', 'Urgent open'), 'rate': ('完成率', 'Completion rate'),
        'trend_title': ('完成工单', 'Completed work'), 'seven_days': ('最近 7 天', 'Last 7 days'),
        'distribution': ('工单状态分布', 'Work by status'), 'records_label': ('条工单', 'orders'),
        'attention': ('需要处理', 'Needs attention'), 'all_orders': ('全部工单', 'All work orders'),
        'search': ('搜索', 'Search'), 'search_placeholder': ('工单、设备或负责人', 'Order, asset or owner'),
        'status_label': ('状态', 'Status'), 'all_statuses': ('全部状态', 'All statuses'),
        'pending': ('待执行', 'Queued'), 'in_progress': ('处理中', 'In progress'), 'completed': ('已完成', 'Completed'),
        'normal': ('常规', 'Normal'), 'sort': ('截止日期', 'Due date'),
        'empty': ('没有符合条件的工单。调整筛选后重试。', 'No matching work orders. Adjust your filters.'),
        'id_label': ('工单 / 工作内容', 'Order / work'), 'asset_label': ('设备', 'Asset'),
        'owner_label': ('负责人', 'Owner'), 'unassigned': ('未分派', 'Unassigned'),
        'priority_label': ('优先级', 'Priority'), 'close': ('关闭详情', 'Close details'),
        'save_owner': ('保存负责人', 'Save owner'), 'checklist': ('作业检查', 'Work checklist'),
        'note_label': ('处理记录', 'Completion note'), 'complete': ('完成工单', 'Complete order'),
        'history': ('活动记录', 'Activity'), 'related': ('查看相关工单', 'View related work'),
        'ready': ('暂无待处理工单', 'No outstanding work'), 'asset_attention': ('有待办', 'Needs work'),
        'check_error': ('请完成全部检查项并填写处理记录。', 'Complete every check and add a completion note.'),
        'owner_error': ('请先选择并保存负责人。', 'Select and save an owner first.'),
        'owner_saved': ('负责人已更新', 'Owner updated'), 'complete_saved': ('工单已完成', 'Order completed'),
        'reset_done': ('已恢复示例初始数据。', 'Initial example data restored.'),
        'nojs': ('启用 JavaScript 后可切换视图和操作工单。', 'Enable JavaScript to change views and operate work orders.'),
        'board': ('状态看板', 'Status board'), 'downtime': ('停机时长（分钟）', 'Downtime (minutes)'),
        'downtime_error': ('紧急工单须填写大于等于 0 的整数停机分钟数。', 'Urgent work requires a whole number of downtime minutes, zero or greater.'),
        'change_applied': ('Builder 改动已应用', 'Builder change applied'),
        'new_rule': ('紧急工单完工规则', 'Urgent completion rule'),
        'inspect_change': ('查看改动', 'Inspect change'),
        'no_urgent': ('当前范围没有未完成的紧急工单。', 'No open urgent work in the current area.'),
    }
    return {key: pair[1 if en else 0] for key, pair in pairs.items()}


def render_app_demo(config, lang, demo_id='builder-preview'):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', demo_id):
        raise ValueError('demo_id must be a lowercase HTML identifier')
    l = labels(lang)
    records = config['records']
    today = date.fromisoformat(config['as_of'])
    if len(records) < 6 or len({r['status'] for r in records}) < 3:
        raise ValueError('App preview needs at least six coherent records across three lifecycle states')
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('App record IDs must be unique')
    for person in config['people']: text(person)
    if len(set(config['people'])) != len(config['people']): raise ValueError('People must be unique')
    assets = {}
    for r in records:
        for key in ('id', 'title', 'asset', 'asset_name', 'location', 'due'): text(r[key])
        date.fromisoformat(r['due'])
        if r['status'] not in ('pending', 'in_progress', 'completed') or r['priority'] not in ('urgent', 'normal'):
            raise ValueError('Unsupported record status or priority')
        if r['owner'] and r['owner'] not in config['people']: raise ValueError('Owner must be in people')
        if not isinstance(r['note'], str) or not r['checks'] or not r['history']: raise ValueError('Record needs a note, checks and history')
        for check in r['checks']:
            text(check['label'])
            if not isinstance(check['checked'], bool): raise ValueError('Checklist state must be boolean')
        for event in r['history']: text(event)
        if r['status'] == 'completed':
            if not r['owner'] or not r['note'].strip() or not all(c['checked'] for c in r['checks']): raise ValueError('Completed work requires owner, completed checks and note')
            if date.fromisoformat(r['completed_on']) > today: raise ValueError('Completion cannot be after as_of')
        elif r.get('completed_on'): raise ValueError('Open work cannot have a completion date')
        asset = (r['asset_name'], r['location'])
        if r['asset'] in assets and assets[r['asset']] != asset: raise ValueError('Asset identity must be consistent')
        assets[r['asset']] = asset
    options = lambda values: ''.join('<option value="' + text(v) + '">' + text(v) + '</option>' for v in values)
    badge = lambda value: '<span class="t0-badge" data-tone="' + value + '">' + text(l[value]) + '</span>'
    total = len(records); opened = [r for r in records if r['status'] != 'completed']
    metrics = zip(('total', 'open', 'urgent', 'rate'), (total, len(opened), sum(r['priority'] == 'urgent' for r in opened), str(int((total-len(opened))/total*100+0.5))+'%'))
    rows = ''
    for r in records:
        rows += '<tr><th scope="row"><button type="button" disabled data-demo-control data-app-record="' + text(r['id']) + '"><span class="t0-record-id">' + text(r['id']) + '</span><strong>' + text(r['title']) + '</strong></button></th><td>' + text(r['asset']) + '</td><td>' + badge(r['status']) + '</td><td>' + text(r['owner'] or l['unassigned']) + '</td><td>' + text(r['due'][5:]) + '</td></tr>'
    attention = ''.join('<button type="button" disabled data-demo-control class="t0-attention-row" data-app-record="' + text(r['id']) + '">' + badge(r['priority']) + '<span><strong>' + text(r['title']) + '</strong><small>' + text(r['id']+' · '+r['asset']) + '</small></span><span>' + text(r['due'][5:]) + ' ↗</span></button>' for r in sorted(opened, key=lambda r: (r['priority'] != 'urgent', r['due']))[:4])
    days = [today-timedelta(days=i) for i in reversed(range(7))]
    counts = [sum(r.get('completed_on') == d.isoformat() for r in records) for d in days]
    trend = ''.join('<div class="t0-week-column"><strong>'+str(n)+'</strong><span style="height:'+str(n/max(1,max(counts))*100)+'px"></span><small>'+d.strftime('%m/%d')+'</small></div>' for d,n in zip(days,counts))
    bars = ''
    for status in ('pending','in_progress','completed'):
        count = sum(r['status'] == status for r in records)
        bars += '<button type="button" disabled data-demo-control data-app-filter="'+status+'"><span>'+text(l[status])+'</span><span class="t0-bar-track"><i style="width:'+str(count/total*100)+'%"></i></span><strong>'+str(count)+'</strong></button>'
    asset_cards = ''.join('<article class="t0-app-card"><span class="t0-record-id">'+text(id)+'</span><h4>'+text(name)+'</h4><p>'+text(location)+'</p><button type="button" disabled data-demo-control data-app-asset="'+text(id)+'">'+text(l['related'])+' →</button></article>' for id,(name,location) in assets.items())
    payload = json.dumps({'data':config,'labels':l},ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    return template('app-demo.html', {
        **{k:text(v) for k,v in l.items()}, **{k:text(config[k]) for k in ('title','workspace','as_of')},
        'demo_id':demo_id, 'config':payload,
        'nav': ''.join('<button type="button" disabled data-demo-control data-app-nav="'+key+'" aria-controls="'+demo_id+'-'+key+'" aria-pressed="'+str(key=='overview').lower()+'"><span aria-hidden="true">'+symbol+'</span>'+text(l[key])+'</button>' for key,symbol in (('overview','▦'),('orders','☷'),('assets','◇'))),
        'locations':'<option value="">'+text(l['all_locations'])+'</option>'+options(list(dict.fromkeys(r['location'] for r in records))),
        'statuses':'<option value="">'+text(l['all_statuses'])+'</option>'+''.join('<option value="'+v+'">'+text(l[v])+'</option>' for v in ('pending','in_progress','completed')),
        'people':'<option value="">'+text(l['unassigned'])+'</option>'+options(config['people']),
        'metrics':''.join('<article class="t0-metric"><span>'+text(l['urgent_open' if key=='urgent' else key])+'</span><strong data-app-metric="'+key+'">'+str(value)+'</strong></article>' for key,value in metrics),
        'trend':trend,'bars':bars,'attention_rows':attention,'rows':rows,'asset_cards':asset_cards,
        'columns':''.join('<th scope="col">'+text(l[key])+'</th>' for key in ('id_label','asset_label','status_label','owner_label','sort')),
    })
