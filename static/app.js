let imageBase64 = null;

document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("image-input");
  const preview = document.getElementById("preview");
  const previewContainer = document.getElementById("preview-container");
  const analyzeBtn = document.getElementById("analyze-btn");
  const resetBtn = document.getElementById("reset-btn");
  const resetSection = document.getElementById("reset-section");

  imageInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) {
      resetPreview();
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      previewContainer.classList.remove("hidden");
      analyzeBtn.disabled = false;

      const base64 = e.target.result.split(",")[1];
      imageBase64 = base64;
    };
    reader.readAsDataURL(file);
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail.target.id === "form-container") {
      injectBase64IntoForm();
      resetSection.classList.remove("hidden");
    }

    if (event.detail.target.id === "confirmation-container") {
      const alert = event.detail.target.querySelector(".alert");
      if (alert) {
        alert.scrollIntoView({ behavior: "smooth", block: "nearest" });
        if (alert.classList.contains("alert-success")) {
          document.body.dispatchEvent(new Event("expensesUpdated"));
          document.body.dispatchEvent(new Event("dashboardUpdated"));
        }
      }
    }

    if (event.detail.target.id === "expenses-list") {
      bindImageButtons();
    }
  });

  document.body.addEventListener("htmx:responseError", (event) => {
    const confirmationContainer = document.getElementById("confirmation-container");
    const message = event.detail.xhr?.responseText || "Une erreur est survenue.";

    confirmationContainer.innerHTML = `
      <div class="alert alert-error">${message}</div>
    `;
    confirmationContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  resetBtn.addEventListener("click", resetApp);

  document.getElementById("image-modal").addEventListener("click", (event) => {
    if (event.target.dataset.closeModal !== undefined) {
      closeImageModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeImageModal();
    }
  });
});

function bindImageButtons() {
  document.querySelectorAll(".btn-image").forEach((button) => {
    button.addEventListener("click", () => {
      openImageModal(button.dataset.imageUrl);
    });
  });
}

function openImageModal(imageUrl) {
  const modal = document.getElementById("image-modal");
  const modalImage = document.getElementById("modal-image");

  modalImage.src = imageUrl;
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
}

function closeImageModal() {
  const modal = document.getElementById("image-modal");
  const modalImage = document.getElementById("modal-image");

  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
  modalImage.src = "";
}

function injectBase64IntoForm() {
  const hiddenField = document.getElementById("image-base64");
  if (hiddenField && imageBase64) {
    hiddenField.value = imageBase64;
  }
}

function resetPreview() {
  const preview = document.getElementById("preview");
  const previewContainer = document.getElementById("preview-container");
  const analyzeBtn = document.getElementById("analyze-btn");
  const imageInput = document.getElementById("image-input");

  preview.src = "";
  previewContainer.classList.add("hidden");
  analyzeBtn.disabled = true;
  imageInput.value = "";
  imageBase64 = null;
}

function resetApp() {
  resetPreview();

  document.getElementById("form-container").innerHTML = "";
  document.getElementById("confirmation-container").innerHTML = "";
  document.getElementById("reset-section").classList.add("hidden");

  document.getElementById("upload-section").scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}
