document.addEventListener('DOMContentLoaded', () => {
    // Lazy Loading Images with Intersection Observer
    const lazyLoadImages = () => {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    };

    lazyLoadImages();

    // Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
        navToggle.setAttribute('aria-expanded', navMenu.classList.contains('active'));
    });

    // Keyboard Navigation for Toggle Button
    navToggle.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            navToggle.click();
        }
    });

    // Smooth Scroll with Throttle
    const throttle = (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });

    // Header Scroll Effect with requestAnimationFrame
    const header = document.querySelector('.main-header');
    let lastScroll = 0;
    let ticking = false;

    const updateHeader = () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }

        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
        ticking = false;
    };

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(updateHeader);
            ticking = true;
        }
    });

    // Form Validation and Submission with Enhanced Error Handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        const formFields = {
            name: document.getElementById('name'),
            email: document.getElementById('email'),
            subject: document.getElementById('subject'),
            message: document.getElementById('message')
        };

        const showError = (element, message) => {
            const errorDiv = element.parentElement.querySelector('.error-message') || 
                           (() => {
                               const div = document.createElement('div');
                               div.className = 'error-message';
                               element.parentElement.appendChild(div);
                               return div;
                           })();
            errorDiv.textContent = message;
            element.setAttribute('aria-invalid', 'true');
            element.classList.add('error');
        };

        const clearError = (element) => {
            const errorDiv = element.parentElement.querySelector('.error-message');
            if (errorDiv) {
                errorDiv.remove();
            }
            element.removeAttribute('aria-invalid');
            element.classList.remove('error');
        };

        const validateField = (element, value, fieldName) => {
            if (!value) {
                showError(element, `${fieldName}を入力してください。`);
                return false;
            }
            clearError(element);
            return true;
        };

        const isValidEmail = (email) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        };

        Object.entries(formFields).forEach(([key, element]) => {
            element.addEventListener('input', () => {
                if (key === 'email' && element.value) {
                    if (!isValidEmail(element.value)) {
                        showError(element, '有効なメールアドレスを入力してください。');
                    } else {
                        clearError(element);
                    }
                } else if (element.value) {
                    clearError(element);
                }
            });
        });

        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            let isValid = true;

            // Validate all fields
            Object.entries(formFields).forEach(([key, element]) => {
                const value = element.value.trim();
                const fieldName = element.previousElementSibling.textContent;
                
                if (key === 'email') {
                    if (!validateField(element, value, fieldName) || !isValidEmail(value)) {
                        isValid = false;
                        if (value && !isValidEmail(value)) {
                            showError(element, '有効なメールアドレスを入力してください。');
                        }
                    }
                } else {
                    if (!validateField(element, value, fieldName)) {
                        isValid = false;
                    }
                }
            });

            if (!isValid) return;

            try {
                const submitButton = contactForm.querySelector('.submit-btn');
                submitButton.disabled = true;
                submitButton.textContent = '送信中...';

                // Here you would typically send the form data to your server
                await simulateFormSubmission();

                // Show success message
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.textContent = 'お問い合わせを受け付けました。担当者より返信させていただきます。';
                successMessage.setAttribute('role', 'alert');
                contactForm.insertAdjacentElement('beforebegin', successMessage);

                // Reset form
                contactForm.reset();
                setTimeout(() => successMessage.remove(), 5000);
            } catch (error) {
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error-message';
                errorMessage.textContent = '送信に失敗しました。時間をおいて再度お試しください。';
                errorMessage.setAttribute('role', 'alert');
                contactForm.insertAdjacentElement('beforebegin', errorMessage);
                setTimeout(() => errorMessage.remove(), 5000);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = '送信する';
            }
        });
    }

    // Animation on Scroll with Intersection Observer
    const observeElements = () => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('.service-card, .resource-card, .news-card').forEach(element => {
            observer.observe(element);
        });
    };

    observeElements();

    // Resource Card Hover Effect with Performance Optimization
    const resourceCards = document.querySelectorAll('.resource-card');
    let isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!isReducedMotion) {
        resourceCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                requestAnimationFrame(() => {
                    card.style.transform = 'translateY(-10px)';
                });
            });

            card.addEventListener('mouseleave', () => {
                requestAnimationFrame(() => {
                    card.style.transform = 'translateY(0)';
                });
            });
        });
    }

    // Helper Functions
    function simulateFormSubmission() {
        return new Promise((resolve) => {
            setTimeout(resolve, 1000);
        });
    }
}); 