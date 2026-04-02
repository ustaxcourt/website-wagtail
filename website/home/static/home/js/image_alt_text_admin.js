(function () {
  // Only run on image edit pages: /admin/images/{id}/
  const match = window.location.pathname.match(/\/admin\/images\/(\d+)\//);
  if (!match) return;

  const imageId = match[1];

  function getCsrfToken() {
    const cookie = document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="));
    return cookie ? cookie.trim().split("=")[1] : "";
  }

  function init() {
    const titleInput = document.querySelector("#id_title");
    if (!titleInput) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "Generate with AI";
    btn.className = "button button-secondary";
    btn.style.marginTop = "0.5rem";
    btn.style.display = "block";

    titleInput.parentNode.appendChild(btn);

    btn.addEventListener("click", async function () {
      btn.disabled = true;
      btn.textContent = "Generating…";

      try {
        const res = await fetch("/chatbot/generate-alt-text/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ image_id: imageId }),
        });
        const data = await res.json();
        if (data.alt_text) {
          titleInput.value = data.alt_text;
          titleInput.dispatchEvent(new Event("change", { bubbles: true }));
        } else {
          alert(data.error || "Failed to generate alt text.");
        }
      } catch {
        alert("Could not reach the server. Please check your connection.");
      } finally {
        btn.disabled = false;
        btn.textContent = "Generate with AI";
      }
    });
  }

  // Wagtail admin is a SPA — wait for the DOM to settle
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
