document.addEventListener("DOMContentLoaded", function () {
    const favoriteButton = document.getElementById("favoriteButton");

    if (favoriteButton) {
        favoriteButton.addEventListener("click", function () {
            fetch(window.location.href, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": favoriteButton.getAttribute("data-csrf-token")
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.is_favorite) {
                        showMessage("Książka została dodana do ulubionych.", "success");
                        favoriteButton.textContent = "Usuń z ulubionych";
                        favoriteButton.classList.remove("btn-primary");
                        favoriteButton.classList.add("btn-danger");
                    } else {
                        showMessage("Książka została usunięta z ulubionych.", "warning");
                        favoriteButton.textContent = "Dodaj do ulubionych";
                        favoriteButton.classList.remove("btn-danger");
                        favoriteButton.classList.add("btn-primary");
                    }
                })
                .catch(error => console.error("Błąd:", error));
        });
    }
});

// Funkcja do wyświetlania powiadomień
function showMessage(message, type) {
    const messagesDiv = document.getElementById("messages");
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-2`;
    alertDiv.role = "alert";
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    messagesDiv.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.classList.remove("show");
        alertDiv.classList.add("hide");
        alertDiv.addEventListener("transitionend", () => alertDiv.remove());
    }, 3000);
}
