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

const input = document.getElementById("course-input");
const list = document.getElementById("course-list");
const items = list.getElementsByTagName("li");

input.addEventListener("input", function () {
    const value = this.value.toLowerCase();
    let hasVisible = false;

    for (let item of items) {
        if (item.textContent.toLowerCase().includes(value)) {
            item.style.display = "";
            hasVisible = true;
        } else {
            item.style.display = "none";
        }
    }

    list.style.display = hasVisible ? "block" : "none";
});

for (let item of items) {
    item.addEventListener("click", function () {
        input.value = this.textContent;
        list.style.display = "none";
    });
}

// Hide when clicking outside
document.addEventListener("click", function (e) {
    if (!e.target.closest(".dropdown")) {
        list.style.display = "none";
    }
});
