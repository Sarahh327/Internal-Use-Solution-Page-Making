// Builder edits an explicitly paired local App through an allowlisted event contract.
(() => {
  function init() {
    document.querySelectorAll('[data-t0-demo="builder"]').forEach(editor => {
      if (editor.dataset.ready) return;
      const module = editor.closest('[data-component="builder"]');
      const app = module.querySelector('#'+CSS.escape(editor.dataset.appTarget));
      if (!app || app.dataset.t0Demo !== 'app') return;
      const one = selector => editor.querySelector(selector);
      const changes = JSON.parse(one('[data-builder-config]').textContent);
      const en = document.documentElement.lang.startsWith('en');
      const copy = (zh,english) => en ? english : zh;
      const input = one('#builder-prompt'), status = one('[data-builder-status]');
      const normalize = value => value.trim().replace(/\s+/g,' ').toLowerCase();
      let pending, applied, state;
      const clearCopyStatus = () => { const copyStatus=one('[data-copy-status]');if(copyStatus)copyStatus.textContent=''; };
      const command = (action,id) => app.dispatchEvent(new CustomEvent('t0:app-command',{detail:{action,id}}));
      function updateControls() {
        one('[data-builder-apply]').disabled = !pending || !state || state.changes.includes(pending.id);
        one('[data-builder-undo]').disabled = !state?.canUndo;
        one('[data-builder-inspect]').hidden = !applied || !state?.changes.includes(applied.id);
      }
      function preview() {
        pending = changes.find(c => normalize(c.prompt) === normalize(input.value));
        one('[data-builder-diff]').hidden = !pending;
        if (!pending) status.textContent=copy('当前演示支持上方的预设需求，请选择一条查看 App 改动。','Choose one of the prepared changes above to preview its App behavior.');
        else {
          one('[data-builder-change-title]').textContent=pending.title;
          one('[data-builder-before]').textContent=pending.before;
          one('[data-builder-after]').textContent=pending.after;
          status.textContent=state?.changes.includes(pending.id) ? copy('此改动已在当前 App 中生效。','This change is already active in the App.') : copy('变更已预览，应用后即可操作。','Change preview ready. Apply it to try the behavior.');
        }
        updateControls();
      }
      app.addEventListener('t0:app-state',event => {
        state=event.detail; one('[data-builder-version]').textContent='v'+state.revision;
        if (state.action==='apply') {
          applied=changes.find(c => c.id===state.changed);
          status.textContent=copy('已应用到本地 App：','Applied to the local App: ')+(applied?.title || '');
        }
        if (state.action==='undo') status.textContent=copy('界面改动已撤销，工单操作记录保留。','UI change undone; work-order records are retained.');
        if (state.action==='reset') { pending=undefined;applied=undefined;input.value=input.defaultValue;one('[data-builder-diff]').hidden=true;clearCopyStatus();status.textContent=copy('App 与 Builder 已恢复初态。','App and Builder restored to their initial state.'); }
        editor.querySelectorAll('[data-builder-control]').forEach(control => {control.disabled=false;});
        updateControls();
      });
      editor.querySelectorAll('[data-builder-preset]').forEach(b => b.addEventListener('click',() => {
        input.value=changes.find(c => c.id===b.dataset.builderPreset).prompt;clearCopyStatus();preview();
      }));
      input.addEventListener('input',() => { pending=undefined;one('[data-builder-diff]').hidden=true;status.textContent='';clearCopyStatus();updateControls(); });
      one('[data-builder-form]').addEventListener('submit',event => {event.preventDefault();preview();});
      one('[data-builder-apply]').addEventListener('click',() => {if(pending && !one('[data-builder-apply]').disabled)command('apply',pending.id);});
      one('[data-builder-undo]').addEventListener('click',() => command('undo'));
      one('[data-builder-inspect]').addEventListener('click',() => {if(applied)command('inspect',applied.id);});
      editor.dataset.ready='true';command('state');
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
