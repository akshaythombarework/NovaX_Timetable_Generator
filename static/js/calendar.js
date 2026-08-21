// NovaX FullCalendar Integration Script

document.addEventListener('DOMContentLoaded', () => {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    let calendar;
    if (typeof FullCalendar !== 'undefined') {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listMonth'
            },
            themeSystem: 'standard',
            events: '/api/calendar/events',
            editable: true,
            selectable: true,
            selectMirror: true,
            dayMaxEvents: true,
            select: function(info) {
                // Open add event modal if present
                const startDateInput = document.getElementById('eventStartDate');
                const endDateInput = document.getElementById('eventEndDate');
                if (startDateInput) startDateInput.value = info.startStr;
                if (endDateInput) endDateInput.value = info.endStr;

                const addModal = document.getElementById('addEventModal');
                if (addModal && typeof bootstrap !== 'undefined') {
                    const modal = new bootstrap.Modal(addModal);
                    modal.show();
                }
            },
            eventClick: function(info) {
                const event = info.event;
                const desc = event.extendedProps.description || 'No description provided.';
                const author = event.extendedProps.created_by || 'System';
                
                alert(`📌 ${event.title}\n\n📝 ${desc}\n👤 Added by: ${author}\n📅 Date: ${event.startStr}`);
            }
        });
        calendar.render();
    }

    // Handle Event Creation Form Submit
    const addEventForm = document.getElementById('addEventForm');
    if (addEventForm) {
        addEventForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('eventTitle').value;
            const start = document.getElementById('eventStartDate').value;
            const end = document.getElementById('eventEndDate').value;
            const description = document.getElementById('eventDescription').value;
            const category = document.getElementById('eventCategory').value;
            const color = document.getElementById('eventColor').value;
            const isPublic = document.getElementById('eventIsPublic').checked;

            try {
                const res = await fetch('/api/calendar/events', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title, start, end, description, category, color, is_public: isPublic
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    if (calendar) calendar.refetchEvents();
                    
                    const addModalEl = document.getElementById('addEventModal');
                    if (addModalEl && typeof bootstrap !== 'undefined') {
                        const modalInstance = bootstrap.Modal.getInstance(addModalEl);
                        if (modalInstance) modalInstance.hide();
                    }
                    addEventForm.reset();
                } else {
                    const err = await res.json();
                    alert('Error adding event: ' + (err.error || 'Failed to save'));
                }
            } catch (err) {
                console.error(err);
                alert('Connection error occurred.');
            }
        });
    }
});
