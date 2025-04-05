// スムーズスクロール
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 60,
                behavior: 'smooth'
            });
        }
    });
});

// ヘッダーのスクロール制御
let lastScroll = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        header.style.transform = 'translateY(0)';
        return;
    }
    
    if (currentScroll > lastScroll && currentScroll > 60) {
        // スクロールダウン時
        header.style.transform = 'translateY(-100%)';
    } else {
        // スクロールアップ時
        header.style.transform = 'translateY(0)';
    }
    
    lastScroll = currentScroll;
});

// フォーム送信処理
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // フォームデータの取得
        const formData = {
            name: this.querySelector('#name').value,
            email: this.querySelector('#email').value,
            subject: this.querySelector('#subject').value,
            message: this.querySelector('#message').value
        };
        
        // 送信ボタンの状態を変更
        const submitButton = this.querySelector('.submit-button');
        const originalText = submitButton.textContent;
        submitButton.textContent = '送信中...';
        submitButton.disabled = true;
        
        // 実際のAPI呼び出しをシミュレート
        setTimeout(() => {
            alert('お問い合わせありがとうございます。\n内容を確認次第、担当者よりご連絡させていただきます。');
            
            // フォームをリセット
            this.reset();
            
            // ボタンを元の状態に戻す
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }, 1500);
    });
}

// リソースアクセスの制御
document.querySelectorAll('.resource-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        alert('社内システムへのアクセスには認証が必要です。\n社内ネットワークに接続していることをご確認ください。');
    });
});

// 画像の遅延読み込み
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// モバイルメニューの制御
const menuToggle = document.createElement('button');
menuToggle.className = 'menu-toggle';
menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
document.querySelector('.nav-container').prepend(menuToggle);

menuToggle.addEventListener('click', function() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
    this.innerHTML = navMenu.classList.contains('active') ? 
        '<i class="fas fa-times"></i>' : 
        '<i class="fas fa-bars"></i>';
});

// スクロールアニメーション
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.about-item, .service-card, .resource-item, .career-position');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// 初期スタイルの設定
document.querySelectorAll('.about-item, .service-card, .resource-item, .career-position').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
});

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll); 