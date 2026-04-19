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

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  return value.toFixed(2);
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function renderMonthChart(monthId, chartData) {
  const canvas = document.getElementById("month-performance-chart");
  const note = document.getElementById("chart-note");

  if (!canvas || !chartData || chartData.month_id !== monthId || !chartData.series || !chartData.series.length) {
    if (note) {
      note.textContent = "Ingen grafdata tilgjengelig for denne måneden ennå.";
    }
    return;
  }

  const labels = chartData.series.map((point, index) => {
    if (!point.timestamp) return index === 0 ? "Start" : "";
    return new Date(point.timestamp).toLocaleString("no-NO", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });
  });

  const portfolioData = chartData.series.map((point) => point.portfolio_return_pct);
  const sp500Data = chartData.series.map((point) => point.sp500_return_pct);
  const dnbData = chartData.series.map((point) => point.dnb_return_pct);

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Portefølje",
          data: portfolioData,
          borderWidth: 2,
          tension: 0.25
        },
        {
          label: "S&P 500",
          data: sp500Data,
          borderWidth: 2,
          tension: 0.25
        },
        {
          label: "DNB Global Indeks",
          data: dnbData,
          borderWidth: 2,
          tension: 0.25,
          spanGaps: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          labels: {
            color: "#f5f7fb"
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#aab4d0"
          },
          grid: {
            color: "#273156"
          }
        },
        y: {
          ticks: {
            color: "#aab4d0",
            callback: function(value) {
              return value + "%";
            }
          },
          grid: {
            color: "#273156"
          }
        }
      }
    }
  });

  if (note) {
    note.textContent = "Grafen viser utvikling i prosent siden kjøp for aktiv måned.";
  }
}

function renderPositions(positions) {
  const grid = document.getElementById("month-positions-grid");
  grid.innerHTML = "";

  positions.forEach((position) => {
    const card = document.createElement("article");
    card.className = "position-card";

    card.innerHTML = `
      <h3>${position.ticker} | ${position.company}</h3>
      <p class="position-meta">${position.exchange} · ${position.country} · ${position.sector}</p>
      <p><strong>Tese:</strong> ${position.thesis}</p>
      <p><strong>Katalysatorer:</strong> ${(position.catalysts || []).join(", ")}</p>
      <p><strong>Risiko:</strong> ${position.risk}</p>
      <p><strong>Konfidens:</strong> ${formatConfidence(position.confidence)}</p>
      <p class="muted"><strong>Kjøpskurs:</strong> ${formatNumber(position.buy_price)}</p>
    `;

    grid.appendChild(card);
  });
}

function renderMidmonth(midmonth) {
  const midmonthBlock = document.getElementById("midmonth-block");

  if (!midmonth) {
    midmonthBlock.innerHTML = `<p>Ingen oppdatering lagt inn ennå.</p>`;
    return;
  }

  const positionsHtml = (midmonth.positions || [])
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
    <p><strong>Dato:</strong> ${midmonth.date}</p>
    <p><strong>Status:</strong> ${midmonth.portfolio_status}</p>
    <p><strong>Hold videre:</strong> ${midmonth.hold_recommendation}</p>
    <p><strong>Største risiko:</strong> ${midmonth.biggest_risk_rest_of_month}</p>
    <p>${midmonth.summary}</p>
    ${positionsHtml}
  `;
}

function renderMonthEnd(monthEnd) {
  const monthEndBlock = document.getElementById("month-end-block");

  if (!monthEnd) {
    monthEndBlock.innerHTML = `<p>Ingen månedsslutt lagt inn ennå.</p>`;
    return;
  }

  const positionsHtml = (monthEnd.positions || [])
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
    <p><strong>Dato:</strong> ${monthEnd.date}</p>
    <p><strong>Resultat:</strong> ${monthEnd.result}</p>
    <p><strong>Hva fungerte best:</strong> ${monthEnd.what_worked_best}</p>
    <p><strong>Hva fungerte dårligst:</strong> ${monthEnd.what_worked_worst}</p>
    <p><strong>Viktigste læring:</strong> ${monthEnd.key_lesson}</p>
    ${positionsHtml}
  `;
}

function renderHeld(heldData, monthId) {
  const heldBlock = document.getElementById("held-block");

  const portfolio = (heldData.portfolios || []).find(
    (item) => item.origin_month_id === monthId
  );

  if (!portfolio) {
    heldBlock.innerHTML = `<p>Ingen videre tracking ennå.</p>`;
    return;
  }

  const positionsHtml = (portfolio.positions || [])
    .map(
      (p) => `
        <div class="sub-block">
          <p><strong>${p.ticker}</strong></p>
          <p>Kjøpskurs: ${formatNumber(p.buy_price)}</p>
          <p>Kurs nå: ${formatNumber(p.current_price)}</p>
          <p>Avkastning: ${formatPercent(p.return_pct)}</p>
        </div>
      `
    )
    .join("");

  heldBlock.innerHTML = `
    <p><strong>Status:</strong> ${portfolio.status}</p>
    <p><strong>Kjøpsdato:</strong> ${portfolio.buy_date}</p>
    <p><strong>Måned lukket:</strong> ${portfolio.closed_date}</p>
    <p><strong>Videre avkastning:</strong> ${formatPercent(portfolio.portfolio_return_pct)}</p>
    <p class="muted"><strong>Sist oppdatert:</strong> ${portfolio.updated_at || "–"}</p>
    ${positionsHtml}
  `;
}

async function initMonthPage() {
  const monthId = getMonthIdFromUrl();

  const month = await loadJson(`data/months/${monthId}.json`);
  const chartData = await loadJson("data/chart_data.json");
  const heldData = await loadJson("data/held_positions.json");

  document.getElementById("month-page-title").textContent = month.label;
  document.getElementById("month-label").textContent = month.label;
  document.getElementById("month-buy-date").textContent = `Kjøpsdato: ${month.buy_date}`;
  document.getElementById("month-analysis-date").textContent = `Analysedato: ${month.analysis_date}`;
  document.getElementById("month-status").textContent = `Status: ${month.status}`;

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

  document.getElementById("month-sp500-buy").textContent =
    formatNumber(month.benchmarks.sp500_buy_price);
  document.getElementById("month-sp500-proxy").textContent =
    month.benchmarks.sp500_proxy_ticker || "–";
  document.getElementById("month-dnb-buy").textContent =
    formatNumber(month.benchmarks.dnb_global_indeks_buy_nav);
  document.getElementById("month-dnb-date").textContent =
    month.benchmarks.dnb_global_indeks_as_of_date || "–";

  renderPositions(month.positions || []);
  renderMidmonth(month.midmonth_update);
  renderMonthEnd(month.month_end);
  renderHeld(heldData, monthId);
  renderMonthChart(monthId, chartData);
}

initMonthPage().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av månedsdata.</p>`;
});