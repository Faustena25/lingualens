// home.js — validation + interaction for the two input cards.
// No real submission logic yet (that's Step 6, once routes exist) —
// for now this proves the UI states work end to end.

document.addEventListener("DOMContentLoaded", () => {
  setupYoutubeForm();
  setupCsvForm();
});

function isValidYoutubeUrl(url) {
  return /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/.test(url);
}

function setupYoutubeForm() {
  const form = document.getElementById("youtube-form");
  const input = document.getElementById("youtube-url");
  const error = document.getElementById("youtube-error");
  const submitBtn = document.getElementById("youtube-submit");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const url = input.value.trim();

    if (!isValidYoutubeUrl(url)) {
      error.style.display = "block";
      input.style.borderColor = "var(--hinglish-rose)";
      return;
    }
    error.style.display = "none";
    input.style.borderColor = "";
    setLoading(submitBtn, "Fetching comments...");
    // Step 6 will POST to /analyse/youtube here and redirect to the dashboard.
  });

  input.addEventListener("input", () => {
    error.style.display = "none";
    input.style.borderColor = "";
  });
}

function setupCsvForm() {
  const form = document.getElementById("csv-form");
  const fileInput = document.getElementById("csv-file");
  const dropzone = document.getElementById("csv-dropzone");
  const dropzoneText = document.getElementById("csv-dropzone-text");
  const error = document.getElementById("csv-error");
  const submitBtn = document.getElementById("csv-submit");

  ["dragover", "dragenter"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, () => dropzone.classList.remove("dragover"))
  );
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      showFileName(file);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) showFileName(fileInput.files[0]);
  });

  function showFileName(file) {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      error.textContent = "That file isn't a .csv — choose a CSV file.";
      error.style.display = "block";
      dropzoneText.textContent = "Drag a CSV here, or click to browse";
      fileInput.value = "";
      return;
    }
    error.style.display = "none";
    dropzoneText.innerHTML = `<span class="file-name">${file.name}</span>`;
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!fileInput.files.length) {
      error.textContent = "Please choose a .csv file with a comment or review column.";
      error.style.display = "block";
      return;
    }
    setLoading(submitBtn, "Uploading...");
    // Step 6 will POST the file to /analyse/csv here and redirect to the dashboard.
  });
}

function setLoading(button, label) {
  button.disabled = true;
  button.innerHTML = `<span class="ll-spinner"></span>${label}`;
}
