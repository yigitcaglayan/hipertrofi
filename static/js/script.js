// Global değişkenler
let currentView = 'front';
let selectedMuscle = null;

// DOM yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

// Uygulamayı başlat
function initializeApp() {
    setupViewToggle();
    setupMuscleInteractions();
    setupPanelClose();
    setupSmoothScroll();
    setupModals();
    setupAuthListeners();
    checkAuth();

    console.log('✓ MuscleFit Pro başlatıldı!');
}

// Görünüm değiştirme butonları
function setupViewToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-btn');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const view = this.getAttribute('data-view');
            switchView(view);

            // Aktif buton stilini güncelle
            toggleButtons.forEach(btn => {
                btn.classList.remove('active');
                // Pasif buton: kırmızı arka plan, beyaz yazı
                btn.style.background = 'linear-gradient(135deg, #e63946 0%, #ff4757 100%)';
                btn.style.color = '#ffffff';
            });

            // Aktif buton: beyaz arka plan, siyah yazı
            this.classList.add('active');
            this.style.background = 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)';
            this.style.color = '#000000';
        });
    });
}

// Görünümü değiştir
function switchView(view) {
    currentView = view;

    const frontView = document.getElementById('frontView');
    const backView = document.getElementById('backView');
    const panel = document.getElementById('exercisePanel');

    // Paneli kapat
    panel.classList.remove('active');
    selectedMuscle = null;

    // Seçili kasları temizle
    document.querySelectorAll('.muscle-area').forEach(muscle => {
        muscle.classList.remove('selected');
    });

    // Görünümü değiştir
    if (view === 'front') {
        frontView.classList.add('active');
        backView.classList.remove('active');
    } else {
        frontView.classList.remove('active');
        backView.classList.add('active');
    }

    console.log(`Görünüm değiştirildi: ${view}`);
}

// Kas etkileşimlerini ayarla
function setupMuscleInteractions() {
    const muscleAreas = document.querySelectorAll('.muscle-area');
    const hoverInfo = document.getElementById('hoverInfo');
    const bodyWrapper = document.querySelector('.body-wrapper');

    muscleAreas.forEach(muscle => {
        // Mouse üzerine geldiğinde
        muscle.addEventListener('mouseenter', function (e) {
            const muscleName = this.getAttribute('data-name');
            hoverInfo.querySelector('.hover-text').textContent = muscleName;
            hoverInfo.classList.add('active');

            // Hover info pozisyonunu ayarla
            updateHoverInfoPosition(e, hoverInfo);
        });

        // Mouse hareket ettiğinde
        muscle.addEventListener('mousemove', function (e) {
            updateHoverInfoPosition(e, hoverInfo);
        });

        // Mouse çıktığında
        muscle.addEventListener('mouseleave', function () {
            hoverInfo.classList.remove('active');
        });

        // Tıklandığında
        muscle.addEventListener('click', function () {
            const muscleId = parseInt(this.getAttribute('data-muscle'));
            const muscleName = this.getAttribute('data-name');

            // Seçili kasları temizle
            muscleAreas.forEach(m => m.classList.remove('selected'));

            // Bu kasları seç
            this.classList.add('selected');

            selectedMuscle = muscleId;
            loadExercises(muscleId, muscleName);

            console.log(`Kas seçildi: ${muscleName} (ID: ${muscleId})`);
        });
    });
}

// Hover info pozisyonunu güncelle
function updateHoverInfoPosition(e, hoverInfo) {
    // Fixed position kullandığımız için direkt client koordinatları
    // CSS'de translate(15px, -50%) var, bu yüzden tam mouse ucunda değil yanında duracak
    hoverInfo.style.left = `${e.clientX}px`;
    hoverInfo.style.top = `${e.clientY}px`;
}

