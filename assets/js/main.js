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

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  return value.toFixed(2);
}

function getReturnClass(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "neutral";
  }
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}

function formatDateText(value) {
  if (!value) return "–";
  return value;
}

async function init() {
  const portfolio = await loadJson("data/current_portfolio.json");
  const benchmarks = await loadJson("data/benchmarks.json");
  const updates = await loadJson("data/updates.json");
  const performance = await loadJson("data/performance.json");
  const monthsIndex = await loadJson("data/months/index.json");

  const activeMonthLink = document.getElementById("active-month-link");
  if (activeMonthLink && monthsIndex.active_month) {
    activeMonthLink.href = `month.html?month=${monthsIndex.active_month}`;
  }

  document.getElementById("month-label").textContent = portfolio.label;
  document.getElementById("buy-date").textContent = `Kjøpsdato: ${portfolio.buy_date}`;
  document.getElementById("last-updated").textContent =
    `Sist oppdatert: ${performance.updated_at || portfolio.updated_at || "–"}`;

  const portfolioReturnEl = document.getElementById("portfolio-return");
  portfolioReturnEl.textContent = formatPercent(performance.portfolio_return_pct);
  portfolioReturnEl.className = getReturnClass(performance.portfolio_return_pct);

  const alphaSp500El = document.getElementById("alpha-sp500");
  alphaSp500El.textContent = formatPercent(performance.alpha_vs_sp500);
  alphaSp500El.className = getReturnClass(performance.alpha_vs_sp500);

  const alphaDnbEl = document.getElementById("alpha-dnb");
  alphaDnbEl.textContent = formatPercent(performance.alpha_vs_dnb);
  alphaDnbEl.className = getReturnClass(performance.alpha_vs_dnb);

  document.getElementById("sp500-return").textContent = formatPercent(benchmarks.sp500.return_pct);
  document.getElementById("sp500-current-price").textContent =
    `Kurs nå: ${formatNumber(benchmarks.sp500.current_price)}`;

  const dnbReturnEl = document.getElementById("dnb-return");
  const dnbDateEl = document.getElementById("dnb-date");

  if (
    benchmarks.dnb_global_indeks.buy_nav === null ||
    benchmarks.dnb_global_indeks.buy_nav === undefined ||
    benchmarks.dnb_global_indeks.buy_nav === 0
  ) {
    dnbReturnEl.textContent = "Ikke tilgjengelig";
    dnbDateEl.textContent = "Sist oppdatert NAV: ikke tilgjengelig";
  } else {
    dnbReturnEl.textContent = formatPercent(benchmarks.dnb_global_indeks.return_pct);
    dnbDateEl.textContent =
      `Sist oppdatert NAV: ${formatDateText(benchmarks.dnb_global_indeks.as_of_date)}`;
  }

  const grid = document.getElementById("positions-grid");
  grid.innerHTML = "";

  portfolio.positions.forEach((position) => {
    const card = document.createElement("article");
    card.className = "position-card";

    card.innerHTML = `
      <h3>${position.ticker} | ${position.company}</h3>
      <p class="position-meta">${position.exchange} · ${position.country} · ${position.sector}</p>
      <p><strong>Tese:</strong> ${position.thesis}</p>
      <p><strong>Katalysatorer:</strong> ${position.catalysts_30d.join(", ")}</p>
      <p><strong>Risiko:</strong> ${position.risk}</p>
      <p class="metric"><strong>Kjøpskurs:</strong> ${formatNumber(position.buy_price)}</p>
      <p class="metric"><strong>Kurs nå:</strong> ${formatNumber(position.current_price)}</p>
      <p class="metric">
        <strong>Avkastning:</strong>
        <span class="${getReturnClass(position.return_pct)}">${formatPercent(position.return_pct)}</span>
      </p>
    `;

    grid.appendChild(card);
  });

  if (updates.midmonth_update) {
    document.getElementById("midmonth-date").textContent =
      `Dato: ${updates.midmonth_update.date}`;
    document.getElementById("midmonth-summary").textContent =
      updates.midmonth_update.summary;
    document.getElementById("hold-decision").textContent =
      updates.midmonth_update.hold_to_day_30 || updates.midmonth_update.hold_recommendation || "–";
    document.getElementById("biggest-risk").textContent =
      updates.midmonth_update.biggest_risk_next_2w || updates.midmonth_update.biggest_risk_rest_of_month || "–";
  }
}

init().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av data.</p>`;
});