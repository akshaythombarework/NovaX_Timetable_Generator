// NovaX Main Global Scripts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Management (Dark / Light)
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('novax-theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (themeToggle) {
        themeToggle.checked = (savedTheme === 'dark');
        themeToggle.addEventListener('change', (e) => {
            const newTheme = e.target.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('novax-theme', newTheme);
        });
    }

    // 2. Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // 4. Dynamic Data Color and Width Attributes
    document.querySelectorAll('[data-color]').forEach(el => {
        if (el.dataset.color) {
            el.style.backgroundColor = el.dataset.color;
        }
    });

    document.querySelectorAll('[data-width]').forEach(el => {
        if (el.dataset.width) {
            el.style.width = el.dataset.width + '%';
        }
    });
});
