async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Kunne ikke laste ${path}`);
  }
  return response.json();
}

function getMonthIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("month") || "2026-05";
}

function formatConfidence(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  return `${value}/10`;
}

async function initMonthPage() {
  const monthId = getMonthIdFromUrl();
  const month = await loadJson(`data/months/${monthId}.json`);

  document.getElementById("month-page-title").textContent = month.label;
  document.getElementById("month-label").textContent = month.label;
  document.getElementById("month-buy-date").textContent = `Kjøpsdato: ${month.buy_date}`;
  document.getElementById("month-analysis-date").textContent = `Analysedato: ${month.analysis_date}`;

  document.getElementById("portfolio-conclusion").textContent =
    month.market_context.portfolio_conclusion || "–";
  document.getElementById("portfolio-confidence").textContent =
    formatConfidence(month.market_context.portfolio_confidence);
  document.getElementById("portfolio-ranking").textContent =
    (month.portfolio.ranking || []).join(" > ");

  document.getElementById("market-summary").textContent =
    month.market_context.summary || "–";
  document.getElementById("freshness-note").textContent =
    month.market_context.freshness_note || "–";

  document.getElementById("portfolio-case").textContent =
    month.portfolio.why_this_portfolio_can_win || "–";
  document.getElementById("portfolio-risk").textContent =
    month.portfolio.biggest_portfolio_risk || "–";

  const grid = document.getElementById("month-positions-grid");
  grid.innerHTML = "";

  month.positions.forEach((position) => {
    const card = document.createElement("article");
    card.className = "position-card";

    card.innerHTML = `
      <h3>${position.ticker} | ${position.company}</h3>
      <p class="position-meta">${position.exchange} · ${position.country} · ${position.sector}</p>
      <p><strong>Tese:</strong> ${position.thesis}</p>
      <p><strong>Katalysatorer:</strong> ${position.catalysts.join(", ")}</p>
      <p><strong>Risiko:</strong> ${position.risk}</p>
      <p><strong>Konfidens:</strong> ${formatConfidence(position.confidence)}</p>
    `;

    grid.appendChild(card);
  });

  const midmonthBlock = document.getElementById("midmonth-block");
  if (month.midmonth_update) {
    const positionsHtml = (month.midmonth_update.positions || [])
      .map(
        (p) => `
          <div class="sub-block">
            <p><strong>${p.ticker}</strong> — ${p.thesis_status}</p>
            <p>${p.comment}</p>
          </div>
        `
      )
      .join("");

    midmonthBlock.innerHTML = `
      <p><strong>Dato:</strong> ${month.midmonth_update.date}</p>
      <p><strong>Status:</strong> ${month.midmonth_update.portfolio_status}</p>
      <p><strong>Hold videre:</strong> ${month.midmonth_update.hold_recommendation}</p>
      <p><strong>Største risiko:</strong> ${month.midmonth_update.biggest_risk_rest_of_month}</p>
      <p>${month.midmonth_update.summary}</p>
      ${positionsHtml}
    `;
  }

  const monthEndBlock = document.getElementById("month-end-block");
  if (month.month_end) {
    const positionsHtml = (month.month_end.positions || [])
      .map(
        (p) => `
          <div class="sub-block">
            <p><strong>${p.ticker}</strong> — ${p.thesis_status}</p>
            <p>${p.comment}</p>
          </div>
        `
      )
      .join("");

    monthEndBlock.innerHTML = `
      <p><strong>Dato:</strong> ${month.month_end.date}</p>
      <p><strong>Resultat:</strong> ${month.month_end.result}</p>
      <p><strong>Hva fungerte best:</strong> ${month.month_end.what_worked_best}</p>
      <p><strong>Hva fungerte dårligst:</strong> ${month.month_end.what_worked_worst}</p>
      <p><strong>Viktigste læring:</strong> ${month.month_end.key_lesson}</p>
      ${positionsHtml}
    `;
  }
}

initMonthPage().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av månedsdata.</p>`;
});