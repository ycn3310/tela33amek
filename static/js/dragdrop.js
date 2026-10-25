const dragArea = document.getElementById("drag-area");
const fileInput = document.getElementById("fileinput");
const fileName = document.getElementById("file-name");
const fileList = document.getElementById("file-list");
const fileError = document.getElementById("file-error");
const submitButton = document.getElementById("uploadButton");
const form = fileInput.closest("form");

const MAX_SIZE = 2 * 1024 * 1024; // 2 MB per file
let selected = [];

function formatSize(bytes) {
    if (bytes < 1024 * 1024) return Math.max(1, Math.round(bytes / 1024)) + " KB";
    return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

// PDFs and raster images only (SVG is excluded on purpose, it can contain scripts)
function isAllowedType(file) {
    if (file.type) {
        return file.type === "application/pdf" ||
               (file.type.startsWith("image/") && file.type !== "image/svg+xml");
    }
    return /\.(pdf|jpe?g|png|gif|webp|bmp|heic|heif|avif)$/i.test(file.name);
}

// Keep the real <input> in sync so the form submits exactly what is listed
function syncInput() {
    const dt = new DataTransfer();
    selected.forEach(f => dt.items.add(f));
    fileInput.files = dt.files;
}

function showErrors(messages) {
    fileError.replaceChildren();
    messages.forEach(m => {
        const line = document.createElement("span");
        line.textContent = m;
        fileError.appendChild(line);
    });
}

function render() {
    fileList.replaceChildren();

    selected.forEach(file => {
        const li = document.createElement("li");
        li.className = "file-item";

        const name = document.createElement("span");
        name.className = "name";
        name.textContent = (file.type === "application/pdf" ? "📄 " : "🖼 ") + file.name;
        name.title = file.name;

        const size = document.createElement("span");
        size.className = "size";
        size.textContent = formatSize(file.size);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "remove";
        remove.setAttribute("aria-label", "Remove " + file.name);
        remove.textContent = "×";
        remove.addEventListener("click", () => {
            selected = selected.filter(f => f !== file);
            syncInput();
            render();
            showErrors([]);
        });

        li.append(name, size, remove);
        fileList.appendChild(li);
    });

    fileName.textContent = selected.length
        ? `✅ ${selected.length} file${selected.length > 1 ? "s" : ""} ready to upload`
        : "";
}

function addFiles(files) {
    const errors = [];

    Array.from(files).forEach(file => {
        if (!isAllowedType(file)) {
            errors.push(`${file.name}: only PDF or image files are allowed.`);
        } else if (file.size === 0) {
            errors.push(`${file.name}: the file is empty.`);
        } else if (file.size > MAX_SIZE) {
            errors.push(`${file.name}: too large (${formatSize(file.size)}), the maximum is 2 MB.`);
        } else {
            const duplicate = selected.some(f =>
                f.name === file.name && f.size === file.size && f.lastModified === file.lastModified);
            if (!duplicate) selected.push(file);
        }
    });

    syncInput();
    render();
    showErrors(errors);
}

// Files picked with the Browse button
fileInput.addEventListener("change", () => addFiles(fileInput.files));

// Prevent the browser from opening the file
["dragenter", "dragover", "dragleave", "drop"].forEach(event => {
    dragArea.addEventListener(event, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

// Highlight the drop area
["dragenter", "dragover"].forEach(event => {
    dragArea.addEventListener(event, () => dragArea.classList.add("dragging"));
});

// Remove highlight
dragArea.addEventListener("dragleave", () => dragArea.classList.remove("dragging"));

// Handle dropped files
dragArea.addEventListener("drop", e => {
    dragArea.classList.remove("dragging");
    addFiles(e.dataTransfer.files);
});

// The input is hidden, so "required" can't show a message: check here instead
form.addEventListener("submit", e => {
    if (selected.length === 0) {
        e.preventDefault();
        showErrors(["Please add at least one PDF or image."]);
        dragArea.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
    }
    submitButton.disabled = true;
    submitButton.textContent = "Uploading…";
});

// Reset the button if the user comes back with the browser's back button
window.addEventListener("pageshow", () => {
    submitButton.disabled = false;
    submitButton.textContent = "Submit";
});
