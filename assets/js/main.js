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

function calculatePositionReturn(buyPrice, currentPrice) {
  return ((currentPrice - buyPrice) / buyPrice) * 100;
}

function calculatePortfolioReturn(positions) {
  const values = positions.map((p) => p.returnPct);
  const total = values.reduce((sum, value) => sum + value, 0);
  return total / values.length;
}

async function init() {
  const portfolio = await loadJson("data/current_portfolio.json");
  const benchmarks = await loadJson("data/benchmarks.json");
  const updates = await loadJson("data/updates.json");

  document.getElementById("month-label").textContent = portfolio.label;
  document.getElementById("buy-date").textContent = `Kjøpsdato: ${portfolio.buy_date}`;

  const enrichedPositions = portfolio.positions.map((position) => {
    const currentPrice = position.current_price;
    const returnPct = calculatePositionReturn(position.buy_price, currentPrice);
    return { ...position, returnPct };
  });

  const portfolioReturn = calculatePortfolioReturn(enrichedPositions);
  const alphaSp500 = portfolioReturn - benchmarks.sp500.return_pct;
  const alphaDnb = portfolioReturn - benchmarks.dnb_global_indeks.return_pct;

  const portfolioReturnEl = document.getElementById("portfolio-return");
  portfolioReturnEl.textContent = formatPercent(portfolioReturn);
  portfolioReturnEl.className = getReturnClass(portfolioReturn);

  const alphaSp500El = document.getElementById("alpha-sp500");
  alphaSp500El.textContent = formatPercent(alphaSp500);
  alphaSp500El.className = getReturnClass(alphaSp500);

  const alphaDnbEl = document.getElementById("alpha-dnb");
  alphaDnbEl.textContent = formatPercent(alphaDnb);
  alphaDnbEl.className = getReturnClass(alphaDnb);

  document.getElementById("sp500-return").textContent = formatPercent(benchmarks.sp500.return_pct);
  document.getElementById("dnb-return").textContent = formatPercent(benchmarks.dnb_global_indeks.return_pct);
  document.getElementById("dnb-date").textContent =
    `Sist oppdatert NAV: ${benchmarks.dnb_global_indeks.as_of_date}`;

  const grid = document.getElementById("positions-grid");
  grid.innerHTML = "";

  enrichedPositions.forEach((position) => {
    const card = document.createElement("article");
    card.className = "position-card";

    card.innerHTML = `
      <h3>${position.ticker} | ${position.company}</h3>
      <p class="position-meta">${position.exchange} · ${position.country} · ${position.sector}</p>
      <p><strong>Tese:</strong> ${position.thesis}</p>
      <p><strong>Katalysatorer:</strong> ${position.catalysts_30d.join(", ")}</p>
      <p><strong>Risiko:</strong> ${position.risk}</p>
      <p class="metric"><strong>Kjøpskurs:</strong> ${position.buy_price}</p>
      <p class="metric"><strong>Kurs nå:</strong> ${position.current_price}</p>
      <p class="metric"><strong>Avkastning:</strong> <span class="${getReturnClass(position.returnPct)}">${formatPercent(position.returnPct)}</span></p>
    `;

    grid.appendChild(card);
  });

  if (updates.midmonth_update) {
    document.getElementById("midmonth-date").textContent = `Dato: ${updates.midmonth_update.date}`;
    document.getElementById("midmonth-summary").textContent = updates.midmonth_update.summary;
    document.getElementById("hold-decision").textContent = updates.midmonth_update.hold_to_day_30;
    document.getElementById("biggest-risk").textContent = updates.midmonth_update.biggest_risk_next_2w;
  }
}

init().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av data.</p>`;
});