document.addEventListener('DOMContentLoaded', () => {
    const themeCheckbox = document.getElementById('themeCheckbox');
    const htmlElement = document.documentElement;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    
    if (themeCheckbox) {
        // Sync checkbox state with saved theme
        themeCheckbox.checked = (savedTheme === 'dark');
        
        themeCheckbox.addEventListener('change', () => {
            const newTheme = themeCheckbox.checked ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Handle poster images for events (Fixes lint issues in HTML)
    const posters = document.querySelectorAll('.event-poster[data-poster]');
    posters.forEach(poster => {
        const url = poster.getAttribute('data-poster');
        if (url) {
            poster.style.backgroundImage = `url('${url}')`;
        }
    });

    // Category chip selection (Contact Page)
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
        });
    });
});
