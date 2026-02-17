(function () {
    var navLinks = document.querySelectorAll('.nav-link');
    var currentPath = window.location.pathname;
    var navbar = document.getElementById('siteNavbar');
    var navToggle = document.getElementById('navToggle');
    var mobileNav = document.getElementById('mobileNav');
    var scrollProgress = document.getElementById('scrollProgress');

    navLinks.forEach(function (link) {
        var href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('is-active');
        }
    });

    function applyNavbarScrollState() {
        if (!navbar) {
            return;
        }

        if (window.scrollY > 16) {
            navbar.classList.add('nav-scrolled');
        } else {
            navbar.classList.remove('nav-scrolled');
        }
    }

    if (navToggle && mobileNav) {
        navToggle.addEventListener('click', function () {
            mobileNav.classList.toggle('hidden');
        });
    }

    applyNavbarScrollState();
    window.addEventListener('scroll', applyNavbarScrollState, { passive: true });

    var ticking = false;

    function updateScrollProgress() {
        if (!scrollProgress) {
            return;
        }

        var doc = document.documentElement;
        var scrollTop = doc.scrollTop || document.body.scrollTop;
        var scrollHeight = doc.scrollHeight - doc.clientHeight;
        var progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
        scrollProgress.style.width = progress + '%';
    }

    function onScrollProgress() {
        if (ticking) {
            return;
        }

        ticking = true;
        window.requestAnimationFrame(function () {
            updateScrollProgress();
            ticking = false;
        });
    }

    updateScrollProgress();
    window.addEventListener('scroll', onScrollProgress, { passive: true });
    window.addEventListener('resize', onScrollProgress, { passive: true });

    var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    document.querySelectorAll('main section, footer').forEach(function (el) {
        if (!el.classList.contains('reveal') && !el.classList.contains('detail-fade')) {
            el.classList.add('scroll-fade');
        }
    });

    var cardTargets = document.querySelectorAll('.card-lift');
    cardTargets.forEach(function (card, index) {
        if (!card.classList.contains('reveal') && !card.classList.contains('detail-fade')) {
            card.classList.add('scroll-slide-up');
            card.style.transitionDelay = (Math.min(index % 4, 3) * 45) + 'ms';
        }
    });

    var revealTargets = document.querySelectorAll('.reveal, .scroll-fade, .scroll-slide-up');

    if (prefersReducedMotion) {
        revealTargets.forEach(function (el) {
            el.classList.add('is-visible');
        });
        return;
    }

    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

        revealTargets.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        revealTargets.forEach(function (el) {
            el.classList.add('is-visible');
        });
    }
})();
