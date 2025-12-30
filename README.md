# 📚 Knowledge Base - GitHub Pages Publisher

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-automated-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Obsidian** notlarınızı otomatik olarak modern, profesyonel bir **GitHub Pages** sitesine dönüştürün.

## ✨ Özellikler

- 🎨 **Modern Cybersecurity Temalı Tasarım** - Dark mode, neon aksan renkler, terminal estetiği
- 📁 **Çoklu Kategori Desteği** - CTF, CheatSheets, Notes, Research, Blog, Projects...
- 🔄 **Tam Otomatik Deploy** - Push yapın, site güncellensin
- 🖼️ **Obsidian Uyumlu** - `![[image.png]]` formatı otomatik çevrilir
- 📱 **Responsive Tasarım** - Mobil ve masaüstü uyumlu
- ⚡ **Hızlı & Hafif** - Vanilla CSS, framework yok

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
├── convert_md_to_html.py       # Ana converter script
├── requirements.txt
└── README.md
```

## 🛠️ Kurulum

### 1. Repo'yu Klonlayın

```bash
git clone https://github.com/onurcangnc/ctf_writeups.git
cd ctf_writeups
```

### 2. GitHub Pages Aktifleştirin

1. Repository → Settings → Pages
2. Source: **GitHub Actions**

### 3. Yeni Klasör Ekleyin (Opsiyonel)

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

### Obsidian'da Yazın

```markdown
# CTF Machine Name

## Reconnaissance

Nmap scan results...

![[images/nmap.png]]

## Exploitation

Found vulnerability in...
```

### Push Yapın

```bash
git add .
git commit -m "Add new writeup"
git push
```

**Otomatik olarak:**
1. ✅ Tüm `.md` dosyaları HTML'e çevrilir
2. ✅ Modern index sayfası oluşturulur
3. ✅ GitHub Pages'e deploy edilir

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