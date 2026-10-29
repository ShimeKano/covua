(() => {
  'use strict';
  const logs = [];
  const panel = () => document.getElementById('diagnostics');
  function report(kind, message, detail = '') {
    const line = '[' + new Date().toISOString() + '] ' + kind + ': ' + message + (detail ? '\\n' + detail : '');
    logs.push(line);
    const root = panel();
    if (root) {
      root.hidden = false;
      const summary = document.getElementById('diagnostics-summary');
      const log = document.getElementById('diagnostics-log');
      if (summary) summary.textContent = message;
      if (log) log.textContent = logs.join('\\n\\n');
    }
    console.error('[COVUA diagnostics]', kind, message, detail);
  }
  window.addEventListener('error', event => {
    const target = event.target;
    if (target && target !== window) {
      report('RESOURCE_ERROR', 'Không tải được tài nguyên: ' + (target.src || target.href || target.tagName), 'Kiểm tra URL, mạng/CDN và tab Network trong DevTools.');
      return;
    }
    report('JAVASCRIPT_ERROR', event.message || 'Lỗi JavaScript không xác định', (event.filename || '') + ':' + (event.lineno || '') + ':' + (event.colno || '') + (event.error && event.error.stack ? '\\n' + event.error.stack : ''));
  }, true);
  window.addEventListener('unhandledrejection', event => {
    const reason = event.reason;
    report('UNHANDLED_PROMISE', reason && (reason.stack || reason.message) || String(reason));
  });
  window.addEventListener('DOMContentLoaded', () => {
    const checks = [
      ['Chess rules library', typeof window.Chess === 'function'],
      ['Chess board element', !!document.getElementById('board')],
      ['Main script tag', !!document.querySelector('script[src="./app.js"]')],
      ['Stylesheet', !!document.querySelector('link[href="./style.css"]')]
    ];
    const failed = checks.filter(x => !x[1]);
    checks.forEach(x => console.info('[COVUA diagnostics]', x[1] ? 'PASS' : 'FAIL', x[0]));
    if (failed.length) report('STARTUP_CHECK_FAILED', 'Một số thành phần bắt buộc không sẵn sàng: ' + failed.map(x => x[0]).join(', '), 'Thử tải lại trang; nếu chess.js lỗi, kiểm tra CDN hoặc kết nối mạng.');
    else console.info('[COVUA diagnostics] Startup checks passed.');
    const copy = document.getElementById('diagnostics-copy');
    if (copy) copy.addEventListener('click', async () => {
      const content = logs.join('\\n\\n') || 'Không ghi nhận lỗi runtime. URL: ' + location.href + ' | User agent: ' + navigator.userAgent;
      try { await navigator.clipboard.writeText(content); copy.textContent = 'Đã sao chép log'; }
      catch { const log = document.getElementById('diagnostics-log'); if (log) { log.textContent = content; log.parentElement.open = true; } }
    });
  });
  window.COVUA_DIAGNOSTICS = { report };
})();