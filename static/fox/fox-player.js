/* fox-player.js — lecteur de séquences de sprites foxbot (frames webp RGBA).
 *
 * Usage décoratif (footer) :
 *   <img class="mascot" data-fox="salue" alt="" aria-hidden="true">
 *
 * Usage overlay vidéo (parle pendant la lecture, respire en pause) :
 *   <img class="fox-overlay" data-fox-overlay data-video="#tuto" alt="" aria-hidden="true">
 *
 * Le script charge les frames à la demande et boucle à 12 ips.
 */
(function () {
  'use strict';
  var BASE = '/fox/';
  var FPS = 12;
  var COUNTS = { salue: 33, respire: 49, parle: 49 };

  function frameUrl(action, i) {
    var n = (i < 10 ? '0' : '') + i;
    return BASE + action + '/f_' + n + '.webp';
  }

  function Fox(img) {
    this.img = img;
    this.action = null;
    this.frames = [];
    this.idx = 0;
    this.timer = null;
    var self = this;
    this._tick = function () {
      if (!self.frames.length) return;
      self.img.src = self.frames[self.idx].src;
      self.idx = (self.idx + 1) % self.frames.length;
    };
  }

  Fox.prototype.setAction = function (action) {
    if (this.action === action || !COUNTS[action]) return;
    this.action = action;
    this.idx = 0;
    var frames = [];
    for (var i = 0; i < COUNTS[action]; i++) {
      var im = new Image();
      im.src = frameUrl(action, i);
      frames.push(im);
    }
    this.frames = frames;
    if (!this.timer) {
      this.timer = setInterval(this._tick, 1000 / FPS);
    }
  };

  function init() {
    var players = [];
    document.querySelectorAll('[data-fox]').forEach(function (el) {
      var fx = new Fox(el);
      fx.setAction(el.getAttribute('data-fox'));
      players.push(fx);
    });
    document.querySelectorAll('[data-fox-overlay]').forEach(function (el) {
      var fx = new Fox(el);
      fx.setAction('respire');
      var sel = el.getAttribute('data-video') || 'video';
      var vid = document.querySelector(sel);
      if (vid) {
        vid.addEventListener('play', function () { fx.setAction('parle'); });
        vid.addEventListener('pause', function () { fx.setAction('respire'); });
        vid.addEventListener('ended', function () { fx.setAction('respire'); });
      }
      players.push(fx);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
