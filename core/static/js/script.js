/* ── PAGE NAVIGATION ── */
let currentPage = 'home';
const darkHeroPages = ['home','geotech','faculty','insights','contact','privacy','imprint'];

function goTo(pageId) {
    const pages = {
        'home': '{% url "index" %}',
        'akademie': '{% url "akademie" %}',
        'geotech': '{% url "geotech" %}',
        'faculty': '{% url "faculty" %}',
        'insights': '{% url "insights" %}',
        'contact': '{% url "contact" %}',
        'privacy': '{% url "privacy" %}',
        'imprint': '{% url "imprint" %}'
    };
    window.location.href = pages[pageId];
}

function updateNav() {
  const nav = document.getElementById('mainNav');
  const isDark = darkHeroPages.includes(currentPage);
  // Reset classes then apply
  nav.classList.remove('transparent');
  if (isDark && window.scrollY < 50) nav.classList.add('transparent');
  // Update nav links active state
  document.querySelectorAll('.nav-link, .mob-link').forEach(l => {
    l.classList.remove('active');
    const text = l.textContent.trim().toLowerCase();
    if ((text === 'group' && currentPage === 'home') ||
        (text === currentPage) ||
        (text === 'intelligence' && currentPage === 'insights')) {
      l.classList.add('active');
    }
  });
  // Update logo for scroll state
  updateLogoForScroll();
}

function updateLogoForScroll() {
  const nav = document.getElementById('mainNav');
  const logo = document.getElementById('navLogo').querySelector('path');
  // Keep logo white always for visibility
  logo.setAttribute('fill', '#fff');
}

/* ── SCROLL HANDLER ── */
window.addEventListener('scroll', function() {
  const nav = document.getElementById('mainNav');
  const isDark = darkHeroPages.includes(currentPage);
  if (window.scrollY > 50) {
    nav.classList.add('scrolled');
    nav.classList.remove('transparent');
  } else {
    nav.classList.remove('scrolled');
    if (isDark) nav.classList.add('transparent');
  }
  updateLogoForScroll();
});

/* ── MOBILE MENU ── */
function toggleMob() {
  document.getElementById('mobMenu').classList.toggle('open');
}

/* ── THEME TOGGLE ── */
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  document.getElementById('themeBtn').textContent = next === 'dark' ? '☀' : '☾';
}

/* ── STAT COUNTERS ── */
function initCounters() {
  document.querySelectorAll('.stat-num[data-target]').forEach(el => {
    if (el.dataset.done) return;
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        el.dataset.done = '1';
        const target = parseInt(el.dataset.target);
        const suffix = el.dataset.suffix || '';
        let cur = 0;
        const step = Math.max(1, Math.floor(target / 60));
        const iv = setInterval(() => {
          cur += step;
          if (cur >= target) { el.textContent = target + suffix; clearInterval(iv); }
          else el.textContent = cur + suffix;
        }, 25);
        observer.disconnect();
      }
    }, { threshold: 0.4 });
    observer.observe(el);
  });
}

