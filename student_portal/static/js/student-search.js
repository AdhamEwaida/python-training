(() => {
  const form = document.querySelector("[data-student-search]");
  if (!form) return;

  const input = form.querySelector("input[name='q']");
  const results = document.querySelector("#student-results");
  const pagination = document.querySelector("#student-pagination");
  const status = document.querySelector("#student-search-status");
  const apiUrl = form.dataset.apiUrl;
  const detailUrl = form.dataset.detailUrl;
  let timer;
  let controller;

  const element = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  };

  const renderStudents = (students) => {
    results.replaceChildren();
    if (!students.length) {
      const empty = element("div", "empty-state text-center rounded-3 p-5");
      empty.append(element("h2", "h5", "No students have been registered yet."));
      empty.append(element("p", "text-secondary mb-0", "Try another search."));
      results.append(empty);
      return;
    }

    const wrapper = element("div", "table-responsive");
    const table = element("table", "table table-hover align-middle mb-4");
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    ["Name", "Email", "Course", "Average"].forEach((label) => {
      headRow.append(element("th", "", label));
    });
    head.append(headRow);
    table.append(head);

    const body = document.createElement("tbody");
    students.forEach((student) => {
      const row = document.createElement("tr");
      const nameCell = document.createElement("td");
      const link = element("a", "fw-semibold", student.name);
      link.href = detailUrl.replace(/0$/, String(student.id));
      nameCell.append(link);
      row.append(nameCell);
      row.append(element("td", "", student.email));
      row.append(element("td", "", student.course.name));
      row.append(element("td", "", student.average === null ? "—" : Number(student.average).toFixed(2)));
      body.append(row);
    });
    table.append(body);
    wrapper.append(table);
    results.append(wrapper);
  };

  const renderPagination = (meta) => {
    pagination.replaceChildren();
    if (!meta || meta.pages <= 1) return;
    const nav = document.createElement("nav");
    nav.setAttribute("aria-label", "Student pages");
    const group = element("div", "d-flex justify-content-center gap-2");
    const previous = element("button", "btn btn-outline-primary btn-sm", "Previous");
    const next = element("button", "btn btn-outline-primary btn-sm", "Next");
    previous.type = next.type = "button";
    previous.disabled = meta.page <= 1;
    next.disabled = meta.page >= meta.pages;
    previous.addEventListener("click", () => search(meta.page - 1));
    next.addEventListener("click", () => search(meta.page + 1));
    group.append(previous, element("span", "align-self-center", `Page ${meta.page} of ${meta.pages}`), next);
    nav.append(group);
    pagination.append(nav);
  };

  const search = async (page = 1) => {
    controller?.abort();
    controller = new AbortController();
    const params = new URLSearchParams({q: input.value.trim(), page, per_page: 10});
    status.textContent = "Loading students.";
    form.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(`${apiUrl}?${params}`, {
        headers: {Accept: "application/json"},
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Student search failed (${response.status}).`);
      const payload = await response.json();
      renderStudents(payload.students);
      renderPagination(payload.pagination);
      status.textContent = `${payload.pagination.total} student records found.`;
      history.replaceState({}, "", `${location.pathname}?q=${encodeURIComponent(input.value.trim())}`);
    } catch (error) {
      if (error.name !== "AbortError") {
        status.textContent = "Student search failed. Please try again.";
      }
    } finally {
      form.removeAttribute("aria-busy");
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    search();
  });
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => search(), 300);
  });
})();
