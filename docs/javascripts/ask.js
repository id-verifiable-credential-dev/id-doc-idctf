/* Ask IDCTF drawer.
 *
 * Opens from the header button, posts the question and the last turns to
 * the endpoint on the drawer's data attribute, and renders the answer as
 * text. Nothing from the model reaches innerHTML: the mini renderer builds
 * nodes for paragraphs, bullets, bold and inline code and escapes the rest.
 * Sources are links to the same origin only. History lives in this object
 * and is gone when the page unloads.
 */
(function () {
  "use strict";

  var MAX_TURNS = 10;
  var TIMEOUT_MS = 50000;

  var COPY = {
    thinking: "Thinking",
    unavailable: "The assistant is not available right now. Try again in a moment.",
    rateLimited: "Too many questions in a short time. Wait a few minutes and try again.",
    tooLong: "That question is too long. Keep it under 1,000 characters.",
    forbidden: "This page cannot reach the assistant.",
    sources: "Sources"
  };

  function init() {
    var drawer = document.querySelector("[data-ask]");
    var openBtn = document.querySelector("[data-ask-open]");
    var backdrop = document.querySelector("[data-ask-backdrop]");
    if (!drawer || !openBtn || !backdrop) { return; }

    var endpoint = drawer.getAttribute("data-ask-endpoint") || "/api/chat";
    var log = drawer.querySelector("[data-ask-log]");
    var empty = drawer.querySelector("[data-ask-empty]");
    var form = drawer.querySelector("[data-ask-form]");
    var input = drawer.querySelector("[data-ask-input]");
    var send = drawer.querySelector("[data-ask-send]");
    var closeBtn = drawer.querySelector("[data-ask-close]");
    var history = [];
    var busy = false;
    var lastFocus = null;
    // Each of these sits beside the drawer in the document (the drawer is
    // included at the end of the `footer` block, so it is a sibling of
    // `.md-footer`, not a descendant of any of them). Never add `.md-container`
    // here: it is an ancestor of the drawer itself, and inerting an ancestor
    // of the drawer inerts the drawer too.
    var inertTargets = Array.prototype.slice.call(document.querySelectorAll(".md-header, .md-tabs, .md-main, .md-footer"));

    openBtn.hidden = false;
    openBtn.setAttribute("aria-expanded", "false");

    function open() {
      lastFocus = document.activeElement;
      drawer.hidden = false;
      backdrop.hidden = false;
      document.documentElement.classList.add("ekdn-ask-open");
      document.body.classList.add("ekdn-ask-open");
      inertTargets.forEach(function (t) {
        if (t.contains(drawer)) { return; }
        t.setAttribute("inert", "");
      });
      openBtn.setAttribute("aria-expanded", "true");
      input.focus();
    }

    function close() {
      drawer.hidden = true;
      backdrop.hidden = true;
      document.documentElement.classList.remove("ekdn-ask-open");
      document.body.classList.remove("ekdn-ask-open");
      inertTargets.forEach(function (t) {
        t.removeAttribute("inert");
      });
      openBtn.setAttribute("aria-expanded", "false");
      if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
    }

    openBtn.addEventListener("click", open);
    closeBtn.addEventListener("click", close);
    backdrop.addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !drawer.hidden) { close(); }
    });

    function el(tag, className, text) {
      var node = document.createElement(tag);
      if (className) { node.className = className; }
      if (text !== undefined) { node.textContent = text; }
      return node;
    }

    function renderInline(text, parent) {
      var re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
      var last = 0;
      var m;
      while ((m = re.exec(text)) !== null) {
        if (m.index > last) { parent.appendChild(document.createTextNode(text.slice(last, m.index))); }
        var tok = m[0];
        if (tok.charAt(0) === "*") {
          parent.appendChild(el("strong", null, tok.slice(2, -2)));
        } else {
          parent.appendChild(el("code", null, tok.slice(1, -1)));
        }
        last = m.index + tok.length;
      }
      if (last < text.length) { parent.appendChild(document.createTextNode(text.slice(last))); }
    }

    var BULLET_RE = /^\s*[-*]\s+/;
    var ORDERED_RE = /^\s*\d+[.)]\s+/;

    function renderList(lines, parent, tag, re) {
      var list = el(tag);
      lines.forEach(function (l) {
        if (l.trim() === "") { return; }
        var li = el("li");
        renderInline(l.replace(re, ""), li);
        list.appendChild(li);
      });
      parent.appendChild(list);
    }

    function renderAnswer(text, parent) {
      var blocks = text.split(/\n\s*\n/);
      blocks.forEach(function (block) {
        var lines = block.split("\n");
        var hasContent = lines.some(function (l) { return l.trim() !== ""; });
        var isBullet = lines.every(function (l) { return BULLET_RE.test(l) || l.trim() === ""; });
        var isOrdered = lines.every(function (l) { return ORDERED_RE.test(l) || l.trim() === ""; });
        if (isBullet && hasContent) {
          renderList(lines, parent, "ul", BULLET_RE);
        } else if (isOrdered && hasContent) {
          renderList(lines, parent, "ol", ORDERED_RE);
        } else {
          var p = el("p");
          renderInline(block.replace(/\n/g, " "), p);
          parent.appendChild(p);
        }
      });
    }

    function addTurn(role, text) {
      empty.hidden = true;
      var item = el("div", "ekdn-ask__msg ekdn-ask__msg--" + role);
      if (role === "user") {
        item.appendChild(el("p", null, text));
      } else {
        renderAnswer(text, item);
      }
      log.appendChild(item);
      log.scrollTop = log.scrollHeight;
      return item;
    }

    function addSources(item, sources) {
      if (!Array.isArray(sources) || !sources.length) { return; }
      var wrap = el("div", "ekdn-ask__sources");
      wrap.appendChild(el("span", "ekdn-ask__sr", COPY.sources));
      var ul = el("ul");
      sources.forEach(function (s) {
        if (!s || typeof s.url !== "string") { return; }
        var u;
        try { u = new URL(s.url, location.origin); } catch (e) { return; }
        if (u.origin !== location.origin) { return; }
        var li = el("li");
        var a = el("a", null, s.title || s.url);
        a.href = u.pathname + u.search + u.hash;
        li.appendChild(a);
        ul.appendChild(li);
      });
      if (ul.childNodes.length) {
        wrap.appendChild(ul);
        item.appendChild(wrap);
      }
    }

    function addNote(text) {
      var item = el("div", "ekdn-ask__msg ekdn-ask__msg--note");
      item.appendChild(el("p", null, text));
      log.appendChild(item);
      log.scrollTop = log.scrollHeight;
      return item;
    }

    function errorCopy(status) {
      if (status === 429) { return COPY.rateLimited; }
      if (status === 400 || status === 413) { return COPY.tooLong; }
      if (status === 403) { return COPY.forbidden; }
      return COPY.unavailable;
    }

    function setBusy(state) {
      busy = state;
      send.disabled = state;
      input.disabled = state;
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var question = input.value.trim();
      if (!question || busy) { return; }
      input.value = "";
      addTurn("user", question);
      var pending = addNote(COPY.thinking);
      pending.classList.add("ekdn-ask__msg--thinking");
      setBusy(true);

      var controller = window.AbortController ? new AbortController() : null;
      var timer = controller ? setTimeout(function () { controller.abort(); }, TIMEOUT_MS) : null;

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, history: history.slice(-MAX_TURNS) }),
        signal: controller ? controller.signal : undefined
      }).then(function (resp) {
        if (!resp.ok) { throw Object.assign(new Error("ask"), { status: resp.status }); }
        return resp.json();
      }).then(function (data) {
        pending.remove();
        if (typeof data.answer !== "string") { throw Object.assign(new Error("ask"), { status: 503 }); }
        var item = addTurn("model", data.answer);
        addSources(item, data.sources);
        if (data.declined !== true) {
          history.push({ role: "user", text: question });
          history.push({ role: "model", text: data.answer.slice(0, 2000) });
          if (history.length > MAX_TURNS) { history = history.slice(-MAX_TURNS); }
        }
      }).catch(function (err) {
        pending.remove();
        addNote(errorCopy(err && err.status));
      }).then(function () {
        if (timer) { clearTimeout(timer); }
        setBusy(false);
        input.focus();
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
