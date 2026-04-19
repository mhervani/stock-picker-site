async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Kunne ikke laste ${path}`);
  }
  return response.json();
}

async function initHistory() {
  const index = await loadJson("data/months/index.json");
  const list = document.getElementById("history-list");

  if (!index.months || !index.months.length) {
    list.innerHTML = "<p>Ingen måneder ennå.</p>";
    return;
  }

  list.innerHTML = "";

  for (const monthMeta of index.months) {
    const month = await loadJson(`data/months/${monthMeta.month_id}.json`);

    const item = document.createElement("article");
    item.className = "history-card";

    item.innerHTML = `
      <h3>${month.label}</h3>
      <p class="muted">Kjøpsdato: ${month.buy_date} · Status: ${month.status}</p>
      <p><strong>Konklusjon:</strong> ${month.market_context.portfolio_conclusion || "–"}</p>
      <p><strong>Rangering:</strong> ${(month.portfolio.ranking || []).join(" > ")}</p>
      <p><strong>Porteføljekonfidens:</strong> ${month.market_context.portfolio_confidence || "–"}/10</p>
      <p><a class="nav-link" href="month.html?month=${month.month_id}">Åpne månedsdetaljer</a></p>
    `;

    list.appendChild(item);
  }
}

initHistory().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av historikk.</p>`;
});