// Sandbox for running LLM-generated JavaScript (the chat agent's run_js_code tool).
//
// The code may have been steered by prompt injection (text inside fetched
// records), so it must not be able to reach the app's page, the admin token,
// or the network. Layers:
//
// 1. A hidden <iframe sandbox="allow-scripts"> without allow-same-origin gets
//    an opaque origin: no access to the parent DOM, localStorage (token),
//    cookies, or the app's origin. No allow-top-navigation/popups/forms either.
// 2. The iframe's CSP (default-src 'none') blocks fetch/XHR/WebSocket/EventSource,
//    import() and resource loads. Workers created from blob: URLs inherit it.
// 3. The code runs in a Worker inside that iframe, so it can't navigate the
//    frame (a way to leak data in a URL) and an infinite loop can't freeze the
//    page: the worker is terminated after a timeout.
//
// If the Worker can't be created the run fails closed with an error rather
// than running the code anywhere less isolated.

const SANDBOX_CSP = "default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval' blob:; worker-src blob:"

// Runs inside the Worker. Kept as a string so it can be put in a Blob.
const WORKER_SOURCE = `
self.onmessage = function (e) {
  Promise.resolve().then(function () {
    var fn = new Function('data', e.data.code)
    return fn(e.data.data)
  }).then(function (value) {
    var json = JSON.stringify(value === undefined ? null : value)
    self.postMessage({ result: json === undefined ? null : JSON.parse(json) })
  }).catch(function (err) {
    self.postMessage({ error: String((err && err.message) || err) })
  })
}
`

// Runs inside the sandboxed iframe: starts one Worker per run and relays the
// single result back to the parent.
const IFRAME_SOURCE = `<!doctype html>
<html><head>
<meta http-equiv="Content-Security-Policy" content="${SANDBOX_CSP}">
</head><body><script>
(function () {
  var workerUrl = URL.createObjectURL(new Blob([${JSON.stringify(WORKER_SOURCE)}], { type: 'text/javascript' }))
  window.addEventListener('message', function (e) {
    if (e.source !== window.parent) return
    var msg = e.data || {}
    var done = false
    var worker = null
    var timer = null
    function reply (r) {
      if (done) return
      done = true
      clearTimeout(timer)
      if (worker) worker.terminate()
      window.parent.postMessage({ id: msg.id, result: r.result, error: r.error }, '*')
    }
    timer = setTimeout(function () {
      reply({ error: 'Code timed out after ' + msg.timeoutMs + ' ms (possible infinite loop)' })
    }, msg.timeoutMs)
    try {
      worker = new Worker(workerUrl)
    } catch (err) {
      reply({ error: 'Sandbox unavailable in this browser: ' + err.message })
      return
    }
    worker.onmessage = function (ev) { reply(ev.data || {}) }
    worker.onerror = function (ev) {
      if (ev.preventDefault) ev.preventDefault()
      reply({ error: ev.message || 'Error in sandboxed code' })
    }
    worker.postMessage({ code: msg.code, data: msg.data })
  })
  window.parent.postMessage({ ready: true }, '*')
})()
</` + `script></body></html>`

export function createJsSandbox (options) {
  const timeoutMs = (options && options.timeoutMs) || 5000
  let iframe = null
  let readyPromise = null
  let seq = 0
  const pending = new Map()

  function onMessage (e) {
    // Only accept messages from our own iframe.
    if (!iframe || e.source !== iframe.contentWindow) return
    const msg = e.data || {}
    if (msg.ready) {
      if (iframe.__resolveReady) iframe.__resolveReady()
      return
    }
    const entry = pending.get(msg.id)
    if (!entry) return
    pending.delete(msg.id)
    clearTimeout(entry.timer)
    entry.resolve(msg.error !== undefined && msg.error !== null ? { error: msg.error } : { result: msg.result })
  }

  function ensureIframe () {
    if (readyPromise) return readyPromise
    window.addEventListener('message', onMessage)
    iframe = document.createElement('iframe')
    iframe.setAttribute('sandbox', 'allow-scripts')
    iframe.setAttribute('aria-hidden', 'true')
    iframe.setAttribute('tabindex', '-1')
    iframe.style.display = 'none'
    readyPromise = new Promise(function (resolve) { iframe.__resolveReady = resolve })
    iframe.srcdoc = IFRAME_SOURCE
    document.body.appendChild(iframe)
    return readyPromise
  }

  function reset () {
    if (iframe && iframe.parentNode) iframe.parentNode.removeChild(iframe)
    iframe = null
    readyPromise = null
  }

  // Runs `code` (a function body receiving `data`) and resolves to
  // { result } or { error }. Never rejects.
  async function run (code, data) {
    if (typeof code !== 'string' || !code) return { error: 'code must be a non-empty string' }
    let payload
    try {
      // Plain JSON copy: strips Vue reactivity and anything non-serializable.
      payload = JSON.parse(JSON.stringify(data === undefined ? null : data))
    } catch (err) {
      return { error: 'Could not pass data into the sandbox: ' + err.message }
    }
    await ensureIframe()
    const id = ++seq
    return new Promise(function (resolve) {
      // Backstop in case the iframe itself stops responding.
      const timer = setTimeout(function () {
        pending.delete(id)
        reset()
        resolve({ error: 'Sandbox did not respond' })
      }, timeoutMs + 2000)
      pending.set(id, { resolve: resolve, timer: timer })
      iframe.contentWindow.postMessage({ id: id, code: code, data: payload, timeoutMs: timeoutMs }, '*')
    })
  }

  function destroy () {
    window.removeEventListener('message', onMessage)
    pending.forEach(function (entry) {
      clearTimeout(entry.timer)
      entry.resolve({ error: 'Sandbox closed' })
    })
    pending.clear()
    reset()
  }

  return { run: run, destroy: destroy }
}
