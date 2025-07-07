console.log("JavaScript file is connected and running!");
// JavaScript for the watch showcase page
// Real-time clock functionality
// Real-time analog watch functionality
function updateClock() {
    const now = new Date();
    const hours = now.getHours() % 12;
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();

    const hourAngle = (hours * 30) + (minutes * 0.5);
    const minuteAngle = minutes * 6;
    const secondAngle = seconds * 6;

    document.getElementById('hourHand').style.transform = `rotate(${hourAngle}deg)`;
    document.getElementById('minuteHand').style.transform = `rotate(${minuteAngle}deg)`;
    document.getElementById('secondHand').style.transform = `rotate(${secondAngle}deg)`;
}

// Call initially and every second
setInterval(updateClock, 1000);
updateClock();

// Smooth scrolling for nav links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Fade-in animation on scroll using IntersectionObserver
const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply observer to each watch showcase
document.querySelectorAll('.watch-showcase').forEach((showcase, index) => {
    showcase.style.opacity = '0';
    showcase.style.transform = 'translateY(50px)';
    showcase.style.transition = `opacity 0.8s ease ${index * 0.2}s, transform 0.8s ease ${index * 0.2}s`;
    observer.observe(showcase);
});

console.log("JavaScript file is connected and running!");
