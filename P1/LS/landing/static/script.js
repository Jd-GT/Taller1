document.addEventListener("DOMContentLoaded", function () {
    console.log("JS cargado correctamente");

    // Agregar funcionalidad de búsqueda
    const searchButton = document.querySelector(".search-bar button");
    searchButton.addEventListener("click", function (e) {
        e.preventDefault();
        alert("Funcionalidad de búsqueda en construcción...");
    });

    // Agregar evento al botón de carrito
    const cartButton = document.querySelector(".btn-add");
    cartButton.addEventListener("click", function () {
        alert("Carrito aún no implementado.");
    });
});
