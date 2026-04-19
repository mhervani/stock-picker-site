async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Kunne ikke laste ${path}`);
  }
  return response.json();
}

function formatPercent(value) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function getReturnClass(value) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}

async function initHistory() {
  const history = await loadJson("data/monthly_history.json");
  const list = document.getElementById("history-list");

  if (!history.length) {
    list.innerHTML = "<p>Ingen historikk ennå.</p>";
    return;
  }

  list.innerHTML = "";

  history.forEach((month) => {
    const item = document.createElement("article");
    item.className = "history-card";

    item.innerHTML = `
      <h3>${month.label}</h3>
      <p class="muted">Kjøpt: ${month.buy_date} · Avsluttet: ${month.end_date}</p>
      <p><strong>Portefølje:</strong> <span class="${getReturnClass(month.portfolio_return_pct)}">${formatPercent(month.portfolio_return_pct)}</span></p>
      <p><strong>S&P 500:</strong> <span class="${getReturnClass(month.sp500_return_pct)}">${formatPercent(month.sp500_return_pct)}</span></p>
      <p><strong>DNB Global Indeks:</strong> <span class="${getReturnClass(month.dnb_global_indeks_return_pct)}">${formatPercent(month.dnb_global_indeks_return_pct)}</span></p>
      <p><strong>Alpha vs S&P 500:</strong> <span class="${getReturnClass(month.alpha_vs_sp500)}">${formatPercent(month.alpha_vs_sp500)}</span></p>
      <p><strong>Alpha vs DNB:</strong> <span class="${getReturnClass(month.alpha_vs_dnb)}">${formatPercent(month.alpha_vs_dnb)}</span></p>
    `;

    list.appendChild(item);
  });
}

initHistory().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av historikk.</p>`;
});