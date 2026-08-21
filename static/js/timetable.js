// NovaX Timetable Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Division Selector change
    const divisionSelect = document.getElementById('divisionSelect');
    if (divisionSelect) {
        divisionSelect.addEventListener('change', (e) => {
            const sectionId = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('section_id', sectionId);
            window.location.href = currentUrl.toString();
        });
    }

    // 2. Week View / Day View Switcher
    const weekViewBtn = document.getElementById('weekViewBtn');
    const dayViewBtn = document.getElementById('dayViewBtn');
    const timetableTable = document.querySelector('.timetable-table');

    if (weekViewBtn && dayViewBtn && timetableTable) {
        weekViewBtn.addEventListener('click', () => {
            weekViewBtn.classList.add('active');
            dayViewBtn.classList.remove('active');
            // Show all day columns
            document.querySelectorAll('.timetable-table th, .timetable-table td').forEach(el => {
                el.style.display = '';
            });
        });

        dayViewBtn.addEventListener('click', () => {
            dayViewBtn.classList.add('active');
            weekViewBtn.classList.remove('active');
            
            // Highlight today or Monday by default
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const today = days[new Date().getDay()];
            const activeDay = (today === 'Sunday') ? 'Monday' : today;

            // In day view, only show time column and activeDay column
            const headerCells = document.querySelectorAll('.timetable-table thead th');
            let targetColIndex = -1;
            headerCells.forEach((th, idx) => {
                if (th.textContent.includes(activeDay)) {
                    targetColIndex = idx;
                }
            });

            if (targetColIndex !== -1) {
                document.querySelectorAll('.timetable-table tr').forEach(row => {
                    Array.from(row.children).forEach((cell, idx) => {
                        if (idx === 0 || idx === targetColIndex) {
                            cell.style.display = '';
                        } else {
                            cell.style.display = 'none';
                        }
                    });
                });
            }
        });
    }

    // 3. Show/Hide Elective Groups
    const toggleElectiveCheck = document.getElementById('toggleElectiveGroups');
    const electiveSidePanel = document.getElementById('electiveSidePanel');
    if (toggleElectiveCheck && electiveSidePanel) {
        toggleElectiveCheck.addEventListener('change', (e) => {
            electiveSidePanel.style.display = e.target.checked ? 'block' : 'none';
        });
    }

    // 4. Print / PDF Export
    const printBtn = document.getElementById('printTimetableBtn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }

    // 5. Subject Card Click Inspection Modal / Popover
    document.querySelectorAll('.subject-card').forEach(card => {
        card.addEventListener('click', () => {
            const subject = card.querySelector('.subject-name')?.innerText || 'Class';
            const faculty = card.querySelector('.subject-faculty')?.innerText || 'Faculty';
            const room = card.querySelector('.subject-room-tag')?.innerText || 'Room';
            console.log(`Inspecting ${subject} by ${faculty} in ${room}`);
        });
    });
});
