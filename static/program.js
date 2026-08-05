const browsebutton = document.querySelector(".browse-button");
const fileinput = document.getElementById("fileinput");

browsebutton.addEventListener("click", () => {
    fileinput.click();
})

const filename = document.getElementById("file-name");

fileinput.addEventListener("change", () => {
    if(fileinput.files.length >0){
        filename.innerHTML = `📄 ${fileinput.files[0].name}<br>✅ Ready to upload`;
    }
})

function setupDropdown(dropdown) {
    const input = dropdown.querySelector("input");
    const list = dropdown.querySelector("ul");
    const items = list.querySelectorAll("li");

    // Show all items when focused
    input.addEventListener("focus", () => {
        items.forEach(item => item.style.display = "");
        list.style.display = "block";
    });

    // Filter items
    input.addEventListener("input", function () {
        const value = this.value.toLowerCase();
        let hasVisible = false;

        items.forEach(item => {
            const visible = item.textContent.toLowerCase().includes(value);
            item.style.display = visible ? "" : "none";

            if (visible) hasVisible = true;
        });

        list.style.display = hasVisible ? "block" : "none";
    });

    // Select an item
    items.forEach(item => {
        item.addEventListener("click", () => {
            input.value = item.textContent;
            list.style.display = "none";
        });
    });
}

// Initialize every dropdown on the page
document.querySelectorAll(".dropdown").forEach(setupDropdown);

// Hide all dropdowns when clicking outside
document.addEventListener("click", e => {
    if (!e.target.closest(".dropdown")) {
        document.querySelectorAll(".dropdown ul").forEach(list => {
            list.style.display = "none";
        });
    }
});