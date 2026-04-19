async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Kunne ikke laste ${path}`);
  }
  return response.json();
}

function formatConfidence(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "–";
  }
  return `${value}/10`;
}

function getStatusBadge(status) {
  const normalized = status || "unknown";
  const cls =
    normalized === "active"
      ? "badge badge-active"
      : normalized === "completed"
      ? "badge badge-completed"
      : "badge";
  return `<span class="${cls}">${normalized}</span>`;
}

async function initHistory() {
  const index = await loadJson("data/months/index.json");
  const held = await loadJson("data/held_positions.json");

  const activeMonth = index.active_month || "–";
  const months = index.months || [];
  const completedCount = months.filter((m) => m.status === "completed").length;
  const heldCount = (held.portfolios || []).length;

  document.getElementById("history-active-month").textContent =
    activeMonth === "–" ? "Ingen aktiv måned" : `Aktiv måned: ${activeMonth}`;
  document.getElementById("history-month-count").textContent =
    `Antall måneder: ${months.length}`;
  document.getElementById("history-active-label").textContent = activeMonth;
  document.getElementById("history-completed-count").textContent = completedCount;
  document.getElementById("history-held-count").textContent = heldCount;

  const list = document.getElementById("history-list");

  if (!months.length) {
    list.innerHTML = "<p>Ingen måneder ennå.</p>";
    return;
  }

  list.innerHTML = "";

  for (const monthMeta of months) {
    const month = await loadJson(`data/months/${monthMeta.month_id}.json`);

    const item = document.createElement("article");
    item.className = "history-card";

    item.innerHTML = `
      <div class="history-card-top">
        <div>
          <h3>${month.label}</h3>
          <p class="muted">Kjøpsdato: ${month.buy_date} · Analysedato: ${month.analysis_date}</p>
        </div>
        <div>${getStatusBadge(month.status)}</div>
      </div>

      <p><strong>Konklusjon:</strong> ${month.market_context.portfolio_conclusion || "–"}</p>
      <p><strong>Porteføljekonfidens:</strong> ${formatConfidence(month.market_context.portfolio_confidence)}</p>
      <p><strong>Rangering:</strong> ${(month.portfolio.ranking || []).join(" > ")}</p>
      <p><strong>Hvorfor denne porteføljen:</strong> ${month.portfolio.why_this_portfolio_can_win || "–"}</p>

      <div class="history-links">
        <a class="nav-link" href="month.html?month=${month.month_id}">Åpne månedsdetaljer</a>
      </div>
    `;

    list.appendChild(item);
  }
}

initHistory().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av historikk.</p>`;
});