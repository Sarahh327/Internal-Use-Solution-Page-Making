#!/usr/bin/env node
// Existing Playwright/Chromium only. No dependency installation or live services.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'tier0-demo-test-'));
const screenshotDir = process.env.DEMO_SCREENSHOT_DIR;
const python = (...args) => execFileSync(process.env.PYTHON || 'python3', args, {encoding:'utf8'});
(async () => {
  const browser = await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH}:{})});
  const results=[];
  try {
    for (const lang of ['zh-CN','en']) {
      const directory=path.join(temp,lang), config=path.join(root,'assets/components',`example.${lang}.json`);
      python(path.join(__dirname,'render_components.py'),config,'--output',path.join(directory,'components.html'));
      fs.mkdirSync(path.join(directory,'assets'));
      // Resource fixture only. Brand fidelity is not certified by this test.
      fs.writeFileSync(path.join(directory,'assets/tier0-logo-black.svg'),'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="24"></svg>');
      const second=python('-c','import json,sys;sys.path.insert(0,sys.argv[1]);from app_rendering import render_app_demo;c=json.load(open(sys.argv[2]));print(render_app_demo(c["builder"]["preview"],c["language"],"hero-preview"))',__dirname,config);
      const pagePath=path.join(directory,'index.html');
      fs.writeFileSync(pagePath,`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive model test</title><meta name="description" content="Local behavioral fixture"></head><body><h1>EAM</h1>${fs.readFileSync(path.join(directory,'components.html'),'utf8')}<section style="max-width:1180px;margin:auto">${second}</section></body></html>`);
      const context=await browser.newContext({offline:true,reducedMotion:'reduce',viewport:{width:1440,height:1000}});
      const page=await context.newPage(), errors=[], requests=[];
      page.on('pageerror',error=>errors.push(error.message));
      page.on('request',request=>{if(/^https?:/.test(request.url()))requests.push(request.url());});
      await page.goto('file://'+pagePath);await page.locator('#builder-preview[data-ready=true]').waitFor();
      const app=page.locator('#builder-preview'), hero=page.locator('#hero-preview');
      const metric=(key)=>app.locator(`[data-app-metric="${key}"]`).innerText();
      const row=(id)=>app.locator(`[data-app-rows] [data-app-record="${id}"]`);
      assert.equal(await metric('total'),'8'); assert.equal(await metric('open'),'4'); assert.equal(await metric('rate'),'50%');
      await app.locator('[data-app-nav="orders"]').focus();await page.keyboard.press('Space');
      assert.equal(await app.locator('[data-app-rows] tr').count(),8);
      await app.locator('[data-app-status]').selectOption('in_progress');assert.equal(await app.locator('[data-app-rows] tr').count(),2);
      await app.locator('[data-app-search]').fill('M-08');assert.equal(await app.locator('[data-app-rows] tr').count(),1);
      await app.locator('[data-app-search]').fill('no-such-record');assert.equal(await app.locator('[data-app-empty]').isVisible(),true);
      await app.locator('[data-app-search]').fill('');await app.locator('[data-app-status]').selectOption('');
      const firstOrder=await app.locator('[data-app-rows] tr').first().innerText();await app.locator('[data-app-sort]').click();
      assert.notEqual(await app.locator('[data-app-rows] tr').first().innerText(),firstOrder);
      await row('WO-2401').click();await app.locator('[data-detail-complete]').click();
      assert.ok(await app.locator('[data-detail-error]').innerText());assert.equal(await metric('open'),'4');
      for(const check of await app.locator('[data-detail-checks] input').all())await check.check();
      const note=lang==='en'?'Seal replaced; running normally.':'已更换密封，运行正常。';
      await app.locator('[data-detail-note]').fill(note);await page.keyboard.press('Escape');
      assert.equal(await app.locator('[data-app-drawer]').isVisible(),false);
      await row('WO-2401').click();assert.equal(await app.locator('[data-detail-note]').inputValue(),note);
      await app.locator('[data-detail-complete]').click();assert.equal(await metric('open'),'3');assert.equal(await metric('urgent'),'1');assert.equal(await metric('rate'),'63%');
      assert.equal(await app.locator('[data-detail-history] li').count(),2);assert.equal(await app.locator('[data-detail-complete]').isDisabled(),true);
      assert.equal(await hero.locator('[data-app-metric="open"]').innerText(),'4');
      await page.keyboard.press('Escape');await page.waitForFunction(()=>document.activeElement?.dataset.appRecord==='WO-2401');
      await row('WO-2403').click();await app.locator('[data-detail-complete]').click();assert.ok(await app.locator('[data-detail-error]').innerText());
      const owner=JSON.parse(fs.readFileSync(config,'utf8')).builder.preview.people[2];
      await app.locator('[data-detail-owner]').selectOption(owner);await app.locator('[data-detail-assign]').click();
      await page.keyboard.press('Escape');assert.ok((await row('WO-2403').locator('..').locator('..').innerText()).includes(owner));
      await app.locator('[data-app-nav="assets"]').click();await app.locator('[data-app-asset="AC-02"]').click();
      assert.equal(await app.locator('[data-app-rows] tr').count(),2);
      await app.locator('[data-app-location]').selectOption({index:2});assert.equal(await metric('total'),'3');
      await app.locator('[data-app-reset]').click();assert.equal(await metric('open'),'4');assert.equal(await metric('total'),'8');
      await app.locator('[data-app-filter="pending"]').click();assert.equal(await app.locator('[data-app-rows] tr').count(),2);
      await app.locator('[data-app-reset]').click();
      const namespace=page.locator('#namespace');await namespace.locator('[data-source-select="1"]').click();
      assert.equal(await namespace.locator('[data-source-panel="1"]').isVisible(),true);
      const branch=namespace.locator('.t0-model > details');await branch.locator(':scope > summary').focus();await page.keyboard.press('Enter');
      assert.equal(await branch.getAttribute('open'),null);await namespace.locator('[data-source-reset]').click();assert.notEqual(await branch.getAttribute('open'),null);
      assert.equal(await namespace.locator('[data-source-panel="0"]').isVisible(),true);
      const agent=page.locator('#uns-agent'),tabs=agent.locator('[role=tab]');
      await tabs.first().focus();await page.keyboard.press('ArrowRight');assert.equal(await tabs.last().getAttribute('aria-selected'),'true');
      await page.keyboard.press('Home');assert.equal(await tabs.first().getAttribute('aria-selected'),'true');
      const answer=await agent.locator('[data-agent-scenario="0"] .t0-answer').innerText();
      await agent.locator('textarea').fill('<img src=x onerror=alert(1)>');await agent.locator('[type=submit]').click();
      assert.equal(await agent.locator('[data-agent-scenario="0"] .t0-answer').innerText(),answer);assert.equal(await agent.locator('img').count(),0);
      assert.ok(await agent.locator('[data-agent-status]').innerText());await agent.locator('summary').filter({hasText:'Skills'}).click();
      await agent.locator('[data-agent-preset="1"]').click();await agent.locator('[type=submit]').click();assert.equal(await agent.locator('[data-agent-scenario="1"]').isVisible(),true);
      await agent.locator('[data-agent-save="1"]').click();await tabs.first().click();await agent.locator('[data-agent-save="1"]').click();assert.equal(await agent.locator('[data-agent-cards] .t0-analysis').count(),1);
      await agent.locator('summary').filter({hasText:'Scheduled Tasks'}).click();await agent.locator('[data-agent-task]').click();await agent.locator('[data-agent-task]').click();assert.equal(await agent.locator('[data-agent-tasks] li').count(),1);
      await agent.locator('[data-agent-reset]').click();assert.equal(await agent.locator('[data-agent-cards] .t0-analysis').count(),0);assert.equal(await agent.locator('[data-agent-tasks] li').count(),0);assert.equal(await agent.locator('details[open]').count(),0);
      const builder=page.locator('#builder-editor');
      const choose=async id=>{await builder.locator(`[data-builder-preset="${id}"]`).click();assert.equal(await builder.locator('[data-builder-diff]').isVisible(),true);};
      const apply=async id=>{await choose(id);await builder.locator('[data-builder-apply]').click();};
      await builder.locator('#builder-prompt').fill('<img src=x onerror=alert(1)>');await builder.locator('[type=submit]').click();
      assert.equal(await builder.locator('[data-builder-version]').innerText(),'v1');assert.equal(await builder.locator('[data-builder-apply]').isDisabled(),true);
      await choose('board');assert.equal(await app.locator('[data-app-nav="board"]').isVisible(),false);
      await builder.locator('#builder-prompt').fill('Unprepared edit');assert.equal(await builder.locator('[data-builder-apply]').isDisabled(),true);
      await apply('board');assert.equal(await builder.locator('[data-builder-version]').innerText(),'v2');assert.equal(await app.locator('[data-app-view="board"]').isVisible(),true);
      assert.equal(await app.locator('.t0-board-card').count(),8);assert.equal(await hero.locator('[data-app-nav="board"]').isVisible(),false);
      await app.evaluate(el=>el.dispatchEvent(new CustomEvent('t0:app-command',{detail:{action:'apply',id:'board'}})));
      assert.equal(await builder.locator('[data-builder-version]').innerText(),'v2');
      await apply('priority');assert.equal(await app.locator('[data-app-priority-heading]').isVisible(),true);assert.ok((await app.locator('[data-app-rows] tr').first().innerText()).includes('WO-2401'));
      await apply('downtime');assert.equal(await builder.locator('[data-builder-version]').innerText(),'v4');await builder.locator('[data-builder-inspect]').click();
      for(const check of await app.locator('[data-detail-checks] input').all())await check.check();
      await app.locator('[data-detail-note]').fill(lang==='en'?'Repair complete.':'已处理完成。');
      for(const value of ['','-1','1.5']){await app.locator('[data-detail-downtime]').fill(value);await app.locator('[data-detail-complete]').click();assert.equal(await metric('open'),'4');assert.ok(await app.locator('[data-detail-error]').innerText());}
      await app.locator('[data-detail-downtime]').fill('12');await app.locator('[data-detail-complete]').click();assert.equal(await metric('open'),'3');
      assert.ok((await app.locator('[data-detail-history]').innerText()).includes('12'));await page.keyboard.press('Escape');
      await builder.locator('[data-builder-undo]').click();assert.equal(await builder.locator('[data-builder-version]').innerText(),'v3');assert.equal(await metric('open'),'3');
      await builder.locator('[data-builder-undo]').click();assert.equal(await app.locator('[data-app-priority-heading]').isVisible(),false);
      await builder.locator('[data-builder-undo]').click();assert.equal(await app.locator('[data-app-nav="board"]').isVisible(),false);assert.equal(await builder.locator('[data-builder-undo]').isDisabled(),true);
      await app.locator('[data-app-reset]').click();assert.equal(await builder.locator('[data-builder-version]').innerText(),'v1');assert.equal(await metric('open'),'4');
      const prompt=lang==='en'?'Editable local requirements':'可编辑的本地需求';await page.locator('#builder-prompt').fill(prompt);
      // No system clipboard mutation: test success and failure deterministically.
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{window.copiedPrompt=value;}}}));
      await page.locator('[data-copy-prompt]').click();await page.waitForFunction(expected=>window.copiedPrompt===expected,prompt);
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
      await page.locator('[data-copy-prompt]').click();assert.equal(await page.locator('#builder-prompt').evaluate(el=>el.selectionEnd-el.selectionStart),prompt.length);
      await page.addScriptTag({path:path.join(directory,'app-demo.js')});await page.addScriptTag({path:path.join(directory,'components.js')});await page.addScriptTag({path:path.join(directory,'builder-demo.js')});
      await agent.locator('[data-agent-save="0"]').click();assert.equal(await agent.locator('[data-agent-cards] .t0-analysis').count(),1);await agent.locator('[data-agent-reset]').click();
      for(const width of [1440,1024,375]){
        await page.setViewportSize({width,height:1000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Overflow at ${width} in ${lang}`);
        await app.locator('[data-app-nav="orders"]').click();
        if(screenshotDir){fs.mkdirSync(screenshotDir,{recursive:true});await app.screenshot({path:path.join(screenshotDir,`${lang}-${width}-orders.png`)});}
        await row('WO-2401').click();assert.equal(await app.locator('[data-app-drawer]').isVisible(),true);
        if(screenshotDir)await page.screenshot({path:path.join(screenshotDir,`${lang}-${width}-detail.png`)});
        await page.keyboard.press('Escape');
        await app.locator('[data-app-reset]').click();
        if(screenshotDir){fs.mkdirSync(screenshotDir,{recursive:true});await app.screenshot({path:path.join(screenshotDir,`${lang}-${width}-app.png`)});}
        await apply('board');assert.equal(await builder.locator('[data-builder-version]').innerText(),'v2');
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
        if(screenshotDir)await page.locator('#builder').screenshot({path:path.join(screenshotDir,`${lang}-${width}-builder-paired.png`)});
        await apply('downtime');await builder.locator('[data-builder-inspect]').click();assert.equal(await app.locator('[data-detail-downtime]').isVisible(),true);
        for(const check of await app.locator('[data-detail-checks] input').all())await check.check();
        await app.locator('[data-detail-note]').fill(lang==='en'?'Checked and repaired.':'已检查修复。');await app.locator('[data-detail-downtime]').fill('5');await app.locator('[data-detail-complete]').click();
        assert.equal(await metric('open'),'3');await page.keyboard.press('Escape');await app.locator('[data-app-reset]').click();

      }
      // A single HTML file in an otherwise empty folder: no build or sibling assets.
      const standalone=path.join(temp,'isolated-'+lang,'demo.html');python(path.join(__dirname,'render_demo.py'),config,'--with-builder','--output',standalone);
      await page.goto('file://'+standalone);const standaloneApp=page.locator('#app-reference');
      await standaloneApp.locator('[data-app-nav="orders"]').click();assert.equal(await standaloneApp.locator('[data-app-rows] tr').count(),8);
      await page.locator('[data-builder-preset="board"]').click();await page.locator('[data-builder-apply]').click();assert.equal(await standaloneApp.locator('[data-app-view="board"]').isVisible(),true);
      await page.reload();assert.equal(await standaloneApp.locator('[data-app-metric="open"]').innerText(),'4');assert.equal(await page.locator('[data-builder-version]').innerText(),'v1');
      const nojs=await browser.newContext({javaScriptEnabled:false,offline:true});const staticPage=await nojs.newPage();await staticPage.goto('file://'+standalone);
      assert.equal(await staticPage.locator('[data-app-metric="total"]').innerText(),'8');assert.equal(await staticPage.locator('[data-demo-control]:enabled').count(),0);
      assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
      results.push({lang,appViewsSearchAndFilters:true,validatedWorkCompletion:true,linkedMetricsAndAssets:true,assignmentAndHistory:true,resetAndInstanceIsolation:true,namespace:true,agent:true,keyboardAndFocus:true,widths:[1440,1024,375],offlineSingleFile:true,noJsReadable:true,builderPreviewApplyUndo:true,builderAppVersionSync:true,requiredDowntimeValidation:true,pageErrors:errors,networkRequests:requests});
      await nojs.close();await context.close();
    }
    console.log(JSON.stringify(results,null,2));
  }finally{await browser.close();fs.rmSync(temp,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exit(1);});