/* ── TRACK SWITCHING (AKADEMIE) ── */
const trackData = [
  /* Track 1: Energy Leadership */
  { faculty: 'Dr. Romenska · Dr. Neville · Dr. Igbokwe', color: '#2d7038', programmes: [
    { t:'Leadership Spark', d:'5-day intensive rated 5/5 at St Andrews by Renaissance Africa Energy. The anchor programme.', p:'€4,500–€6,500', i:'Dr. Romenska & Dr. Neville' },
    { t:'Social Identity Leadership', d:'How social identities function inside organisations. Original research. Unique to Citadel globally.', p:'€4,500', i:'Dr. Fergus Neville' },
    { t:'The Corridor Leader', d:'Managing across the Africa-Europe divide — culture, regulation, communication, governance.', p:'€5,500', i:'Dr. Neville & Dr. Romenska' },
    { t:'AI-Augmented Leadership', d:'Integrating AI tools into executive decision-making for energy sector leaders.', p:'€4,500', i:'Dr. Igbokwe & Dr. Romenska' },
  ]},
  /* Track 2: Executive Coaching */
  { faculty: 'Dr. Romenska · Dr. Igbokwe', color: '#5a3a8f', programmes: [
    { t:'One-to-One Executive Coaching', d:'Confidential coaching engagements for senior leaders navigating complex transitions, stakeholder pressure, or strategic inflection points.', p:'€6,500–€12,000', i:'Dr. Sandra Romenska' },
    { t:'Coaching for High-Potential Leaders', d:'Structured six-month development cycles for succession candidates and newly-promoted directors.', p:'€4,500–€7,500', i:'Dr. Romenska' },
    { t:'Team Coaching & Alignment', d:'Executive team coaching to accelerate strategy execution, role clarity, and collective decision-making.', p:'€5,500', i:'Dr. Romenska & Dr. Igbokwe' },
    { t:'Coaching Supervision for Internal Coaches', d:'Accreditation-aligned supervision for HR and L&D professionals operating as internal coaches.', p:'€3,500', i:'Dr. Romenska' },
  ]},
  /* Track 3: Geospatial Intelligence & Data Analytics */
  { faculty: 'Dr. Igbokwe · Nnadozie Onyeukwu', color: '#01696f', programmes: [
    { t:'Advanced GIS for Energy Operations', d:'Spatial analysis, decision protocols, engineering applications. Built on 14 publications.', p:'€3,500–€5,000', i:'Dr. Igbokwe' },
    { t:'GeoTech Certified Operator (PROS)', d:'3-day hands-on certification for pipeline route optimisation system operators.', p:'€2,000–€3,500', i:'Dr. Igbokwe & Nnadozie' },
    { t:'UAV / Drone Operations', d:'EASA-compliant drone operations for pipeline surveillance and offshore inspection.', p:'€3,500', i:'Nnadozie Onyeukwu' },
    { t:'GeoAI & Data Analytics', d:'Python, ML, open-source libraries, and cloud platforms for energy spatial problems.', p:'€4,000', i:'Dr. Igbokwe' },
  ]},
  /* Track 4: Oil & Gas Technical */
  { faculty: 'Dr. Onwuegbuchulem · Christian Udogwu', color: '#8a4500', programmes: [
    { t:'Asset Integrity Management', d:'Built on 13 years at Chevron Escravos. Corrosion, flow assurance, PIA 2021 compliance.', p:'€3,000–€4,500', i:'Dr. Onwuegbuchulem' },
    { t:'Offshore Engineering: Full Lifecycle', d:'FEED through commissioning on $8B+ Chevron projects. Real case studies.', p:'€3,500–€5,000', i:'Christian Udogwu' },
    { t:'Process Safety Management', d:'HAZOP, SID reviews, PHA — operational safety for onshore and offshore.', p:'€2,500', i:'Dr. Onwuegbuchulem' },
    { t:'JV Management & Negotiation', d:'Joint venture governance and government relations in the Nigerian oil sector.', p:'€3,000', i:'Christian Udogwu' },
  ]},
  /* Track 5: Bespoke / In-House Training */
  { faculty: 'Dr. Igbokwe · Dr. Romenska · Dr. Neville · Dr. Onwuegbuchulem', color: '#b8860b', programmes: [
    { t:'Diagnostic & Programme Design', d:'A senior-faculty diagnostic that translates your capability gap into a bespoke curriculum — not a catalogue pick.', p:'From €6,500', i:'Dr. Igbokwe & Dr. Romenska' },
    { t:'On-Site Leadership Intensives', d:'Multi-day leadership programmes delivered at your operating base — Lagos, Edinburgh, Münster, or elsewhere on request.', p:'€18,000–€45,000', i:'Dr. Romenska & Dr. Neville' },
    { t:'Blended Technical + Leadership Curricula', d:'Combined technical (asset integrity, GIS, offshore) and leadership modules, sequenced to your operating calendar.', p:'On application', i:'Dr. Onwuegbuchulem & Dr. Igbokwe' },
    { t:'Executive Study Tours (St Andrews)', d:'Curated 5–10 day study tours hosted at the University of St Andrews with industry site visits.', p:'€8,500 per delegate', i:'Faculty team' },
  ]},
];

function switchTrack(idx, btn) {
  document.querySelectorAll('.track-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const track = trackData[idx];
  document.getElementById('trackFaculty').innerHTML = 'Faculty: <span class="gold">' + track.faculty + '</span>';
  const grid = document.getElementById('progGrid');
  grid.innerHTML = track.programmes.map(p =>
    '<div class="prog-card" style="border-top-color:' + track.color + '">' +
      '<h4 class="prog-title">' + p.t + '</h4>' +
      '<p class="prog-instructor">Delivered by ' + p.i + '</p>' +
      '<p class="prog-desc">' + p.d + '</p>' +
      '<p class="prog-price">' + p.p + ' <span>per delegate</span></p>' +
    '</div>'
  ).join('');
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', function() {
  updateNav();
  initCounters();
  switchTrack(0, document.querySelector('.track-tab'));
});
