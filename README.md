# 📚 Knowledge Base - GitHub Pages & Medium Publisher

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-automated-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Obsidian** notlarınızı otomatik olarak modern bir **GitHub Pages** sitesine ve **Medium**'a dönüştürün.

## ✨ Özellikler

### GitHub Pages Publisher
- 🎨 **Modern Cybersecurity Temalı Tasarım** - Dark mode, neon aksan renkler, terminal estetiği
- 📁 **Çoklu Kategori Desteği** - CTF, CheatSheets, Notes, Research, Blog, Projects...
- 🔄 **Tam Otomatik Deploy** - Push yapın, site güncellensin
- 🖼️ **Obsidian Uyumlu** - `![[image.png]]` formatı otomatik çevrilir
- 📱 **Responsive Tasarım** - Mobil ve masaüstü uyumlu
- ⚡ **Hızlı & Hafif** - Vanilla CSS, framework yok

### Medium Publisher
- 🚀 **Otomatik Draft Oluşturma** - API ile boş draft oluşturulur
- 🤖 **Playwright ile İçerik Yazma** - Headless Chrome ile içerik otomatik yazılır
- 🍪 **Cookie Auth** - Browser cookies ile authentication (API key gerekmez)
- 📋 **Clipboard Fallback** - Otomatik yöntem başarısız olursa panoya kopyalar
- 🔐 **TLS Fingerprinting Bypass** - curl_cffi ile Cloudflare bypass

## 🚀 Desteklenen Dizinler

Script aşağıdaki dizinleri otomatik tarar:

| Dizin | Açıklama |
|-------|----------|
| `TryHackMe/` | TryHackMe CTF writeup'ları |
| `HackTheBox/` | HackTheBox machine writeup'ları |
| `CheatSheets/` | Hızlı referans kılavuzları |
| `Notes/` | Teknik notlar |
| `Research/` | Güvenlik araştırmaları |
| `Blog/` | Blog yazıları |
| `Projects/` | Proje dokümantasyonları |
| `Writeups/` | Genel CTF writeup'ları |

## 📂 Proje Yapısı

```
knowledge-base/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow
├── TryHackMe/
│   └── MachineName/
│       ├── writeup.md          # Obsidian'da yazın
│       └── images/             # Ekran görüntüleri
├── CheatSheets/
│   └── topic.md
├── Notes/
│   └── subject.md
├── scripts/
│   ├── convert_md_to_html.py  # Ana HTML converter script
│   └── medium_publisher.py    # Medium publishing library
├── requirements.txt
├── .gitignore                 # Hassas dosyalar hariç tutulur
└── README.md
```

## 🛠️ Kurulum

### 1. Repo'yu Klonlayın

```bash
git clone https://github.com/onurcangnc/ctf_writeups.git
cd ctf_writeups
```

### 2. Python Bağımlılıklarını Yükleyin

```bash
pip install -r requirements.txt
```

### 3. GitHub Pages Aktifleştirin

1. Repository → Settings → Pages
2. Source: **GitHub Actions**

### 4. Medium Publisher Kurulumu (Opsiyonel)

Medium'a otomatik publish için GitHub Secrets'a şunları ekleyin:

**Gerekli:**
- `MEDIUM_EMAIL` - Medium email adresiniz
- `MEDIUM_PASSWORD` - Medium şifreniz

**2FA kullanıyorsanız (opsiyonel):**
- `GMAIL_REFRESH_TOKEN` - Gmail OAuth refresh token
- `GMAIL_CLIENT_ID` - Google OAuth client ID
- `GMAIL_CLIENT_SECRET` - Google OAuth client secret

> ⚠️ **2FA Setup**: [Google Cloud Console](https://console.cloud.google.com/)'da proje oluşturup Gmail API'yi aktif edin, OAuth credentials alın.

### 5. Yeni Klasör Ekleyin (Opsiyonel)

`convert_md_to_html.py` içindeki `CONFIG` bölümüne yeni dizin ekleyin:

```python
CONFIG = {
    "base_dirs": [
        "TryHackMe",
        "HackTheBox",
        "CheatSheets",
        "YeniKlasorAdi",  # Buraya ekleyin
        ...
    ],
    ...
}
```

## 📝 Kullanım

### GitHub Pages için HTML Convert

```bash
python scripts/convert_md_to_html.py
```

**Otomatik olarak:**
1. ✅ Tüm `.md` dosyaları HTML'e çevrilir
2. ✅ Modern index sayfası oluşturulur
3. ✅ Git'e push yapınca GitHub Actions deploy eder

### Obsidian'da Yazın

```markdown
# CTF Machine Name

## Reconnaissance

Nmap scan results...

![[images/nmap.png]]

## Exploitation

Found vulnerability in...
```

### GitHub'a Push

```bash
git add .
git commit -m "Add new writeup"
git push
```

### Medium Publish

```bash
# CLI ile
python scripts/medium_publisher.py TryHackMe/MachineName/writeup.md --method playwright

# Veya Python içinde
from scripts.medium_publisher import MediumPublisher
publisher = MediumPublisher()
result = publisher.publish("TryHackMe/MachineName/writeup.md", method='playwright')
```

**Publish Methods:**
- `auto` (default): Önce Playwright dener, başarısız olursa clipboard
- `playwright`: Headless Chrome ile otomatik yazar
- `clipboard`: Panoya kopyalar, manuel yapıştırırsınız

## 🔧 Medium Publisher Nasıl Çalışır?

### 1. Draft Oluşturma (API)

```python
# Medium internal API kullanılır
POST https://medium.com/new-story
Headers:
  - X-XSRF-Token: {cookies'tan}
  - X-Client-Date: {timestamp}
Body:
  - visibility: 0 (draft)
```

### 2. İçerik Yazma (Playwright)

```python
# Headless Chrome açılır
# Draft editörü açılır
# İçerik satır satır yazılır
# Ctrl+S ile kaydedilir
```

### 3. Cloudflare Bypass

- `curl_cffi` Chrome TLS fingerprinting taklidi yapar
- Browser cookies ile authentication sağlanır
- API key veya OAuth gerekmez

### Visibility Levels

| Değer | Durum |
|-------|-------|
| `0` | Draft |
| `1` | Public |
| `2` | Unlisted |

## 🎨 Tasarım Özellikleri

- **Dark Theme**: Göz yormayan koyu tema
- **Neon Accent**: `#00ff88` cybersecurity yeşili
- **Grid Background**: Terminal/matrix estetiği
- **Card Layout**: Her writeup için hover efektli kartlar
- **Responsive**: Mobil uyumlu grid sistemi
- **Syntax Highlighting**: Kod blokları için özel stil

## 🔧 Özelleştirme

### Renkleri Değiştirin

`convert_md_to_html.py` içinde CSS değişkenlerini düzenleyin:

```css
:root {
    --accent-primary: #00ff88;    /* Ana vurgu rengi */
    --bg-primary: #0a0a0f;        /* Arka plan */
    ...
}
```

### Kategori İkonlarını Değiştirin

```python
CATEGORY_META = {
    "TryHackMe": {
        "icon": "🎯",
        "description": "TryHackMe CTF writeups"
    },
    ...
}
```

## 🌐 Live Demo

👉 [https://onurcangnc.github.io/ctf_writeups/](https://onurcangnc.github.io/ctf_writeups/)

## 📄 License

MIT License - Özgürce kullanın ve geliştirin.

---

**Made with 💚 by [onurcangnc](https://github.com/onurcangnc)**
