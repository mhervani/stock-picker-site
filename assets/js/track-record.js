async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Kunne ikke laste ${path}`);
  }
  return response.json();
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function getReturnClass(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "neutral";
  }
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}

async function initTrackRecord() {
  const trackRecord = await loadJson("data/track_record.json");
  const monthlyHistory = await loadJson("data/monthly_history.json");
  const held = await loadJson("data/held_positions.json");

  document.getElementById("track-record-title").textContent = "Samlet resultat";
  document.getElementById("track-record-subtitle").textContent =
    `Viser ${trackRecord.months_completed || 0} fullførte måneder`;

  document.getElementById("months-completed").textContent =
    trackRecord.months_completed ?? 0;
  document.getElementById("beat-sp500-count").textContent =
    trackRecord.beat_sp500_count ?? 0;
  document.getElementById("beat-dnb-count").textContent =
    trackRecord.beat_dnb_count ?? 0;

  document.getElementById("avg-alpha-sp500").textContent =
    formatPercent(trackRecord.avg_alpha_vs_sp500);
  document.getElementById("avg-alpha-dnb").textContent =
    formatPercent(trackRecord.avg_alpha_vs_dnb);
  document.getElementById("cumulative-return").textContent =
    formatPercent(trackRecord.cumulative_portfolio_return_pct);
  document.getElementById("held-portfolio-count").textContent =
    (held.portfolios || []).length;

  const tableBody = document.getElementById("track-record-table-body");
  tableBody.innerHTML = "";

  for (const item of monthlyHistory) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.label || item.month_id}</td>
      <td>${item.buy_date || "–"}</td>
      <td>${item.end_date || "–"}</td>
      <td class="${getReturnClass(item.portfolio_return_pct)}">${formatPercent(item.portfolio_return_pct)}</td>
      <td class="${getReturnClass(item.sp500_return_pct)}">${formatPercent(item.sp500_return_pct)}</td>
      <td class="${getReturnClass(item.dnb_global_indeks_return_pct)}">${formatPercent(item.dnb_global_indeks_return_pct)}</td>
      <td class="${getReturnClass(item.alpha_vs_sp500)}">${formatPercent(item.alpha_vs_sp500)}</td>
      <td class="${getReturnClass(item.alpha_vs_dnb)}">${formatPercent(item.alpha_vs_dnb)}</td>
    `;
    tableBody.appendChild(tr);
  }

  const heldList = document.getElementById("held-list");
  heldList.innerHTML = "";

  if (!held.portfolios || !held.portfolios.length) {
    heldList.innerHTML = "<p>Ingen videre trackede porteføljer ennå.</p>";
    return;
  }

  for (const portfolio of held.portfolios) {
    const item = document.createElement("article");
    item.className = "history-card";

    item.innerHTML = `
      <div class="history-card-top">
        <div>
          <h3>${portfolio.label}</h3>
          <p class="muted">Kjøpt: ${portfolio.buy_date} · Lukket: ${portfolio.closed_date}</p>
        </div>
        <div><span class="badge badge-tracking">${portfolio.status}</span></div>
      </div>

      <p><strong>Videre avkastning:</strong> <span class="${getReturnClass(portfolio.portfolio_return_pct)}">${formatPercent(portfolio.portfolio_return_pct)}</span></p>
      <p class="muted"><strong>Sist oppdatert:</strong> ${portfolio.updated_at || "–"}</p>

      <div class="sub-block">
        ${(portfolio.positions || [])
          .map(
            (p) => `
              <p><strong>${p.ticker}</strong>: ${formatPercent(p.return_pct)}</p>
            `
          )
          .join("")}
      </div>
    `;

    heldList.appendChild(item);
  }
}

initTrackRecord().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av track record.</p>`;
});