import * as pdfjsLib from
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs";

pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs";

let activeViewer = null;

const viewerStates = new WeakMap();

const MIN_ZOOM = 0.25;
const MAX_ZOOM = 3;

function initViewer(viewer) {
    if (viewerStates.has(viewer)) return viewerStates.get(viewer);

    const state = {
        pdf: null,
        task: null,
        renderTask: null,
        image: null,
        kind: null, // "pdf" | "image"
        page: 1,
        zoom: 1,
        version: 0,
        objectUrl: null,
    };

    viewerStates.set(viewer, state);

    const $ = selector => viewer.querySelector(selector);
    const canvas = $("[data-pdf-canvas]");
    const ctx = canvas.getContext("2d");

    const status = $("[data-pdf-status]");
    const pageLabel = $("[data-current-page]");
    const countLabel = $("[data-page-count]");
    const zoomLabel = $("[data-zoom-level]");
    const prev = $("[data-prev]");
    const next = $("[data-next]");
    const zoomOut = $("[data-zoom-out]");
    const zoomIn = $("[data-zoom-in]");

    // Width available to the canvas, based on the actual container.
    function availableWidth() {
        const el = canvas.parentElement || viewer;
        const cs = getComputedStyle(el);
        const padding =
            parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
        const width = el.clientWidth - padding;

        return width > 0 ? width : window.innerWidth - 32;
    }

    // Zoom that makes the content fit the screen width.
    function fitZoom(naturalWidth, maxZoom) {
        const zoom = availableWidth() / naturalWidth;
        return Math.round(Math.max(MIN_ZOOM, Math.min(maxZoom, zoom)) * 100) / 100;
    }

    function updateControls() {
        const count = state.pdf?.numPages ?? 0;

        pageLabel.textContent = state.page;
        countLabel.textContent = count || "—";
        zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;

        prev.disabled = !state.pdf || state.page <= 1;
        next.disabled = !state.pdf || state.page >= count;
        zoomOut.disabled = state.zoom <= MIN_ZOOM;
        zoomIn.disabled = state.zoom >= MAX_ZOOM;
    }

    async function renderPage() {
        const isImage = state.kind === "image";

        if (isImage ? !state.image : !state.pdf) return;

        if (state.renderTask) {
            state.renderTask.cancel();
            state.renderTask = null;
        }

        const version = state.version;
        const ratio = window.devicePixelRatio || 1;

        // --- Image: draw the bitmap directly on the canvas ---
        if (isImage) {
            // zoom 1 = natural size.
            const scale = state.zoom;
            const width = state.image.width * scale;
            const height = state.image.height * scale;

            canvas.width = Math.ceil(width * ratio);
            canvas.height = Math.ceil(height * ratio);
            canvas.style.maxWidth = "none"; // don't let CSS squash the width
            canvas.style.width = `${width}px`;
            canvas.style.height = `${height}px`;

            ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
            ctx.imageSmoothingQuality = "high";
            ctx.drawImage(state.image, 0, 0, width, height);
            ctx.setTransform(1, 0, 0, 1, 0, 0);

            status.textContent = "";
            return;
        }

        // --- PDF ---
        const page = await state.pdf.getPage(state.page);

        if (version !== state.version) return;

        const viewport = page.getViewport({ scale: state.zoom });

        canvas.width = Math.ceil(viewport.width * ratio);
        canvas.height = Math.ceil(viewport.height * ratio);
        canvas.style.maxWidth = "none"; // don't let CSS squash the width
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;

        const task = page.render({
            canvasContext: ctx,
            viewport,
            transform: ratio === 1
                ? null
                : [ratio, 0, 0, ratio, 0, 0],
        });

        state.renderTask = task;

        try {
            await task.promise;

            if (version === state.version) {
                status.textContent = "";
            }
        } catch (error) {
            if (error.name !== "RenderingCancelledException") throw error;
        } finally {
            if (state.renderTask === task) state.renderTask = null;
        }
    }

    async function changePage(page) {
        if (!state.pdf) return;

        state.page = Math.max(1, Math.min(state.pdf.numPages, page));
        updateControls();

        try {
            await renderPage();
        } catch (error) {
            console.error(error);
            status.textContent = "Unable to render this page.";
        }
    }

    const IMAGE_TYPES = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
    };

    // Identify the file from its magic bytes, falling back to the header.
    function detectFileType(buffer, headerType = "") {
        const b = new Uint8Array(buffer, 0, Math.min(12, buffer.byteLength));
        const ascii = (from, to) => String.fromCharCode(...b.slice(from, to));

        if (ascii(0, 4) === "%PDF") return "application/pdf";
        if (b[0] === 0x89 && ascii(1, 4) === "PNG") return "image/png";
        if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return "image/jpeg";
        if (ascii(0, 4) === "GIF8") return "image/gif";
        if (ascii(0, 4) === "RIFF" && ascii(8, 12) === "WEBP") return "image/webp";

        const clean = headerType.split(";")[0].trim().toLowerCase();
        return clean || "application/pdf";
    }

    async function loadPdf() {
        const version = ++state.version;

        if (state.renderTask) {
            state.renderTask.cancel();
            state.renderTask = null;
        }

        if (state.task) {
            try {
                await state.task.destroy();
            } catch {
                // Previous task may already be closed.
            }
        }

        // Release the previous image, if any.
        if (state.image) {
            state.image.close?.();
            state.image = null;
        }

        state.task = null;
        state.pdf = null;
        state.kind = null;
        state.page = 1;
        state.zoom = 1; // temporary, replaced by the fit zoom once loaded

        if (state.objectUrl) {
            URL.revokeObjectURL(state.objectUrl);
            state.objectUrl = null;
        }

        canvas.width = 0;
        canvas.height = 0;
        updateControls();
        status.textContent = "Loading file…";

        try {
            const response = await fetch(viewer.dataset.pdfUrl, {
                credentials: "same-origin",
            });

            if (!response.ok) {
                throw new Error(`File request failed: ${response.status}`);
            }

            const buffer = await response.arrayBuffer();

            if (version !== state.version) return;

            const mime = detectFileType(
                buffer,
                response.headers.get("Content-Type") || ""
            );
            const isImage = mime in IMAGE_TYPES;
            const isPdf = mime === "application/pdf";

            if (!isImage && !isPdf) {
                throw new Error(`Unsupported file type: ${mime}`);
            }

            const blob = new Blob([buffer], { type: mime });

            if (isPdf) {
                const task = pdfjsLib.getDocument({ data: buffer });
                state.task = task;

                const pdf = await task.promise;

                if (version !== state.version) {
                    await pdf.destroy();
                    return;
                }

                state.pdf = pdf;
                state.kind = "pdf";

                const firstPage = await pdf.getPage(1);
                if (version !== state.version) return;

                // Fit to width, but don't blow small pages up beyond 150%.
                state.zoom = fitZoom(firstPage.getViewport({ scale: 1 }).width, 1.5);
            } else {
                const bitmap = await createImageBitmap(blob);

                if (version !== state.version) {
                    bitmap.close?.();
                    return;
                }

                state.image = bitmap;
                state.kind = "image";

                // Fit to width, but never upscale beyond natural size.
                state.zoom = fitZoom(bitmap.width, 1);
            }

            state.objectUrl = URL.createObjectURL(blob);

            const ext = isPdf ? "pdf" : IMAGE_TYPES[mime];
            const download = $("[data-close]").parentElement
                .querySelector(".pdf-download");

            download.href = state.objectUrl;
            download.download = `paper-${viewer.id.replace("pdf-viewer-", "")}.${ext}`;

            updateControls();
            await renderPage();
        } catch (error) {
            if (version !== state.version) return;

            console.error("File viewer error:", error);
            status.textContent =
                "Could not load this paper. Check your connection or permissions.";
        }
    }

    prev.addEventListener("click", () => changePage(state.page - 1));
    next.addEventListener("click", () => changePage(state.page + 1));

    zoomOut.addEventListener("click", async () => {
        state.zoom = Math.max(MIN_ZOOM, state.zoom - 0.25);
        updateControls();

        try {
            await renderPage();
        } catch (error) {
            console.error(error);
        }
    });

    zoomIn.addEventListener("click", async () => {
        state.zoom = Math.min(MAX_ZOOM, state.zoom + 0.25);
        updateControls();

        try {
            await renderPage();
        } catch (error) {
            console.error(error);
        }
    });

    $("[data-fullscreen]").addEventListener("click", async () => {
        try {
            if (document.fullscreenElement === viewer) {
                await document.exitFullscreen();
            } else {
                await viewer.requestFullscreen();
            }
        } catch (error) {
            console.error(error);
        }
    });

    $("[data-close]").addEventListener("click", () => {
        viewer.hidden = true;

        const toggle = document.querySelector(
            `[data-pdf-toggle="${viewer.id.replace("pdf-viewer-", "")}"]`
        );

        toggle?.setAttribute("aria-expanded", "false");

        if (activeViewer === viewer) activeViewer = null;
    });

    state.loadPdf = loadPdf;
    updateControls();

    return state;
}

document.querySelectorAll("[data-pdf-toggle]").forEach(toggle => {
    toggle.addEventListener("click", async () => {
        const id = toggle.dataset.pdfToggle;
        const viewer = document.getElementById(`pdf-viewer-${id}`);

        if (!viewer) return;

        if (!viewer.hidden) {
            viewer.hidden = true;
            toggle.setAttribute("aria-expanded", "false");
            if (activeViewer === viewer) activeViewer = null;
            return;
        }

        if (activeViewer && activeViewer !== viewer) {
            activeViewer.hidden = true;

            document.querySelector(
                `[data-pdf-toggle="${activeViewer.id.replace("pdf-viewer-", "")}"]`
            )?.setAttribute("aria-expanded", "false");
        }

        activeViewer = viewer;
        viewer.hidden = false;
        toggle.setAttribute("aria-expanded", "true");

        const state = initViewer(viewer);

        // state.kind is set for both PDFs and images, so this only loads once.
        if (!state.kind) await state.loadPdf();

        viewer.scrollIntoView({ behavior: "smooth", block: "start" });
    });
});
