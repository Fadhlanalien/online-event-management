// Toggles the mobile nav menu open/closed for the custom navbar (navbar01)
document.addEventListener('DOMContentLoaded', function () {
  var toggleBtn = document.getElementById('navToggle');
  var menu = document.getElementById('navMenu');

  if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', function () {
      menu.classList.toggle('active');
    });
  }
});