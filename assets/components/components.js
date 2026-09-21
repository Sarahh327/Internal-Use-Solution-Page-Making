// Local, deterministic demo state only. Never generate apps, query UNS or schedule jobs.
(() => {
  function init() {
    const en = document.documentElement.lang.startsWith('en');
    const copy = (zh, english) => en ? english : zh;
    document.querySelectorAll('[data-component="builder"]').forEach(module => {
      const button = module.querySelector('[data-copy-prompt]');
      if (!button || button.dataset.ready) return;
      button.dataset.ready = 'true'; button.disabled = false;
      button.addEventListener('click', async () => {
        const input = module.querySelector('#builder-prompt');
        const status = module.querySelector('[data-copy-status]');
        try { await navigator.clipboard.writeText(input.value); status.textContent = copy('需求已复制。', 'Prompt copied.'); }
        catch { input.focus(); input.select(); status.textContent = copy('已选中需求，请使用复制快捷键。', 'Prompt selected. Use your copy shortcut.'); }
      });
    });
    document.querySelectorAll('[data-t0-demo]').forEach(root => {
      if (root.dataset.ready) return;
      const all = selector => [...root.querySelectorAll(selector)];
      const one = selector => root.querySelector(selector);
      const disclosures = all('details').map(element => [element, element.open]);
      const resetDisclosures = () => disclosures.forEach(([element, open]) => { element.open = open; });
      if (root.dataset.t0Demo === 'namespace') {
        const selectSource = b => {
          all('[data-source-select]').forEach(other => other.setAttribute('aria-pressed', String(other === b)));
          all('[data-source-panel]').forEach(p => { p.hidden = p.dataset.sourcePanel !== b.dataset.sourceSelect; });
        };
        all('[data-source-select]').forEach(b => b.addEventListener('click', () => selectSource(b)));
        one('[data-source-reset]').addEventListener('click', () => {
          selectSource(one('[data-source-select]')); resetDisclosures();
        });
      } else if (root.dataset.t0Demo === 'agent') {
        const tabs = all('[role="tab"]'), panels = all('[role="tabpanel"]');
        const scenarios = all('[data-agent-scenario]'), input = one('#agent-followup');
        const status = one('[data-agent-status]'), cards = one('[data-agent-cards]');
        const saved = new Set(), tasks = new Set(); let current = 0;
        const activateTab = tab => {
          tabs.forEach(t => { t.setAttribute('aria-selected', String(t === tab)); t.tabIndex = t === tab ? 0 : -1; });
          panels.forEach(p => { p.hidden = p.id !== tab.getAttribute('aria-controls'); });
        };
        tabs.forEach((tab, index) => {
          tab.addEventListener('click', () => activateTab(tab));
          tab.addEventListener('keydown', event => {
            let next;
            if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
            if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
            if (event.key === 'Home') next = 0;
            if (event.key === 'End') next = tabs.length - 1;
            if (next === undefined) return;
            event.preventDefault(); activateTab(tabs[next]); tabs[next].focus();
          });
        });
        const showScenario = index => {
          current = index; scenarios.forEach((s, i) => { s.hidden = i !== index; }); activateTab(tabs[0]);
          status.textContent = copy('已切换预设分析示例。', 'Prepared analysis example loaded.');
        };
        all('[data-agent-preset]').forEach(b => b.addEventListener('click', () => {
          const index = Number(b.dataset.agentPreset);
          input.value = scenarios[index].querySelector('.t0-question').textContent;
          showScenario(index);
        }));
        const normalize = s => s.trim().replace(/\s+/g, ' ').toLowerCase();
        one('[data-agent-form]').addEventListener('submit', event => {
          event.preventDefault();
          const index = scenarios.findIndex(s => normalize(s.querySelector('.t0-question').textContent) === normalize(input.value));
          if (index < 0) { status.textContent = copy('此演示仅支持 Skills 中的预设问题，请选择一个示例。', 'This demo supports the prepared questions in Skills. Select an example.'); return; }
          showScenario(index);
        });
        all('[data-agent-save]').forEach(b => b.addEventListener('click', () => {
          const id = b.dataset.agentSave;
          if (!saved.has(id)) {
            const card = scenarios[Number(id)].querySelector('.t0-analysis').cloneNode(true);
            cards.append(card); saved.add(id); one('[data-agent-empty]').hidden = true;
          }
          status.textContent = copy('示例卡片已加入本页 Card List。', 'Example card added to this page’s Card List.');
          activateTab(tabs[1]); tabs[1].focus();
        }));
        one('[data-agent-task]').addEventListener('click', () => {
          if (!tasks.has(current)) {
            const li = document.createElement('li'); li.textContent = scenarios[current].querySelector('.t0-question').textContent;
            one('[data-agent-tasks]').append(li); tasks.add(current);
          }
          status.textContent = copy('已加入本页示例任务，未创建真实定时任务。', 'Added to this page’s example tasks; no real schedule was created.');
        });
        one('[data-agent-reset]').addEventListener('click', () => {
          cards.replaceChildren(); one('[data-agent-tasks]').replaceChildren(); saved.clear(); tasks.clear();
          one('[data-agent-empty]').hidden = false; input.value = input.defaultValue;
          showScenario(0); resetDisclosures(); status.textContent = copy('示例已重置。', 'Example reset.');
        });
      } else return; // Custom demos provide their own initializer; never enable inert controls.
      root.dataset.ready = 'true'; all('[data-demo-control]').forEach(b => { b.disabled = false; });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
