// JavaScript do ustawienia dnia tygodnia, daty i godziny
document.addEventListener("DOMContentLoaded", function() {
    const daysOfWeek = ["Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota"];
    const today = new Date();

    // Ustawienie nagłówka z dniem tygodnia
    const dayOfWeek = daysOfWeek[today.getDay()];
    const formattedDate = today.toLocaleDateString("pl-PL", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Uzyskanie godziny i minut
    const hours = String(today.getHours()).padStart(2, '0'); // dodanie zer wiodących
    const minutes = String(today.getMinutes()).padStart(2, '0'); // dodanie zer wiodących
    const formattedTime = `${hours}:${minutes}`;

    // Wyświetlanie pełnej daty z dniem tygodnia i czasem
    document.getElementById("header").innerText = `${dayOfWeek}, ${formattedDate}`;
    document.getElementById("datetime").innerText = formattedTime; // Wyświetlanie godziny
});
