/* ==========================================================================
   Dynatrace AI + MCP Workshop — interactive checkpoint lists
   Save as: docs/assets/js/workshop.js

   Then add this line to docs/_layouts/default.html, immediately before
   the closing </body> tag:

     <script src="{{ '/assets/js/workshop.js' | relative_url }}"></script>

   What it does:
     - turns every bullet inside a .lab-checkpoint into a clickable item
     - keeps the state in localStorage, per page, so a refresh or a return
       visit does not wipe someone's progress
     - shows a small "n of m complete" line above the buttons
     - keyboard accessible: Tab to focus, Space or Enter to toggle

   It is entirely progressive. With JavaScript disabled the list still
   renders as a static checklist with empty boxes.
   ========================================================================== */

(function () {
  'use strict';

  function init() {
    var cards = document.querySelectorAll('.lab-checkpoint');
    if (!cards.length) return;

    // Scope saved state to the page, so each lab keeps its own progress.
    var pageKey = 'ws-checklist:' + window.location.pathname;

    Array.prototype.forEach.call(cards, function (card, cardIndex) {
      var list = card.querySelector('ul');
      if (!list) return;

      var items = list.querySelectorAll(':scope > li');
      if (!items.length) return;

      var storageKey = pageKey + ':' + cardIndex;
      var saved = read(storageKey);

      // --- progress line, inserted just above the button row ---------------
      var progress = document.createElement('p');
      progress.className = 'checkpoint-progress';
      var actions = card.querySelector('.checkpoint-actions');
      if (actions) {
        card.insertBefore(progress, actions);
      } else {
        card.appendChild(progress);
      }

      function update() {
        var done = list.querySelectorAll('li.is-done').length;
        var total = items.length;
        progress.textContent = done + ' of ' + total + ' complete';
        progress.classList.toggle('is-complete', done === total);
        if (done === total) {
          progress.textContent = 'All ' + total + ' checks complete';
        }
      }

      function persist() {
        var state = [];
        Array.prototype.forEach.call(items, function (li, i) {
          if (li.classList.contains('is-done')) state.push(i);
        });
        write(storageKey, state);
      }

      Array.prototype.forEach.call(items, function (li, i) {
        li.classList.add('ws-task');
        li.setAttribute('role', 'checkbox');
        li.setAttribute('tabindex', '0');

        if (saved.indexOf(i) !== -1) li.classList.add('is-done');
        li.setAttribute('aria-checked', li.classList.contains('is-done'));

        function toggle() {
          li.classList.toggle('is-done');
          li.setAttribute('aria-checked', li.classList.contains('is-done'));
          persist();
          update();
        }

        li.addEventListener('click', function (event) {
          // Let links and code-copy buttons inside an item behave normally.
          if (event.target.closest('a, button')) return;
          toggle();
        });

        li.addEventListener('keydown', function (event) {
          if (event.key === ' ' || event.key === 'Enter') {
            event.preventDefault();
            toggle();
          }
        });
      });

      update();
    });
  }

  function read(key) {
    try {
      var raw = window.localStorage.getItem(key);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  function write(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      /* Private browsing or a full quota — progress just will not persist. */
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
