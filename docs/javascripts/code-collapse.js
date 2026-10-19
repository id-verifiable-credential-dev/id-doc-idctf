/* Turns every titled code block into a card: a header with the block's title
   on the left and its format (the fence's data-format) on the right, and,
   when the block is longer than ten lines, a footer with a switch that shows
   the rest. Runs once per page; the build never checks it, so a change here
   is looked at in the browser. */
(function () {
  var LIMIT = 10;
  function init() {
    var blocks = document.querySelectorAll('.md-typeset .highlight');
    Array.prototype.forEach.call(blocks, function (wrap) {
      var code = wrap.querySelector('pre > code');
      if (!code || wrap.dataset.ekdnCode) return;
      wrap.dataset.ekdnCode = '1';
      wrap.classList.add('ekdn-code');

      var filename = wrap.querySelector(':scope > .filename');
      var format = wrap.dataset.format;
      if (filename || format) {
        var head = document.createElement('div');
        head.className = 'ekdn-code__head';
        var title = document.createElement('span');
        title.className = 'ekdn-code__title';
        title.textContent = filename ? filename.textContent : '';
        head.appendChild(title);
        if (format) {
          var badge = document.createElement('span');
          badge.className = 'ekdn-code__format';
          badge.textContent = format;
          head.appendChild(badge);
        }
        if (filename) filename.replaceWith(head);
        else wrap.insertBefore(head, wrap.firstChild);
      }

      var lines = code.textContent.replace(/\n$/, '').split('\n').length;
      if (lines <= LIMIT) return;
      wrap.classList.add('ekdn-code--collapsed');

      var foot = document.createElement('div');
      foot.className = 'ekdn-code__foot';
      var count = document.createElement('span');
      count.className = 'ekdn-code__count';
      var sw = document.createElement('button');
      sw.type = 'button';
      sw.className = 'ekdn-code__switch';
      sw.setAttribute('role', 'switch');
      sw.innerHTML = '<span class="ekdn-code__track" aria-hidden="true">' +
        '<span class="ekdn-code__thumb"></span></span>Show all lines';
      function sync() {
        var collapsed = wrap.classList.contains('ekdn-code--collapsed');
        count.textContent = collapsed ? LIMIT + ' of ' + lines + ' lines' : lines + ' lines';
        sw.setAttribute('aria-checked', collapsed ? 'false' : 'true');
      }
      sw.addEventListener('click', function () {
        wrap.classList.toggle('ekdn-code--collapsed');
        sync();
        if (wrap.classList.contains('ekdn-code--collapsed') &&
            wrap.getBoundingClientRect().top < 0) {
          wrap.scrollIntoView({ block: 'start' });
        }
      });
      foot.appendChild(count);
      foot.appendChild(sw);
      wrap.appendChild(foot);
      sync();
    });
  }
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
