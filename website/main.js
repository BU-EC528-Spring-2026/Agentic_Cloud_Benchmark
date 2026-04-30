const leaderboardRows = [
  {
    "agent": "OpenAI Code + Ops",
    "model": "gpt-4.1-mini",
    "code": 91.4,
    "ops": 72.7,
    "combined": 76.6,
    "scenarios": "61"
  },
  {
    "agent": "Claude Code + Ops",
    "model": "claude-sonnet-4",
    "code": 0,
    "ops": 0,
    "combined": 0,
    "scenarios": "54"
  },
  {
    "agent": "Gold Patch Baseline",
    "model": "reference",
    "code": 100,
    "ops": 100,
    "combined": 100,
    "scenarios": "54"
  }
];

function formatScore(value) {
  return value === 0 ? "Pending" : value.toFixed(1);
}

function average(row) {
  return (row.code + row.ops + row.combined) / 3;
}

const body = document.querySelector("#leaderboard-body");

leaderboardRows
  .map((row) => ({ ...row, avg: average(row) }))
  .sort((a, b) => b.avg - a.avg)
  .forEach((row, index) => {
    const tr = document.createElement("tr");
    const pending = row.avg === 0;

    tr.innerHTML = `
      <td>${index + 1}</td>
      <td><strong>${row.agent}</strong></td>
      <td>${row.model}</td>
      <td class="score">${formatScore(row.code)}</td>
      <td class="score">${formatScore(row.ops)}</td>
      <td class="score">${formatScore(row.combined)}</td>
      <td class="score">${pending ? '<span class="tag">Pending</span>' : row.avg.toFixed(1)}</td>
      <td>${row.scenarios}</td>
    `;
    body.appendChild(tr);
  });
