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

async function initTrackRecord() {
  const trackRecord = await loadJson("data/track_record.json");

  document.getElementById("months-completed").textContent = trackRecord.months_completed;
  document.getElementById("beat-sp500").textContent = trackRecord.beat_sp500_count;
  document.getElementById("beat-dnb").textContent = trackRecord.beat_dnb_count;
  document.getElementById("avg-alpha-sp500").textContent = formatPercent(trackRecord.avg_alpha_vs_sp500);
  document.getElementById("avg-alpha-dnb").textContent = formatPercent(trackRecord.avg_alpha_vs_dnb);
  document.getElementById("cumulative-return").textContent = formatPercent(trackRecord.cumulative_portfolio_return_pct);
}

initTrackRecord().catch((error) => {
  console.error(error);
  document.body.innerHTML += `<p style="padding: 20px;">Feil ved lasting av track record.</p>`;
});