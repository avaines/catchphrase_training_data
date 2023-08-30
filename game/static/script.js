function showPopup() {
    var popup = document.getElementById("popup");
    popup.style.display = "flex"; // Show the popup
    setTimeout(hidePopup, 3000);  // Hide the popup after 3 seconds (adjust as needed)
}

function hidePopup() {
    var popup = document.getElementById("popup");
    popup.style.display = "none"; // Hide the popup
}