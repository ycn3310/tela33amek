const input = document.querySelector("#search-bar");
const modules = document.querySelectorAll(".module-link");
input.addEventListener("input", e => {
    const value = e.target.value;
    console.log(value);
    modules.forEach((moduleLink) => {
        const name = moduleLink.querySelector(".module-name").textContent.toLowerCase();
        moduleLink.style.display = name.includes(value) ? "" : "none";
    })
})