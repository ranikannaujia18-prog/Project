const searchInput = document.getElementById("searchInput");
if (searchInput) {
  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase().trim();
    document.querySelectorAll(".task-item").forEach((item) => {
      const text = item.dataset.search || item.innerText.toLowerCase();
      item.style.display = text.includes(query) ? "flex" : "none";
    });
  });
}

// Render a simple current-month calendar. Task deadlines are managed separately.
const calendarGrid = document.getElementById("calendarGrid");
if (calendarGrid) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const days = new Date(year, month + 1, 0).getDate();
  const labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  labels.forEach((label) => {
    const cell = document.createElement("div");
    cell.className = "cal-cell cal-head";
    cell.textContent = label;
    calendarGrid.appendChild(cell);
  });
  for (let i = 0; i < firstDay; i++) {
    const blank = document.createElement("div");
    blank.className = "cal-cell blank";
    blank.textContent = " ";
    calendarGrid.appendChild(blank);
  }
  for (let day = 1; day <= days; day++) {
    const cell = document.createElement("div");
    cell.className = "cal-cell" + (day === now.getDate() ? " today" : "");
    cell.textContent = day;
    calendarGrid.appendChild(cell);
  }
}
