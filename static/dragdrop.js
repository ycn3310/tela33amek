const dragArea = document.getElementById("drag-area");
const fileInput = document.getElementById("fileinput");
const fileName = document.getElementById("file-name");

// Prevent the browser from opening the file
["dragenter", "dragover", "dragleave", "drop"].forEach(event => {
    dragArea.addEventListener(event, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

// Highlight the drop area
dragArea.addEventListener("dragover", () => {
    dragArea.classList.add("dragging");
});

// Remove highlight
dragArea.addEventListener("dragleave", () => {
    dragArea.classList.remove("dragging");
});

// Handle the dropped file
dragArea.addEventListener("drop", e => {
    dragArea.classList.remove("dragging");

    const files = e.dataTransfer.files;

    if (files.length > 0) {
        fileInput.files = files;
        fileName.textContent = files[0].name;
    }
});