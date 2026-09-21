#!/usr/bin/env python3
"""Meaningful positive/negative fixtures; no browser or network required."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from render_components import render,ROOT
from check_solution import audit

class ComponentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.config=json.loads((ROOT/'assets/components/example.en.json').read_text())
        self.zh=json.loads((ROOT/'assets/components/example.zh-CN.json').read_text())
        (self.p/'assets').mkdir()
        # The audit checks resource presence, not decoded image content or OCR.
        for name in ('dashboard.png','dashboard.en.png','tier0-logo-black.svg'):(self.p/'assets'/name).write_text('resource fixture')
        self.write('index.html','zh-CN',render(self.zh),'en.html','en')
        self.write('en.html','en',render(self.config),'index.html','zh-CN')
        self.manifest={'images':[{'path':'assets/dashboard.en.png','language':'en','kind':'localized','source':'assets/dashboard.png'},{'path':'assets/dashboard.png','language':'zh-CN','kind':'original'}]}
    def tearDown(self):self.tmp.cleanup()
    def write(self,name,lang,body,other,otherlang):
        image='assets/dashboard.en.png' if lang=='en' else 'assets/dashboard.png'
        body+=f'<figure data-visual="evidence" data-evidence-reason="User-requested original capture"><img src="{image}" alt="Original evidence" width="100" height="100"></figure>'
        (self.p/name).write_text(f'<!doctype html><html lang="{lang}"><head><title>EAM</title><meta name="description" content="Asset management"></head><body><h1>EAM</h1><a href="{other}" lang="{otherlang}">EN / 中文</a>{body}</body></html>')
    def codes(self):return {e['code'] for e in audit(self.p/'en.html',self.manifest)['errors']}
    def mutate(self,old,new):
        p=self.p/'en.html';p.write_text(p.read_text().replace(old,new))
    def test_complete_bilingual_pages(self):
        self.assertEqual(self.codes(),set());self.assertEqual(audit(self.p/'index.html',self.manifest)['errors'],[])
        self.assertTrue(audit(self.p/'en.html',self.manifest)['manual_required'])
    def test_missing_namespace(self):
        self.mutate('id="namespace"','id="removed"');self.assertIn('module',self.codes())
    def test_tree_without_acquisition(self):
        self.mutate('data-uns-source','data-removed');self.assertIn('uns-acquisition',self.codes())
    def test_acquisition_without_model(self):
        self.mutate('data-uns-model','data-removed');self.assertIn('uns-model',self.codes())
    def test_legacy_eam_namespace(self):
        self.mutate('data-uns-source','class="eam-source"');self.mutate('data-uns-model','class="uns-model"');self.assertEqual(self.codes(),set())
    def test_missing_agent(self):
        self.mutate('id="uns-agent"','id="removed"');self.assertIn('module',self.codes())
    def test_broken_resource(self):
        (self.p/'assets/dashboard.en.png').unlink();self.assertIn('missing-resource',self.codes())
    def test_image_language_mismatch(self):
        self.manifest['images'][0]['language']='zh-CN';self.assertIn('image-language',self.codes())
    def test_stale_project(self):
        r=audit(self.p/'en.html',self.manifest,['EAM']);self.assertIn('stale-project',{e['code'] for e in r['errors']})
    def test_translation_and_placeholder(self):
        self.mutate('<h1>EAM</h1>','<h1>设备 {{heading}}</h1>');self.assertTrue({'untranslated-text','placeholder'}<=self.codes())
    def test_service_drift(self):
        self.mutate('Apply for Trial ↗','Free Trial');self.assertIn('delivery-cta',self.codes())
    def test_duplicate_id_and_anchor(self):
        self.mutate('</body>','<div id="builder"></div><a href="#missing">Jump</a></body>');self.assertTrue({'duplicate-id','anchor'}<=self.codes())
    def test_css_dependency(self):
        (self.p/'x.css').write_text('@import "missing.css";div{background:url("missing.png")}')
        self.mutate('</head>','<link rel="stylesheet" href="x.css"></head>');self.assertIn('missing-resource',self.codes())
    def test_source_mapping_rejected(self):
        c=copy.deepcopy(self.config);c['agent']['field_refs'].append('v1/Factory/State/inventory#expiry')
        with self.assertRaises(ValueError):render(c)
    def test_no_script_injection(self):
        c=copy.deepcopy(self.config);c['builder']['prompt']='<script>alert(1)</script>'
        s=render(c);self.assertNotIn('<script>',s);self.assertIn('&lt;script&gt;',s)
        c['logo']='javascript:alert(1)'
        with self.assertRaises(ValueError):render(c)
    def test_no_unsubstantiated_verified_result(self):
        c=copy.deepcopy(self.config);c['agent']['data_status']='verified'
        with self.assertRaises((ValueError,KeyError)):render(c)
    def test_cli_and_overwrite_guard(self):
        target=self.p/'generated/fragments.html';cmd=[sys.executable,str(ROOT/'scripts/render_components.py'),str(ROOT/'assets/components/example.en.json'),'--output',str(target)]
        first=subprocess.run(cmd,capture_output=True);self.assertEqual(first.returncode,0,first.stderr)
        self.assertTrue((target.parent/'components.css').is_file())
        before=target.read_bytes();second=subprocess.run(cmd,capture_output=True);self.assertNotEqual(second.returncode,0);self.assertEqual(before,target.read_bytes())
    def test_query_fragment_and_reciprocal_language(self):
        self.mutate('href="index.html"','href="index.html?v=2#builder"');self.assertNotIn('language-link',self.codes());self.assertNotIn('anchor',self.codes())
        p=self.p/'index.html';p.write_text(p.read_text().replace('href="en.html"','href="unrelated.html"'));self.assertIn('language-backlink',self.codes())
    def test_app_requires_meaningful_data_and_lifecycle_states(self):
        c=copy.deepcopy(self.config);c['builder']['preview']['records']=c['builder']['preview']['records'][:2]
        with self.assertRaisesRegex(ValueError,'six coherent records'):render(c)
    def test_completed_record_requires_work_evidence(self):
        c=copy.deepcopy(self.config);r=c['builder']['preview']['records'][0];r['status']='completed'
        with self.assertRaises(ValueError):render(c)
    def test_app_configuration_cannot_break_out_of_json(self):
        c=copy.deepcopy(self.config);c['builder']['preview']['records'][0]['note']='</script><img src=x onerror=alert(1)>'
        s=render(c);self.assertNotIn('</script><img',s);self.assertIn('\\u003c/script\\u003e',s)
    def test_agent_only_lists_referenced_sources(self):
        from demo_rendering import render_agent
        self.assertNotIn('equipment_status',render_agent(self.config['agent'],'en'))
    def test_namespace_topic_mapping(self):
        c=copy.deepcopy(self.config);c['namespace']['sources'][0]['topic']='v1/Unknown/State/unknown'
        with self.assertRaises(ValueError):render(c)
    def test_followup_must_have_a_prepared_response(self):
        c=copy.deepcopy(self.config);c['agent']['followup']='Invent an unprepared answer'
        with self.assertRaises(ValueError):render(c)
    def test_example_fields_validated(self):
        c=copy.deepcopy(self.config);c['agent']['examples'][0]['field_refs']=['unknown#field']
        with self.assertRaises(ValueError):render(c)
    def test_static_demo_and_unclassified_visual_rejected(self):
        self.mutate('</body>','<img src="assets/dashboard.en.png" alt="Demo" width="100" height="100"></body>')
        self.assertIn('visual-inventory',self.codes())
        self.mutate('alt="Demo"','alt="Demo" data-visual="interactive" data-t0-demo="custom"')
        self.assertIn('static-demo',self.codes())
    def test_missing_demo_and_broken_control_target(self):
        self.mutate('data-t0-demo="app"','data-removed="app"')
        self.mutate('aria-controls="agent-chat"','aria-controls="missing-panel"')
        self.assertTrue({'builder-link','demo-contract','aria-reference'}<=self.codes())
    def test_evidence_reason_required(self):
        self.mutate('data-evidence-reason="User-requested original capture"','')
        self.assertIn('evidence-reason',self.codes())
    def test_interactive_visual_requires_inventory_id(self):
        self.mutate('id="builder-preview"','');self.assertIn('demo-id',self.codes())
    def test_builder_requires_a_paired_app(self):
        self.mutate('data-app-target="builder-preview"','data-app-target="agent-demo"')
        self.assertIn('builder-link',self.codes())
    def test_builder_cannot_be_copy_only(self):
        self.mutate('data-builder-apply','data-removed')
        self.assertIn('builder-changes',self.codes())
    def test_builder_changes_are_allowlisted(self):
        c=copy.deepcopy(self.config);c['builder']['changes'][0]['id']='execute_arbitrary_script'
        with self.assertRaisesRegex(ValueError,'Unsupported Builder change'):render(c)
    def test_builder_prompt_matching_is_unambiguous(self):
        c=copy.deepcopy(self.config);c['builder']['changes'][1]['prompt']=c['builder']['changes'][0]['prompt']
        with self.assertRaisesRegex(ValueError,'prompts must be unique'):render(c)
    def test_builder_configuration_is_escaped(self):
        c=copy.deepcopy(self.config);c['builder']['changes'][0]['after']='</script><img src=x onerror=alert(1)>'
        s=render(c);self.assertNotIn('</script><img',s);self.assertIn('\\u003c/script\\u003e',s)
if __name__=='__main__':unittest.main()
