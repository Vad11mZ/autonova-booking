(function () {
    const form = document.getElementById('booking-form');
    if (!form) return;
    const result = document.getElementById('availability-result');
    const carId = form.dataset.carId;
    const start = form.querySelector('[name="start_date"]');
    const end = form.querySelector('[name="end_date"]');

    async function checkAvailability() {
        if (!start.value || !end.value) return;
        const url = `/api/cars/${carId}/availability?start_date=${start.value}&end_date=${end.value}`;
        try {
            const response = await fetch(url);
            const data = await response.json();
            result.textContent = data.message;
            result.className = `availability-result ${data.available ? 'ok' : 'bad'}`;
        } catch (error) {
            result.textContent = 'Не удалось проверить доступность через API.';
            result.className = 'availability-result bad';
        }
    }

    start.addEventListener('change', checkAvailability);
    end.addEventListener('change', checkAvailability);
})();
