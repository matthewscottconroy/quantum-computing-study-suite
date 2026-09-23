/* Quantum Study web deck — offline drill runner.
 *
 * Reads the deck from the inlined JSON block (id="deck-data"), keeps per-card
 * Leitner scheduling in localStorage, and never touches the network.  No build
 * step, no framework: one IIFE, plain DOM.
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ data
  var DECK = JSON.parse(document.getElementById('deck-data').textContent);
  var CARDS = DECK.cards;
  var META = DECK.meta;
  var BY_ID = {};
  CARDS.forEach(function (c) { BY_ID[c.id] = c; });

  var STORE_KEY = 'quantum-study-webdeck-v1';
  // Leitner box -> days until the card comes back.  Box 0 is "today".
  var INTERVALS = [0, 1, 2, 4, 8, 16, 32, 64, 128];
  var AGAIN_GAP = 5;            // cards to wait before a lapsed card returns
  var DAY_MS = 86400000;

  // ------------------------------------------------------------- utilities
  function $(id) { return document.getElementById(id); }

  function today() {
    var d = new Date();
    return Math.floor((d.getTime() - d.getTimezoneOffset() * 60000) / DAY_MS);
  }

  function dayKey(n) { return new Date(n * DAY_MS).toISOString().slice(0, 10); }

  function shuffleInPlace(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  // ------------------------------------------------------- persisted state
  function blankState() {
    return {
      v: 1,
      cards: {},                                  // id -> {b,d,r,l,t}
      cats: META.categories.map(function (c) { return c.name; }),
      shuffle: true,
      stats: { reviews: 0, days: {} }             // days: "YYYY-MM-DD" -> count
    };
  }

  function loadState() {
    var raw = null;
    try { raw = window.localStorage.getItem(STORE_KEY); } catch (e) { raw = null; }
    if (!raw) return blankState();
    var parsed;
    try { parsed = JSON.parse(raw); } catch (e) { return blankState(); }
    if (!parsed || typeof parsed !== 'object') return blankState();
    var s = blankState();
    if (parsed.cards && typeof parsed.cards === 'object') {
      Object.keys(parsed.cards).forEach(function (id) {
        if (!BY_ID[id]) return;                   // card retired from the deck
        var p = parsed.cards[id];
        if (!p || typeof p !== 'object') return;
        s.cards[id] = {
          b: Math.max(0, Math.min(INTERVALS.length - 1, p.b | 0)),
          d: p.d | 0,
          r: Math.max(0, p.r | 0),
          l: Math.max(0, p.l | 0),
          t: p.t | 0
        };
      });
    }
    if (Array.isArray(parsed.cats)) {
      var known = {};
      META.categories.forEach(function (c) { known[c.name] = true; });
      var keep = parsed.cats.filter(function (n) { return known[n]; });
      if (keep.length) s.cats = keep;
    }
    if (typeof parsed.shuffle === 'boolean') s.shuffle = parsed.shuffle;
    if (parsed.stats && typeof parsed.stats === 'object') {
      s.stats.reviews = Math.max(0, parsed.stats.reviews | 0);
      if (parsed.stats.days && typeof parsed.stats.days === 'object') {
        Object.keys(parsed.stats.days).forEach(function (k) {
          if (/^\d{4}-\d{2}-\d{2}$/.test(k)) s.stats.days[k] = parsed.stats.days[k] | 0;
        });
      }
    }
    return s;
  }

  function save() {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify(state));
    } catch (e) {
      if (!storageWarned) {
        storageWarned = true;
        toast('This browser refused to save progress (private mode?)');
      }
    }
  }

  var state = loadState();
  var storageWarned = false;

  // --------------------------------------------------------- session state
  var queue = [];        // cards still to see this session
  var idx = 0;           // pointer into queue
  var revealed = false;
  var undoStack = [];
  var shownId = null;
  var session = { again: 0, good: 0, easy: 0 };

  function selected() {
    var set = {};
    state.cats.forEach(function (n) { set[n] = true; });
    return set;
  }

  function poolCards() {
    var sel = selected();
    return CARDS.filter(function (c) { return sel[c.category]; });
  }

  function buildQueue(preserveSession) {
    var t = today();
    var due = [], fresh = [];
    poolCards().forEach(function (c) {
      var p = state.cards[c.id];
      if (!p) fresh.push(c);
      else if (p.d <= t) due.push(c);
    });
    due.sort(function (a, b) {
      var pa = state.cards[a.id], pb = state.cards[b.id];
      return (pa.d - pb.d) || (pa.b - pb.b) || (a.id < b.id ? -1 : 1);
    });
    if (state.shuffle) { shuffleInPlace(due); shuffleInPlace(fresh); }
    queue = due.concat(fresh);
    idx = 0;
    revealed = false;
    undoStack = [];
    if (!preserveSession) session = { again: 0, good: 0, easy: 0 };
    render();
  }

  // ------------------------------------------------------------- scheduling
  function bumpDay() {
    var k = dayKey(today());
    state.stats.days[k] = (state.stats.days[k] | 0) + 1;
    var keys = Object.keys(state.stats.days).sort();
    while (keys.length > 400) { delete state.stats.days[keys.shift()]; }
  }

  function streak() {
    var n = 0, d = today();
    if (!state.stats.days[dayKey(d)]) d -= 1;     // today not started yet is fine
    while (state.stats.days[dayKey(d)]) { n++; d -= 1; }
    return n;
  }

  function rate(kind) {
    if (!revealed || idx < 0 || idx >= queue.length) return;
    var card = queue[idx];
    var t = today();
    var before = state.cards[card.id] ? JSON.parse(JSON.stringify(state.cards[card.id])) : null;
    undoStack.push({ id: card.id, before: before, at: idx, kind: kind });
    if (undoStack.length > 50) undoStack.shift();

    var p = state.cards[card.id] || { b: 0, d: t, r: 0, l: 0, t: t };
    if (kind === 'again') {
      p.b = 0; p.l += 1; p.d = t;
    } else {
      p.b = Math.min(p.b + (kind === 'easy' ? 2 : 1), INTERVALS.length - 1);
      p.d = t + INTERVALS[p.b];
    }
    p.r += 1;
    p.t = t;
    state.cards[card.id] = p;
    state.stats.reviews += 1;
    session[kind] += 1;
    bumpDay();
    save();

    queue.splice(idx, 1);
    if (kind === 'again') queue.splice(Math.min(idx + AGAIN_GAP, queue.length), 0, card);
    if (idx >= queue.length) idx = 0;
    revealed = false;
    render();
  }

  function undo() {
    var last = undoStack.pop();
    if (!last) { toast('Nothing to undo'); return; }
    var card = BY_ID[last.id];
    for (var i = 0; i < queue.length; i++) {
      if (queue[i].id === last.id) { queue.splice(i, 1); break; }
    }
    if (last.before) state.cards[last.id] = last.before;
    else delete state.cards[last.id];
    state.stats.reviews = Math.max(0, state.stats.reviews - 1);
    var k = dayKey(today());
    if (state.stats.days[k]) state.stats.days[k] = Math.max(0, state.stats.days[k] - 1);
    if (!state.stats.days[k]) delete state.stats.days[k];
    session[last.kind] = Math.max(0, session[last.kind] - 1);
    save();
    idx = Math.min(last.at, queue.length);
    queue.splice(idx, 0, card);
    revealed = true;
    render();
    toast('Undid “' + last.kind + '”');
  }

  // ----------------------------------------------------------------- render
  function counts() {
    var t = today(), due = 0, fresh = 0, learned = 0, pool = poolCards();
    pool.forEach(function (c) {
      var p = state.cards[c.id];
      if (!p) fresh += 1;
      else {
        if (p.r > 0) learned += 1;
        if (p.d <= t) due += 1;
      }
    });
    return { due: due, fresh: fresh, learned: learned, total: pool.length };
  }

  function render() {
    var c = counts();
    var reviewed = session.again + session.good + session.easy;
    var left = queue.length;

    $('deck-sub').textContent = state.cats.length === META.categories.length
      ? plural(META.total, 'card', 'cards')
      : plural(c.total, 'card', 'cards') + ' in ' + plural(state.cats.length, 'category', 'categories');

    $('counters').innerHTML = '';
    addChip('due', 'due', c.due);
    addChip('fresh', 'new', c.fresh);
    addChip('', 'left', left);
    addChip('', 'done', reviewed);

    var denom = reviewed + left;
    $('progress-bar').style.width = (denom ? (reviewed / denom) * 100 : 0) + '%';

    var noCats = state.cats.length === 0;
    var empty = !noCats && left === 0;
    $('card-view').hidden = noCats || empty;
    $('done-view').hidden = !empty;
    $('empty-view').hidden = !noCats;
    $('act-reveal').hidden = noCats || empty || revealed;
    $('act-rate').hidden = noCats || empty || !revealed;

    if (noCats || empty) {
      if (empty) {
        $('done-again').textContent = session.again;
        $('done-good').textContent = session.good;
        $('done-easy').textContent = session.easy;
        $('done-line').textContent = reviewed
          ? plural(reviewed, 'review', 'reviews') + ' this session · ' + plural(streak(), 'day', 'days') + ' streak'
          : 'Nothing is due right now. Come back later, or pick more categories.';
        $('done-next').textContent = nextDueLine();
      }
      return;
    }

    var card = queue[idx];
    var colour = META.colors[card.category] || 'var(--accent)';
    var chip = $('card-cat');
    chip.textContent = card.category;
    chip.style.background = colour;
    $('card-front').textContent = card.front;
    $('card-back').textContent = card.back;
    $('card-id').textContent = card.id;
    $('card-reveal').hidden = !revealed;
    $('card-hint').hidden = revealed;
    $('card').setAttribute('aria-expanded', revealed ? 'true' : 'false');
    if (card.id !== shownId) {           // only jump to the top on a new card
      shownId = card.id;
      $('stage').scrollTop = 0;
    }
  }

  function nextDueLine() {
    var t = today(), soonest = null;
    poolCards().forEach(function (card) {
      var p = state.cards[card.id];
      if (p && p.d > t && (soonest === null || p.d < soonest)) soonest = p.d;
    });
    if (soonest === null) return '';
    var days = soonest - t;
    return 'Next card is due in ' + (days === 1 ? 'a day' : plural(days, 'day', 'days')) + '.';
  }

  function addChip(cls, label, n) {
    var el = document.createElement('span');
    el.className = 'chip' + (cls ? ' ' + cls : '');
    var b = document.createElement('b');
    b.textContent = n;
    el.appendChild(b);
    el.appendChild(document.createTextNode(label));
    $('counters').appendChild(el);
  }

  // ------------------------------------------------------------------ chrome
  var toastTimer = null;
  function toast(msg) {
    var el = $('toast');
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.hidden = true; }, 1800);
  }

  function openSheet(which) {
    $('sheet-filters').hidden = which !== 'filters';
    $('sheet-help').hidden = which !== 'help';
    $('scrim').hidden = !which;
    if (which === 'filters') renderFilters();
  }

  function renderFilters() {
    var sel = selected(), t = today();
    var list = $('cat-list');
    list.innerHTML = '';
    META.categories.forEach(function (cat) {
      var due = 0, fresh = 0;
      CARDS.forEach(function (c) {
        if (c.category !== cat.name) return;
        var p = state.cards[c.id];
        if (!p) fresh += 1;
        else if (p.d <= t) due += 1;
      });
      var row = document.createElement('label');
      row.className = 'cat-row';
      var box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = !!sel[cat.name];
      box.addEventListener('change', function () {
        state.cats = box.checked
          ? state.cats.concat([cat.name])
          : state.cats.filter(function (n) { return n !== cat.name; });
        save();
        buildQueue();
        renderFilters();
      });
      var dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.background = META.colors[cat.name] || 'var(--accent)';
      var name = document.createElement('span');
      name.className = 'name';
      name.textContent = cat.name;
      var n = document.createElement('span');
      n.className = 'n';
      n.textContent = due + ' due · ' + fresh + ' new · ' + cat.count;
      row.appendChild(box); row.appendChild(dot); row.appendChild(name); row.appendChild(n);
      list.appendChild(row);
    });
    $('opt-shuffle').checked = state.shuffle;
    var c = counts();
    $('filter-summary').textContent =
      c.learned + ' of ' + c.total + ' seen · ' + state.stats.reviews + ' reviews all-time · '
      + plural(streak(), 'day', 'days') + ' streak';
  }

  function setAll(on) {
    state.cats = on ? META.categories.map(function (c) { return c.name; }) : [];
    save();
    buildQueue();
    renderFilters();
  }

  function resetProgress() {
    if (!window.confirm('Erase all web-deck progress on this device? The desktop app is unaffected.')) return;
    state.cards = {};
    state.stats = { reviews: 0, days: {} };
    save();
    buildQueue();
    renderFilters();
    toast('Progress reset');
  }

  // ------------------------------------------------------------------ wiring
  function reveal() {
    if (revealed || $('card-view').hidden) return;
    revealed = true;
    render();
  }

  $('card').addEventListener('click', reveal);
  $('act-reveal').addEventListener('click', reveal);
  Array.prototype.forEach.call(document.querySelectorAll('[data-rate]'), function (b) {
    b.addEventListener('click', function () { rate(b.getAttribute('data-rate')); });
  });
  $('btn-filters').addEventListener('click', function () { openSheet('filters'); });
  $('btn-help').addEventListener('click', function () { openSheet('help'); });
  $('scrim').addEventListener('click', function () { openSheet(null); });
  Array.prototype.forEach.call(document.querySelectorAll('[data-close]'), function (b) {
    b.addEventListener('click', function () { openSheet(null); });
  });
  $('btn-all').addEventListener('click', function () { setAll(true); });
  $('btn-none').addEventListener('click', function () { setAll(false); });
  $('btn-reset').addEventListener('click', resetProgress);
  $('opt-shuffle').addEventListener('change', function () {
    state.shuffle = $('opt-shuffle').checked;
    save();
    buildQueue(true);
  });
  $('btn-restart').addEventListener('click', function () { buildQueue(); });
  $('btn-shuffle-now').addEventListener('click', function () {
    var rest = queue.slice(idx);
    shuffleInPlace(rest);
    queue = queue.slice(0, idx).concat(rest);
    revealed = false;
    render();
    toast('Shuffled');
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var tag = (ev.target && ev.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    var sheetOpen = !$('scrim').hidden;
    if (ev.key === 'Escape') { if (sheetOpen) { openSheet(null); ev.preventDefault(); } return; }
    if (sheetOpen) return;
    switch (ev.key) {
      case ' ':
      case 'Enter':
        ev.preventDefault();
        if (revealed) rate('good'); else reveal();
        break;
      case '1': ev.preventDefault(); rate('again'); break;
      case '2': ev.preventDefault(); rate('good'); break;
      case '3': ev.preventDefault(); rate('easy'); break;
      case 'u': case 'U': ev.preventDefault(); undo(); break;
      case 's': case 'S': ev.preventDefault(); $('btn-shuffle-now').click(); break;
      case 'f': case 'F': ev.preventDefault(); openSheet('filters'); break;
      case 'r': case 'R': ev.preventDefault(); buildQueue(); toast('New session'); break;
      case '?': ev.preventDefault(); openSheet('help'); break;
      default: break;
    }
  });

  buildQueue();
})();