// Egzersizleri yükle
async function loadExercises(muscleId, muscleName) {
    const panel = document.getElementById('exercisePanel');
    const titleElement = document.getElementById('muscleName');
    const listElement = document.getElementById('exerciseList');

    // Panel başlığını ayarla
    titleElement.textContent = `${muscleName} Egzersizleri`;

    // Yükleniyor göster
    listElement.innerHTML = '<div class="loading" style="height: 100px; border-radius: 15px; margin: 1rem 0;"></div>'.repeat(3);

    // Paneli aç
    panel.classList.add('active');

    try {
        // API'den egzersizleri al
        const response = await fetch(`/api/exercises/${muscleId}`);
        const exercises = await response.json();

        // Egzersizleri göster
        displayExercises(exercises);

        console.log(`${exercises.length} egzersiz yüklendi`);
    } catch (error) {
        console.error('Egzersizler yüklenirken hata:', error);
        listElement.innerHTML = '<p style="color: var(--primary-color); text-align: center; padding: 2rem;">Egzersizler yüklenirken bir hata oluştu.</p>';
    }
}

// Egzersizleri göster
function displayExercises(exercises) {
    const listElement = document.getElementById('exerciseList');

    if (exercises.length === 0) {
        listElement.innerHTML = '<p style="color: var(--gray-text); text-align: center; padding: 2rem;">Bu kas grubu için egzersiz bulunamadı.</p>';
        return;
    }

    listElement.innerHTML = '';

    exercises.forEach((exercise, index) => {
        const card = createExerciseCard(exercise, index);
        listElement.appendChild(card);
    });
}

// Egzersiz kartı oluştur
function createExerciseCard(exercise, index) {
    const card = document.createElement('div');
    card.className = 'exercise-card';
    card.style.animationDelay = `${index * 0.1}s`;

    // Zorluk seviyesine göre badge
    const difficultyClass = getDifficultyClass(exercise.difficulty);
    const difficultyText = getDifficultyText(exercise.difficulty);

    // Egzersiz görseli varsa ekle
    const imageHTML = exercise.image_url ? `
        <div class="exercise-image-container">
            <img src="${exercise.image_url}" alt="${exercise.turkish_name}" class="exercise-image" 
                 onerror="this.parentElement.style.display='none'">
        </div>
    ` : '';

    card.innerHTML = `
        ${imageHTML}
        <div class="exercise-header">
            <h4 class="exercise-title">${exercise.turkish_name}</h4>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span class="exercise-badge ${difficultyClass}">${difficultyText}</span>
                <button class="favorite-btn" onclick="toggleFavorite(${exercise.id}, this)" 
                        style="background:none; border:none; cursor:pointer; font-size: 1.2rem; transition: transform 0.2s;" 
                        title="Favorilere Ekle">
                    ${exercise.is_favorite ? '❤️' : '🤍'}
                </button>
            </div>
        </div>
        <p class="exercise-description">${exercise.description || 'Açıklama mevcut değil.'}</p>
        <div class="exercise-meta">
            <span class="meta-item">
                <span>🎯</span>
                <span>Zorluk: ${difficultyText}</span>
            </span>
            <span class="meta-item">
                <span>🏋️</span>
                <span>${exercise.equipment || 'Ekipman belirtilmemiş'}</span>
            </span>
            <span class="meta-item">
                <span>📊</span>
                <span>${exercise.sets || '3 set'}</span>
            </span>
            <span class="meta-item">
                <span>🔢</span>
                <span>${exercise.reps || '10-12 tekrar'}</span>
            </span>
        </div>
    `;

    return card;
}

// Zorluk seviyesi class'ını al
function getDifficultyClass(difficulty) {
    const map = {
        'Başlangıç': 'badge-beginner',
        'Orta': 'badge-intermediate',
        'İleri': 'badge-advanced'
    };
    return map[difficulty] || 'badge-intermediate';
}

// Zorluk seviyesi metnini al
function getDifficultyText(difficulty) {
    const map = {
        'Başlangıç': 'Başlangıç',
        'Orta': 'Orta',
        'İleri': 'İleri Seviye'
    };
    return map[difficulty] || difficulty;
}

