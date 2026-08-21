// NovaX Chart.js Analytics Initializers

document.addEventListener('DOMContentLoaded', () => {
    // 1. Teacher Load Distribution Bar Chart
    const teacherLoadCanvas = document.getElementById('teacherLoadChart');
    if (teacherLoadCanvas && typeof Chart !== 'undefined') {
        const labels = JSON.parse(teacherLoadCanvas.dataset.labels || '[]');
        const data = JSON.parse(teacherLoadCanvas.dataset.loads || '[]');

        new Chart(teacherLoadCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Assigned Weekly Hours',
                    data: data,
                    backgroundColor: 'rgba(99, 102, 241, 0.75)',
                    borderColor: '#6366f1',
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 2. Syllabus Coverage Distribution Donut Chart
    const syllabusDistCanvas = document.getElementById('syllabusDistChart');
    if (syllabusDistCanvas && typeof Chart !== 'undefined') {
        const counts = JSON.parse(syllabusDistCanvas.dataset.counts || '{}');

        new Chart(syllabusDistCanvas, {
            type: 'doughnut',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    data: Object.values(counts),
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#3b82f6',
                        '#10b981'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '70%'
            }
        });
    }

    // 3. Teacher Dashboard Weekly Hours Chart
    const weeklyTeacherCanvas = document.getElementById('teacherWeeklyChart');
    if (weeklyTeacherCanvas && typeof Chart !== 'undefined') {
        const days = JSON.parse(weeklyTeacherCanvas.dataset.days || '[]');
        const lectures = JSON.parse(weeklyTeacherCanvas.dataset.lectures || '[]');

        new Chart(weeklyTeacherCanvas, {
            type: 'bar',
            data: {
                labels: days,
                datasets: [{
                    label: 'Lectures',
                    data: lectures,
                    backgroundColor: 'rgba(16, 185, 129, 0.75)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }
});
