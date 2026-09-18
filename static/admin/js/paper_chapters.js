document.addEventListener("DOMContentLoaded", function () {
    const courseSelect = document.getElementById("id_course");
    const chapterSelect = document.getElementById("id_chapter");

    if (!courseSelect || !chapterSelect) {
        return;
    }

    courseSelect.addEventListener("change", function () {
        const courseId = this.value;

        // Clear current chapters
        chapterSelect.innerHTML = "";

        if (!courseId) {
            return;
        }

        fetch(
            `/admin/pages/paper/chapters-for-course/?course_id=${courseId}`
        )
            .then(response => response.json())
            .then(chapters => {
                chapters.forEach(chapter => {
                    const option = document.createElement("option");

                    option.value = chapter.id;
                    option.textContent = chapter.name;

                    chapterSelect.appendChild(option);
                });
            });
    });
});