// Panel kapatma
function setupPanelClose() {
    const closeBtn = document.getElementById('closePanel');
    const panel = document.getElementById('exercisePanel');

    closeBtn.addEventListener('click', function () {
        panel.classList.remove('active');

        // Seçili kasları temizle
        document.querySelectorAll('.muscle-area').forEach(muscle => {
            muscle.classList.remove('selected');
        });

        selectedMuscle = null;
        console.log('Panel kapatıldı');
    });

    // Panel dışına tıklandığında kapat
    document.addEventListener('click', function (e) {
        if (panel.classList.contains('active') &&
            !panel.contains(e.target) &&
            !e.target.closest('.muscle-area')) {
            panel.classList.remove('active');

            // Seçili kasları temizle
            document.querySelectorAll('.muscle-area').forEach(muscle => {
                muscle.classList.remove('selected');
            });

            selectedMuscle = null;
        }
    });
}

// Smooth scroll
function setupSmoothScroll() {
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
}

// Klavye kısayolları
document.addEventListener('keydown', function (e) {
    // ESC tuşu ile paneli kapat
    if (e.key === 'Escape') {
        const panel = document.getElementById('exercisePanel');
        if (panel.classList.contains('active')) {
            panel.classList.remove('active');

            // Seçili kasları temizle
            document.querySelectorAll('.muscle-area').forEach(muscle => {
                muscle.classList.remove('selected');
            });

            selectedMuscle = null;
        }
    }

    // F tuşu ile ön görünüme geç
    if (e.key === 'f' || e.key === 'F') {
        switchView('front');
        document.querySelector('[data-view="front"]').classList.add('active');
        document.querySelector('[data-view="back"]').classList.remove('active');
    }

    // B tuşu ile arka görünüme geç
    if (e.key === 'b' || e.key === 'B') {
        switchView('back');
        document.querySelector('[data-view="back"]').classList.add('active');
        document.querySelector('[data-view="front"]').classList.remove('active');
    }
});

// Scroll animasyonları
window.addEventListener('scroll', function () {
    const elements = document.querySelectorAll('.step, .feature-item');

    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;

        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
});

// Konsol mesajı
console.log(`
╔═══════════════════════════════════════╗
║         Hipertrofi v1.0              ║
║   İnteraktif Kas Antrenman Rehberi   ║
║                                       ║
║   Klavye Kısayolları:                ║
║   • ESC: Paneli kapat                ║
║   • F: Ön görünüm                    ║
║   • B: Arka görünüm                  ║
╚═══════════════════════════════════════╝
`);

// ---------------- AUTH & FAVORITES LOGIC ---------------- //

let currentUser = null;

async function checkAuth() {
    try {
        const res = await fetch('/api/check_auth');
        const data = await res.json();
        if (data.authenticated) {
            currentUser = data.username;
            updateUIForLogin(true, data.username);
        } else {
            updateUIForLogin(false);
        }
    } catch (e) {
        console.error('Auth check failed', e);
    }
}

function updateUIForLogin(isLoggedIn, username) {
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userGreeting = document.getElementById('user-greeting');
    const usernameDisplay = document.getElementById('username-display');
    const favoritesBtn = document.getElementById('favoritesBtn');

    if (isLoggedIn) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
        userGreeting.style.display = 'block';
        usernameDisplay.textContent = username;
    } else {
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
        userGreeting.style.display = 'none';
        usernameDisplay.textContent = '';
    }
}

function setupModals() {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const favoritesModal = document.getElementById('favoritesModal');

    // Open/Close Handlers
    document.getElementById('loginBtn').onclick = () => loginModal.style.display = 'flex';
    document.getElementById('favoritesBtn').onclick = () => {
        if (!currentUser) {
            showTooltip(document.getElementById('favoritesBtn'), 'Favorilerim için lütfen giriş yapın!');
            setTimeout(() => loginModal.style.display = 'flex', 1500);
            return;
        }
        loadFavorites();
        favoritesModal.style.display = 'flex';
    };

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.onclick = function () {
            this.closest('.modal').style.display = 'none';
        }
    });

    // Switch between Login/Register
    document.getElementById('openRegisterLink').onclick = (e) => {
        e.preventDefault();
        loginModal.style.display = 'none';
        registerModal.style.display = 'flex';
    };
    document.getElementById('openLoginLink').onclick = (e) => {
        e.preventDefault();
        registerModal.style.display = 'none';
        loginModal.style.display = 'flex';
    };

    // Outside click
    window.onclick = (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    };
}

