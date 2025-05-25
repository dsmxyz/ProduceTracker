document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;

    // Check for saved user preference
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode === 'dark') {
        htmlElement.setAttribute('data-bs-theme', 'dark');
        darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i> Light Mode';
        updateFooterForDarkMode();
    }

    // Toggle dark mode
    darkModeToggle.addEventListener('click', function() {
        if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
            htmlElement.setAttribute('data-bs-theme', 'light');
            darkModeToggle.innerHTML = '<i class="bi bi-moon-fill"></i> Dark Mode';
            localStorage.setItem('darkMode', 'light');
            updateFooterForDarkMode(false);
        } else {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i> Light Mode';
            localStorage.setItem('darkMode', 'dark');
            updateFooterForDarkMode(true);
        }
    });

    // Function to update footer colors
    function updateFooterForDarkMode(isDark) {
        const footer = document.querySelector('footer');
        if (footer) {
            if (isDark) {
                footer.classList.remove('bg-light');
                footer.classList.add('bg-dark');
            } else {
                footer.classList.remove('bg-dark');
                footer.classList.add('bg-light');
            }
        }
    }
});