document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll('.stat-num');

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;

                const updateCount = () => {
                    const target = +counter.getAttribute('data-target');
                    const suffix = counter.getAttribute('data-suffix') || '';
                    let current = +counter.innerText;

                    const increment = Math.ceil(target / 100);

                    if (current < target) {
                        counter.innerText = current + increment;
                        setTimeout(updateCount, 20);
                    } else {
                        counter.innerText = target + suffix;
                    }
                };

                updateCount();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 }); // triggers when 50% visible

    counters.forEach(counter => {
        observer.observe(counter);
    });
});
