(function () {
  // Clique em horário vazio da agenda
  const PX_POR_MINUTO = 1.2;
  document.querySelectorAll('.coluna').forEach(function (coluna) {
    coluna.addEventListener('click', function (evento) {
      if (evento.target.closest('.bloco')) return;
      const y = evento.clientY - coluna.getBoundingClientRect().top;
      const [h0] = coluna.dataset.inicio.split(':').map(Number);
      const minutos = Math.floor(y / PX_POR_MINUTO / 15) * 15 + h0 * 60;
      const hora = String(Math.floor(minutos / 60)).padStart(2, '0') + ':' + String(minutos % 60).padStart(2, '0');
      const params = new URLSearchParams({ data: coluna.dataset.data, hora: hora, profissional_id: coluna.dataset.profissional });
      window.location.href = coluna.dataset.novo + '?' + params.toString();
    });
  });

  // Datas dd/mm/aaaa e hora 24h
  if (window.flatpickr) {
    if (flatpickr.l10ns && flatpickr.l10ns.pt) flatpickr.localize(flatpickr.l10ns.pt);
    document.querySelectorAll('input[type="date"]').forEach(function (campo) {
      flatpickr(campo, {
        dateFormat: 'Y-m-d', altInput: true, altFormat: 'd/m/Y', allowInput: true, disableMobile: true,
        onChange: function () {
          campo.dispatchEvent(new Event('change'));
          if (campo.hasAttribute('data-enviar')) campo.form.submit();
        }
      });
    });
    const campoHora = document.getElementById('hora');
    if (campoHora) {
      flatpickr(campoHora, {
        enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true,
        minuteIncrement: 5, allowInput: true, disableMobile: true,
        onChange: function () { campoHora.dispatchEvent(new Event('input')); }
      });
    }
  } else {
    document.querySelectorAll('input[data-enviar]').forEach(function (campo) {
      campo.addEventListener('change', function () { campo.form.submit(); });
    });
  }

  // Previsão de término
  const servico = document.getElementById('servico_id');
  const hora = document.getElementById('hora');
  const previsao = document.getElementById('previsao');
  function atualizarPrevisao() {
    const opcao = servico.options[servico.selectedIndex];
    const duracao = opcao ? Number(opcao.dataset.duracao) : 0;
    if (!duracao || !hora.value) { previsao.textContent = ''; return; }
    const [h, m] = hora.value.split(':').map(Number);
    const fim = h * 60 + m + duracao;
    previsao.textContent = 'Termina às ' + String(Math.floor(fim / 60) % 24).padStart(2, '0') + ':' + String(fim % 60).padStart(2, '0') + '.';
  }
  if (servico && hora && previsao) {
    servico.addEventListener('change', atualizarPrevisao);
    hora.addEventListener('input', atualizarPrevisao);
    atualizarPrevisao();
  }

  // Confirmação
  document.querySelectorAll('form[data-confirmar]').forEach(function (form) {
    form.addEventListener('submit', function (evento) {
      if (!window.confirm(form.dataset.confirmar)) evento.preventDefault();
    });
  });
})();
