# Obsidian to Medium Publisher

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-automated-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Obsidian** yazılarınızı otomatik olarak **Medium** draft'larına dönüştürün. CTF writeup'ları, blog yazıları, notlarınızı tek bir komutla yayınlayın.

## Özellikler

- **Frontmatter ile seçici publishing** - Sadece istediğiniz yazıları yayınlayın
- **Takip mekanizması** - Aynı içeriği tekrar göndermez, değişiklikleri algılar
- **Obsidian resim link desteği** - `![[resim.png]]` formatını otomatik dönüştürür
- **GitHub Actions entegrasyonu** - Push yapın, otomatik Medium draft oluştursun
- **GitHub Pages deploy** - Statik site olarak da yayınlayın
- **Interaktif CLI** - Değişikliklerde onay ister

## Kullanım Alanları

- **CTF Writeup'ları** - TryHackMe, HackTheBox çözümlerinizi dokümante edin
- **Blog Yazarlığı** - Obsidian'da yazın, Medium'da yayınlayın
- **Teknik Notlar** - Geliştirme notlarınızı paylaşın
- **Akademik Yazılar** - Araştırma notlarınızı draft olarak saklayın

## Teknolojiler

| Teknoloji | Kullanım Amacı |
|-----------|----------------|
| **Python 3.11+** | Ana scripting dili |
| **PyYAML** | Frontmatter parsing |
| **markdown2** | Markdown → HTML dönüşümü |
| **requests** | Medium API iletişimi |
| **GitHub Actions** | CI/CD otomasyonu |
| **GitHub Pages** | Statik site hosting |
| **Obsidian** | Markdown editörü (client side) |

## Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/onurcangnc/ctf_writeups.git
cd ctf_writeups
```

### 2. Python Bağımlılıkları

```bash
pip install -r requirements.txt
```

### 3. Medium Integration Token Alın

1. [Medium Settings](https://medium.com/me/settings) → Integration Tokens
2. "Get integration token" → İsim verin → Token'ı kopyalayın

### 4. GitHub Secret Ekleyin

GitHub repo → Settings → Secrets and variables → Actions → New repository secret

```
Name: MEDIUM_TOKEN
Value: your_medium_integration_token_here
```

## Kullanım

### Frontmatter Ekleyin

Obsidian'da yazınızın başına ekleyin:

```yaml
---
title: Makale Başlığı
tags: [etiket1, etiket2, etiket3]
publish-medium: true
---
```

### Yerel Çalıştırma

```bash
python publish_to_medium.py
```

### Otomatik Mod (GitHub Actions)

```bash
git add .
git commit -m "Yeni yazı eklendi"
git push
```

Her push'ta otomatik olarak:
1. ✅ GitHub Pages'e deploy
2. ✅ Medium'a draft gönder

## Proje Yapısı

```
ctf_writeups/
├── .github/
│   └── workflows/
│       ├── deploy-and-update-index.yml  # GitHub Pages deploy
│       └── publish_to_medium.yml         # Medium publish
├── TryHackMe/
│   ├── ChallengeName/
│   │   ├── writeup.md                   # Obsidian'da yazın
│   │   └── images/                      # Resimler
│   └── ...
├── publish_to_medium.py                 # Ana script
├── convert_md_to_html.py                # Markdown → HTML
├── published_posts.json                 # Takip dosyası (auto)
└── requirements.txt                     # Python bağımlılıkları
```

## Frontmatter Seçenekleri

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| `title` | Hayır | Yazı başlığı (yoksa H1'den alınır) |
| `tags` | Hayır | Medium tag'leri (max 5) |
| `publish-medium` | **Evet** | `true` olanlar yayınlanır |

## Workflow'lar

### 1. Deploy & Update Index

Her push'ta:
- `TryHackMe/*/` altındaki `.html` dosyalarını bulur
- `index.html`'i günceller
- GitHub Pages'e deploy eder

### 2. Publish to Medium

Her push'ta (`published_posts.json` hariç):
- `publish-medium: true` olan `.md` dosyalarını bulur
- Değişiklik kontrolü yapar
- Medium'a draft gönderir
- `published_posts.json`'i günceller

## Örnek Çıktı

```
==================================================
CTF Writeups - Medium Publisher v2.0
==================================================

Medium API'ye bağlanılıyor...
Bağlandı: User ID = 1b073698e93a... (gizlendi)

1 adet publishable yazı bulundu:
  [YENİ] Test

1 yazı gönderilecek:
  - Test

Devam etmek istiyor musunuz? [y/N]: y
==================================================
Dizin: Test
==================================================
  İşleniyor: ---.md
  ✓ SUCCESS: Draft oluşturuldu!
     URL: https://medium.com/@user/c8df4f32003e
==================================================
Tamamlandı! 1/1 işlem başarılı.
==================================================
```

## Contributing

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## License

MIT License - kendi projenizde özgürce kullanın.

## Inspirations

- [Obsidian](https://obsidian.md) - Powerful markdown editor
- [Medium API](https://github.com/Medium/medium-api-docs) - Publishing platform
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation

---

**Not:** Bu proje originally CTF writeup'ları için geliştirilmiştir ancak **herhangi bir Obsidian → Medium otomasyonu** için kullanılabilir.
