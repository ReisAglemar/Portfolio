/**
 * Portfólio Aglemar Reis - JavaScript Interativo & Fluido
 * Recursos:
 * - Scroll Reveal com IntersectionObserver e verificação de viewport imediata
 * - Navegação ativa dinâmica (ScrollSpy)
 * - Header fixo com efeito glassmorphism ao rolar
 * - Botão flutuante "Voltar ao Topo"
 * - Feedback interativo no formulário de contato
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    initHeaderScroll();
    initScrollSpy();
    initBackToTop();
    initFormFeedback();
});

/**
 * 1. Animação de revelação suave (Scroll Reveal) segura e imediata
 */
function initScrollReveal() {
    // Sinaliza que o JS foi carregado para ativar as transições sem travar o conteúdo
    document.documentElement.classList.add('js-ready');

    // Seleciona todos os elementos relevantes tanto do index.html quanto do agora.html
    const revealElements = document.querySelectorAll(
        '.reveal, .secao, .detail-card, .blueprint-wrapper, .agora-hero, .intro figure, .intro #nome, .intro #descricao, .intro #menu, .container-footer form'
    );

    const revealItem = (el) => {
        el.classList.add('revealed');
    };

    revealElements.forEach((el, index) => {
        el.classList.add('reveal');
        el.style.setProperty('--reveal-delay', `${(index % 3) * 0.08}s`);

        // Se o elemento já está na tela ou muito perto ao carregar, revela logo sem esperar scroll
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight + 80) {
            revealItem(el);
        }
    });

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting || entry.boundingClientRect.top < window.innerHeight + 50) {
                    revealItem(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            root: null,
            threshold: 0.01,
            rootMargin: '80px 0px 80px 0px'
        });

        revealElements.forEach(el => {
            if (!el.classList.contains('revealed')) {
                observer.observe(el);
            }
        });
    } else {
        // Fallback imediato se o navegador não suportar IntersectionObserver
        revealElements.forEach(revealItem);
    }

    // Garantia absoluta: revela qualquer elemento que possa ter ficado para trás
    setTimeout(() => {
        revealElements.forEach(revealItem);
    }, 500);
}

/**
 * 2. Adiciona efeito glassmorphism e sombra ao rolar a página
 */
function initHeaderScroll() {
    const headerNav = document.querySelector('.header-nav');
    if (!headerNav) return;

    const handleScroll = () => {
        if (window.scrollY > 40) {
            headerNav.classList.add('nav-scrolled');
        } else {
            headerNav.classList.remove('nav-scrolled');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}

/**
 * 3. ScrollSpy: Destaca o link de navegação conforme a seção visível
 */
function initScrollSpy() {
    const sections = document.querySelectorAll('header#header, section#conhecimentos, section#projetos, footer#footer');
    const navLinks = document.querySelectorAll('.header-nav ul li a[href^="#"], .header-nav ul li a[href="index.html"]');

    if (!sections.length || !navLinks.length) return;

    const updateActiveLink = () => {
        const scrollPosition = window.scrollY + 180;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    if (
                        (href === `#${sectionId}`) ||
                        (sectionId === 'header' && (href === 'index.html' || href === '#header'))
                    ) {
                        link.classList.add('active-nav');
                    } else if (href.startsWith('#') || href === 'index.html') {
                        link.classList.remove('active-nav');
                    }
                });
            }
        });
    };

    window.addEventListener('scroll', updateActiveLink, { passive: true });
    updateActiveLink();
}

/**
 * 4. Botão Voltar ao Topo flutuante e dinâmico
 */
function initBackToTop() {
    if (document.getElementById('back-to-top')) return;

    const button = document.createElement('button');
    button.id = 'back-to-top';
    button.setAttribute('aria-label', 'Voltar ao topo');
    button.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
    `;
    document.body.appendChild(button);

    const toggleButton = () => {
        if (window.scrollY > 350) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    };

    window.addEventListener('scroll', toggleButton, { passive: true });

    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * 5. Feedback visual no formulário de envio
 */
function initFormFeedback() {
    const form = document.querySelector('#form-contato');
    if (!form) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    const status = form.querySelector('#form-status');
    const textoOriginal = submitBtn ? submitBtn.textContent : '';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.textContent = 'Enviando...';
        status.textContent = '';

        try {
            const resposta = await fetch(form.action, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(Object.fromEntries(new FormData(form)))
            });
            const dados = await resposta.json().catch(() => ({}));
            status.textContent = dados.mensagem || (resposta.ok ? 'Mensagem enviada!' : 'Erro ao enviar.');
            if (resposta.ok) form.reset();
        } catch {
            status.textContent = 'Sem conexão. Tente novamente.';
        } finally {
            submitBtn.disabled = false;
            submitBtn.style.opacity = '';
            submitBtn.textContent = textoOriginal;
        }
    });
}
