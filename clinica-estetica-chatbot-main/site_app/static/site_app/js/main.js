(function () {
  'use strict';

  // Header: sombra suave ao rolar a página
  var header = document.getElementById('header');
  function aoRolar() {
    header.classList.toggle('is-rolado', window.scrollY > 8);
  }
  aoRolar();
  window.addEventListener('scroll', aoRolar, { passive: true });

  // Menu mobile
  var toggle = document.getElementById('menuToggle');
  var nav = document.getElementById('nav');
  function fecharMenu() {
    nav.classList.remove('is-aberto');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menu');
  }
  toggle.addEventListener('click', function () {
    var aberto = nav.classList.toggle('is-aberto');
    toggle.setAttribute('aria-expanded', String(aberto));
    toggle.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
  });
  nav.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', fecharMenu); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') fecharMenu(); });

  

    // ===== Agendamento: calendário, horários e envio pelo WhatsApp =====
  var cfgEl = document.getElementById('agenda-config');
  var gradeEl = document.getElementById('agGrade');
  if (cfgEl && gradeEl) {
    var cfg = JSON.parse(cfgEl.textContent);
    var mesEl = document.getElementById('agMes');
    var prevEl = document.getElementById('agPrev');
    var nextEl = document.getElementById('agNext');
    var dataEl = document.getElementById('agData');
    var horasEl = document.getElementById('agHoras');
    var maisEl = document.getElementById('agMais');
    var resumoEl = document.getElementById('agResumo');
    var nomeEl = document.getElementById('agNome');
    var telEl = document.getElementById('agTel');
    var tratEl = document.getElementById('agTrat');
    var enviarEl = document.getElementById('agEnviar');

    var POR_PAGINA = 4; // horários visíveis antes de "Mostrar mais horários"
    var SEMANA = ['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.'];
    var pad = function (n) { return String(n).padStart(2, '0'); };
    var rotuloHora = function (min) { return pad(Math.floor(min / 60)) + ':' + pad(min % 60); };
    var maiuscula = function (t) { return t.charAt(0).toUpperCase() + t.slice(1); };

    var agora = new Date();
    var hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    var limite = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate() + cfg.dias_a_frente);
    var MAX_OPCOES = 2; // até 2 opções de horário
    var estado = { data: null, horas: [], mes: new Date(hoje.getFullYear(), hoje.getMonth(), 1), todos: false };

    function dataTexto(d, curto) {
      return d.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: curto ? 'short' : 'long' });
    }

    // Horários de início (minutos desde 00:00) de uma data; vazio = sem atendimento
    function slotsDoDia(d) {
      if (d < hoje || d > limite) return [];
      var faixa = cfg.horarios[String(d.getDay())];
      if (!faixa) return [];
      var passo = cfg.duracao_min, lista = [];
      var ehHoje = d.getTime() === hoje.getTime();
      var minAgora = agora.getHours() * 60 + agora.getMinutes();
      for (var t = faixa[0] * 60; t + passo <= faixa[1] * 60; t += passo) {
        if (!ehHoje || t > minAgora) lista.push(t);
      }
      return lista;
    }

    function atualizarEnvio() {
      var nomeOk = nomeEl.value.trim().length >= 3;
      var telOk = /^\d{10,13}$/.test(telEl.value.replace(/\D/g, ''));
      enviarEl.disabled = !(estado.data && estado.horas.length > 0 && nomeOk && telOk);
    }

    function desenharCalendario() {
      var ano = estado.mes.getFullYear(), mes = estado.mes.getMonth();
      mesEl.textContent = maiuscula(estado.mes.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }));
      prevEl.disabled = estado.mes <= new Date(hoje.getFullYear(), hoje.getMonth(), 1);
      nextEl.disabled = new Date(ano, mes + 1, 1) > limite;

      gradeEl.innerHTML = '';
      SEMANA.forEach(function (s) {
        var h = document.createElement('span');
        h.className = 'cal__sem';
        h.textContent = s;
        gradeEl.appendChild(h);
      });
      var vazios = new Date(ano, mes, 1).getDay();
      for (var v = 0; v < vazios; v++) gradeEl.appendChild(document.createElement('span'));

      var total = new Date(ano, mes + 1, 0).getDate();
      for (var n = 1; n <= total; n++) {
        (function (d) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'cal__dia';
          b.textContent = d.getDate();
          b.disabled = slotsDoDia(d).length === 0;
          b.setAttribute('aria-label', maiuscula(dataTexto(d)));
          b.setAttribute('aria-pressed', String(!!estado.data && d.getTime() === estado.data.getTime()));
          b.addEventListener('click', function () { escolherDia(d); });
          gradeEl.appendChild(b);
        })(new Date(ano, mes, n));
      }
    }

    // Atualiza botões marcados e o texto "1ª opção / 2ª opção"
    function marcarHorarios() {
      var botoes = horasEl.querySelectorAll('.horario');
      Array.prototype.forEach.call(botoes, function (x) {
        x.setAttribute('aria-pressed', String(estado.horas.indexOf(x._t) !== -1));
      });
      var partes = estado.horas.map(function (t, i) { return (i + 1) + 'ª opção: ' + rotuloHora(t); });
      resumoEl.textContent = partes.length
        ? partes.join(' · ')
        : (estado.data ? 'Escolha até ' + MAX_OPCOES + ' opções de horário.' : '');
    }

    function desenharHorarios() {
      horasEl.innerHTML = '';
      if (!estado.data) {
        dataEl.textContent = 'Escolha um dia';
        maisEl.hidden = true;
        resumoEl.textContent = '';
        return;
      }
      dataEl.textContent = dataTexto(estado.data, true);
      var slots = slotsDoDia(estado.data);
      var visiveis = estado.todos ? slots : slots.slice(0, POR_PAGINA);
      visiveis.forEach(function (t) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'horario';
        b._t = t;
        b.textContent = rotuloHora(t) + ' - ' + rotuloHora(t + cfg.duracao_min);
        b.setAttribute('aria-pressed', String(estado.horas.indexOf(t) !== -1));
        b.addEventListener('click', function () {
          var i = estado.horas.indexOf(t);
          if (i !== -1) {
            estado.horas.splice(i, 1);                 // clicar de novo desmarca
          } else if (estado.horas.length < MAX_OPCOES) {
            estado.horas.push(t);
          } else {
            estado.horas[MAX_OPCOES - 1] = t;          // já há 2: troca a 2ª opção
          }
          marcarHorarios();
          atualizarEnvio();
        });
        horasEl.appendChild(b);
      });
      maisEl.hidden = estado.todos || slots.length <= POR_PAGINA;
      marcarHorarios();
    }

    function escolherDia(d) {
      estado.data = d;
      estado.horas = [];
      estado.todos = false;
      desenharCalendario();
      desenharHorarios();
      atualizarEnvio();
    }

    prevEl.addEventListener('click', function () {
      estado.mes = new Date(estado.mes.getFullYear(), estado.mes.getMonth() - 1, 1);
      desenharCalendario();
    });
    nextEl.addEventListener('click', function () {
      estado.mes = new Date(estado.mes.getFullYear(), estado.mes.getMonth() + 1, 1);
      desenharCalendario();
    });
    maisEl.addEventListener('click', function () {
      estado.todos = true;
      desenharHorarios();
    });
    nomeEl.addEventListener('input', atualizarEnvio);
    telEl.addEventListener('input', atualizarEnvio);

    // Botões "Agendar" dos cards: escolhem o tratamento e levam ao formulário
    document.querySelectorAll('[data-servico]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var nome = btn.getAttribute('data-servico');
        var existe = Array.prototype.some.call(tratEl.options, function (o) { return o.value === nome; });
        if (existe) tratEl.value = nome;
        document.getElementById('agendamento').scrollIntoView({ behavior: 'smooth', block: 'start' });
        nomeEl.focus({ preventScroll: true });
      });
    });

    enviarEl.addEventListener('click', function () {
      if (enviarEl.disabled) return;
      var msg = 'Olá, Dra. Silvia! Me chamo ' + nomeEl.value.trim() +
                ' e gostaria de agendar ' + tratEl.value.toLowerCase() +
                ' na ' + maiuscula(dataTexto(estado.data)) + ', às ' + rotuloHora(estado.horas[0]) +
                (estado.horas.length > 1 ? ' (como segunda opção, às ' + rotuloHora(estado.horas[1]) + ')' : '') +
                '. Meu telefone para contato: ' + telEl.value.trim() + '.';
      var url = 'https://wa.me/' + gradeEl.dataset.whatsapp + '?text=' + encodeURIComponent(msg);
      window.open(url, '_blank', 'noopener');
    });

    // Vindo da página de serviços (?servico=Nome): já seleciona o tratamento
    var servicoURL = new URLSearchParams(window.location.search).get('servico');
    if (servicoURL) {
      Array.prototype.forEach.call(tratEl.options, function (o) { if (o.value === servicoURL) tratEl.value = servicoURL; });
    }

    // Já abre no primeiro dia com horário livre
    for (var i = 0; i <= cfg.dias_a_frente; i++) {
      var d0 = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate() + i);
      if (slotsDoDia(d0).length) { estado.data = d0; estado.mes = new Date(d0.getFullYear(), d0.getMonth(), 1); break; }
    }
    desenharCalendario();
    desenharHorarios();
    atualizarEnvio();
  }

  // ===== Página de contato: formulário -> WhatsApp =====
  var formContato = document.getElementById('contatoForm');
  if (formContato) {
    var okEl = document.getElementById('cOk');
    var numero = (document.getElementById('agenda-config') && '') || '';
    formContato.addEventListener('submit', function (e) {
      e.preventDefault();
      var nome = document.getElementById('cNome').value.trim();
      var tel = document.getElementById('cTel').value.trim();
      okEl.hidden = false;
      okEl.classList.remove('contato__ok--erro');
      if (nome.length < 3) {
        okEl.classList.add('contato__ok--erro');
        okEl.textContent = 'Digite seu nome, com pelo menos 3 caracteres.';
        document.getElementById('cNome').focus();
        return;
      }
      if (!/^\d{10,13}$/.test(tel.replace(/\D/g, ''))) {
        okEl.classList.add('contato__ok--erro');
        okEl.textContent = 'Digite um telefone válido com DDD. Exemplo: (11) 99999-9999.';
        document.getElementById('cTel').focus();
        return;
      }
      var extra = document.getElementById('cMsg').value.trim();
      var msg = 'Olá, Dra. Silvia! Sou ' + nome + ' (' + tel + '). Tenho interesse em ' +
                document.getElementById('cTrat').value.toLowerCase() +
                ', de preferência no período: ' + document.getElementById('cPer').value.toLowerCase() + '.' +
                (extra ? ' ' + extra : '');
      var base = formContato.dataset.whatsapp.split('?')[0];
      var url = base + '?text=' + encodeURIComponent(msg);
      window.open(url, '_blank', 'noopener');
      okEl.innerHTML = 'Se o WhatsApp não abriu, <a href="' + url + '" target="_blank" rel="noopener">clique aqui para enviar</a>.';
    });
  }
})();