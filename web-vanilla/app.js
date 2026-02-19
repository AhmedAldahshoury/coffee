const API_BASE_KEY = 'coffee_console_api_base';
const TOKEN_KEY = 'coffee_console_token';
const REQUEST_LOG_LIMIT = 30;

const state = {
  currentStudy: null,
  lastSuggestion: null,
  logs: [],
};

function getApiBase() {
  const raw = document.getElementById('apiBase').value.trim();
  return raw.replace(/\/$/, '');
}

function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
  renderTokenStatus();
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setOutput(id, payload, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  const text = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
  el.textContent = text;
  el.classList.toggle('error', isError);
  el.classList.toggle('success', !isError);
}

function prettyJson(value) {
  if (value === null || value === undefined) return '(none)';
  if (typeof value === 'string') return value;
  return JSON.stringify(value, null, 2);
}

function safeParseJson(text) {
  try {
    return { ok: true, value: JSON.parse(text) };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'Invalid JSON' };
  }
}

function setLoading(button, label) {
  const oldText = button.textContent;
  button.disabled = true;
  button.textContent = `${label}...`;
  return () => {
    button.disabled = false;
    button.textContent = oldText;
  };
}

function updateLinks() {
  const base = getApiBase();
  document.getElementById('docsLink').href = `${base}/docs`;
}

function renderTokenStatus() {
  const token = getToken();
  const status = token ? `Token: set (${token.slice(0, 16)}...)` : 'Token: none';
  document.getElementById('tokenStatus').textContent = status;
}

function addLog(logEntry) {
  state.logs.unshift(logEntry);
  state.logs = state.logs.slice(0, REQUEST_LOG_LIMIT);
  renderApiLog();
}

