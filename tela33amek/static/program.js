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