function setupAuthListeners() {
    // Register
    document.getElementById('registerForm').onsubmit = async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;

        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const d = await res.json();
        if (d.success) {
            alert(d.message);
            document.getElementById('registerModal').style.display = 'none';
            document.getElementById('loginModal').style.display = 'flex';
        } else {
            alert(d.message);
        }
    };

    // Login
    document.getElementById('loginForm').onsubmit = async (e) => {
        e.preventDefault();
        const identifier = document.getElementById('loginIdentifier').value;
        const password = document.getElementById('loginPassword').value;

        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const d = await res.json();
        if (d.success) {
            document.getElementById('loginModal').style.display = 'none';
            checkAuth(); // Update UI
        } else {
            alert(d.message);
        }
    };

    // Logout
    document.getElementById('logoutBtn').onclick = async () => {
        if (confirm('Çıkış yapmak istiyor musunuz?')) {
            await fetch('/api/logout', { method: 'POST' });
            currentUser = null;
            updateUIForLogin(false);
            window.location.reload(); // Refresh to clear states
        }
    };
}

async function toggleFavorite(exId, btn) {
    if (!currentUser) {
        showTooltip(btn, 'Giriş yapmanız gerekmektedir!');
        return;
    }

    // Determine current state by icon
    const isFav = btn.innerText === '❤️';

    // Toggle UI immediately (optimistic)
    btn.innerText = isFav ? '🤍' : '❤️';
    btn.style.transform = 'scale(1.2)';
    setTimeout(() => btn.style.transform = 'scale(1)', 200);

    const endpoint = '/api/favorites';
    const method = isFav ? 'DELETE' : 'POST';

    try {
        const res = await fetch(endpoint, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exercise_id: exId })
        });
        const d = await res.json();
        if (!d.success) {
            // Revert if failed
            btn.innerText = isFav ? '❤️' : '🤍';
            alert('Hata oluştu');
        }
    } catch (e) {
        console.error(e);
        btn.innerText = isFav ? '❤️' : '🤍';
    }
}

async function loadFavorites() {
    const list = document.getElementById('favoritesList');
    list.innerHTML = '<div class="loading" style="height: 50px;"></div>';

    const res = await fetch('/api/favorites');
    const favs = await res.json();

    if (favs.length === 0) {
        list.innerHTML = '<p style="color: #bbb; text-align: center; margin-top:2rem;">Listeniz boş. Egzersizlerdeki ❤️ butonuna basarak ekleyebilirsiniz.</p>';
        return;
    }

    list.innerHTML = '';
    favs.forEach((ex, idx) => {
        ex.is_favorite = true; // Favorites list contains favorites
        const card = createExerciseCard(ex, idx);
        list.appendChild(card);
    });
}

function showTooltip(element, message) {
    const tooltip = document.createElement('div');
    tooltip.innerText = message;
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#e63946';
    tooltip.style.color = 'white';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '5px';
    tooltip.style.top = '-40px';
    tooltip.style.left = '50%';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.whiteSpace = 'nowrap';
    tooltip.style.fontSize = '0.9rem';
    tooltip.style.zIndex = '3000';
    tooltip.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';

    // Ensure parent position handles absolute child
    const oldPos = element.style.position;
    if (oldPos !== 'absolute' && oldPos !== 'fixed') {
        element.style.position = 'relative';
    }

    element.appendChild(tooltip);
    setTimeout(() => {
        tooltip.remove();
        element.style.position = oldPos;
    }, 2500);
}