function renderApiLog() {
  const container = document.getElementById('apiLog');
  container.innerHTML = '';

  state.logs.forEach((log, idx) => {
    const item = document.createElement('div');
    item.className = 'log-item';

    const header = document.createElement('div');
    header.className = 'log-header';
    header.innerHTML = `
      <strong>${log.method}</strong>
      <span>${log.url}</span>
      <span>${log.status}</span>
      <span>${log.durationMs} ms</span>
    `;

    const details = document.createElement('details');
    if (idx === 0) details.open = true;
    const summary = document.createElement('summary');
    summary.textContent = 'request/response';

    const body = document.createElement('div');
    body.className = 'log-body';
    body.innerHTML = `
      <div><strong>Request Body</strong></div>
      <pre class="json-view">${escapeHtml(prettyJson(log.requestBody))}</pre>
      <div><strong>Response Body</strong></div>
      <pre class="json-view">${escapeHtml(prettyJson(log.responseBody))}</pre>
    `;

    details.append(summary, body);
    item.append(header, details);
    container.appendChild(item);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

async function parseResponseBody(response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }
  try {
    return await response.text();
  } catch {
    return null;
  }
}

async function apiFetch(path, options = {}) {
  const start = performance.now();
  const base = getApiBase();
  const url = `${base}${path}`;
  const method = options.method || 'GET';
  const headers = new Headers(options.headers || {});

  const token = getToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const requestConfig = { ...options, method, headers };
  let requestBodyForLog = null;
  if (options.body !== undefined && !(options.body instanceof FormData) && typeof options.body !== 'string') {
    requestBodyForLog = options.body;
    headers.set('Content-Type', 'application/json');
    requestConfig.body = JSON.stringify(options.body);
  } else {
    requestConfig.body = options.body;
    if (typeof options.body === 'string') requestBodyForLog = options.body;
    if (options.body instanceof FormData) requestBodyForLog = '[FormData]';
  }

  let response = null;
  let responseBody = null;
  let status = 'ERR';
  try {
    response = await fetch(url, requestConfig);
    status = response.status;
    responseBody = await parseResponseBody(response);

    const durationMs = Math.round(performance.now() - start);
    addLog({ method, url, status, durationMs, requestBody: requestBodyForLog, responseBody });

    if (!response.ok) {
      throw new Error(typeof responseBody === 'string' ? responseBody : JSON.stringify(responseBody));
    }

    return { response, data: responseBody };
  } catch (error) {
    const durationMs = Math.round(performance.now() - start);
    addLog({
      method,
      url,
      status,
      durationMs,
      requestBody: requestBodyForLog,
      responseBody: responseBody || (error instanceof Error ? error.message : 'Unknown error'),
    });
    throw error;
  }
}

function parseTextareaJson(id) {
  const raw = document.getElementById(id).value;
  const parsed = safeParseJson(raw);
  if (!parsed.ok) {
    throw new Error(`Invalid JSON in ${id}: ${parsed.error}`);
  }
  return parsed.value;
}

function renderBrewsTable(data) {
  const rows = Array.isArray(data) ? data : data?.items || [];
  const container = document.getElementById('brewsTable');
  if (!rows.length) {
    container.innerHTML = '<p>No brews.</p>';
    return;
  }
  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>id</th><th>method</th><th>score</th><th>brewed_at</th><th>status</th></tr></thead>';
  const tbody = document.createElement('tbody');

  rows.forEach((brew) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${brew.id || ''}</td>
      <td>${brew.method || ''}</td>
      <td>${brew.score ?? ''}</td>
      <td>${brew.brewed_at || ''}</td>
      <td>${brew.status || ''}</td>
    `;
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.innerHTML = '';
  container.appendChild(table);
}

function currentStudyPayload() {
  return {
    method_id: document.getElementById('studyMethod').value.trim(),
    variant_id: document.getElementById('studyVariant').value.trim() || null,
  };
}

function setDefaultBrewedAt() {
  document.getElementById('brewBrewedAt').value = new Date().toISOString();
}

function wireTabs() {
  const tabButtons = document.querySelectorAll('.tab');
  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach((it) => it.classList.remove('active'));
      btn.classList.add('active');

      const name = btn.dataset.tab;
      document.querySelectorAll('main > .panel').forEach((panel) => {
        if (panel.id === 'apiLogPanel') {
          panel.classList.add('active');
          return;
        }
        panel.classList.toggle('active', panel.id === `tab-${name}`);
      });
    });
  });
}

function bindAction(buttonId, outputId, actionName, handler) {
  const btn = document.getElementById(buttonId);
  btn.addEventListener('click', async () => {
    const reset = setLoading(btn, actionName);
    try {
      const data = await handler();
      if (outputId) setOutput(outputId, data, false);
    } catch (error) {
      if (outputId) setOutput(outputId, error instanceof Error ? error.message : String(error), true);
    } finally {
      reset();
    }
  });
}

function init() {
  const apiBaseInput = document.getElementById('apiBase');
  const savedBase = localStorage.getItem(API_BASE_KEY);
  if (savedBase) apiBaseInput.value = savedBase;

  document.getElementById('saveApiBase').addEventListener('click', () => {
    localStorage.setItem(API_BASE_KEY, getApiBase());
    updateLinks();
  });

  apiBaseInput.addEventListener('change', updateLinks);
  updateLinks();
  wireTabs();
  setDefaultBrewedAt();
  renderTokenStatus();

  bindAction('pingBtn', 'pingStatus', 'Ping', async () => {
    const { data } = await apiFetch('/health');
    return `ok ${JSON.stringify(data)}`;
  });

  bindAction('registerBtn', 'registerResult', 'Register', async () => {
    const { data } = await apiFetch('/api/v1/auth/register', {
      method: 'POST',
      body: {
        email: document.getElementById('registerEmail').value.trim(),
        password: document.getElementById('registerPassword').value,
        name: document.getElementById('registerName').value.trim() || null,
      },
    });
    return data;
  });

  bindAction('loginBtn', 'authResult', 'Login', async () => {
    const { data } = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      body: {
        email: document.getElementById('loginEmail').value.trim(),
        password: document.getElementById('loginPassword').value,
      },
    });
    setToken(data.access_token);
    return data;
  });

  bindAction('logoutBtn', 'authResult', 'Logout', async () => {
    setToken(null);
    return { message: 'Token removed from localStorage' };
  });

  bindAction('meBtn', 'authResult', 'Me', async () => {
    const { data } = await apiFetch('/api/v1/auth/me');
    return data;
  });

  bindAction('listBrewsBtn', 'createBrewResult', 'List', async () => {
    const { data } = await apiFetch('/api/v1/brews');
    renderBrewsTable(data);
    return { count: Array.isArray(data) ? data.length : data?.items?.length ?? 0 };
  });

  bindAction('getBrewBtn', 'brewDetailResult', 'Fetch', async () => {
    const brewId = document.getElementById('brewIdInput').value.trim();
    const { data } = await apiFetch(`/api/v1/brews/${brewId}`);
    return data;
  });

  bindAction('createBrewBtn', 'createBrewResult', 'Create', async () => {
    const payload = {
      method: document.getElementById('brewMethod').value.trim(),
      variant_id: document.getElementById('brewVariant').value.trim() || null,
      brewed_at: document.getElementById('brewBrewedAt').value.trim() || new Date().toISOString(),
      score: document.getElementById('brewScore').value ? Number(document.getElementById('brewScore').value) : null,
      status: document.getElementById('brewStatus').value,
      comments: document.getElementById('brewComments').value.trim() || null,
      parameters: parseTextareaJson('brewParams'),
    };
    const { data } = await apiFetch('/api/v1/brews', { method: 'POST', body: payload });
    if (data?.id) document.getElementById('applyBrewId').value = data.id;
    return data;
  });

  bindAction('importBtn', 'importResult', 'Import', async () => {
    const fileInput = document.getElementById('importFile');
    if (!fileInput.files?.length) throw new Error('Select a CSV file first.');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    const method = document.getElementById('importMethod').value.trim();
    if (method) formData.append('method', method);

    const { data } = await apiFetch('/api/v1/import/csv/upload', {
      method: 'POST',
      body: formData,
    });
    return data;
  });

  bindAction('exportBtn', 'exportResult', 'Export', async () => {
    const { response } = await apiFetch('/api/v1/export/csv/download');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'brews.export.csv';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    return { message: 'Downloaded brews.export.csv' };
  });

  bindAction('createStudyBtn', 'studyResult', 'Study', async () => {
    const payload = currentStudyPayload();
    const { data } = await apiFetch('/api/v1/optimisation/studies', { method: 'POST', body: payload });
    state.currentStudy = payload;
    return data;
  });

  bindAction('suggestBtn', 'suggestResult', 'Suggest', async () => {
    const payload = state.currentStudy || currentStudyPayload();
    const { data } = await apiFetch('/api/v1/optimisation/suggest', { method: 'POST', body: payload });
    state.lastSuggestion = data;
    if (data?.id) document.getElementById('applySuggestionId').value = data.id;
    return data;
  });

  bindAction('applyBtn', 'applyResult', 'Apply', async () => {
    const suggestionId = document.getElementById('applySuggestionId').value.trim();
    const brewId = document.getElementById('applyBrewId').value.trim();
    if (!suggestionId || !brewId) throw new Error('Suggestion ID and Brew ID are required.');
    const scoreRaw = document.getElementById('applyScore').value;
    const payload = {
      brew_id: brewId,
      score: scoreRaw ? Number(scoreRaw) : null,
      failed: document.getElementById('applyFailed').checked,
    };
    const { data } = await apiFetch(`/api/v1/optimisation/suggestions/${suggestionId}/apply`, {
      method: 'POST',
      body: payload,
    });
    return data;
  });

  bindAction('healthBtn', 'metaResult', 'Health', async () => {
    const { data } = await apiFetch('/health');
    return data;
  });

  bindAction('openapiBtn', 'metaResult', 'OpenAPI', async () => {
    const { data } = await apiFetch('/openapi.json');
    return { openapi: data?.openapi, title: data?.info?.title, paths: Object.keys(data?.paths || {}).length };
  });
}

document.addEventListener('DOMContentLoaded', init);
