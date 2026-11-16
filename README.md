 <div align="center">

  <img src="resources/images/logo.png" alt="Lexora Logo" width="120" height="120">

  # Lexora

  **Translate Documents. Preserve Formatting.**

  *Belgelerinizi çevirin, biçimlendirmelerini koruyun.*

  [![Release](https://img.shields.io/badge/Release-v1.0.1-blue.svg)](https://github.com/EnginArslan49/lexora-offline-document-translator/releases/tag/v1.0.1)
  [![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/)
  [![PySide6](https://img.shields.io/badge/PySide6-6.7.3-brightgreen.svg)](https://pypi.org/project/PySide6/)
  [![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-lightgrey.svg)](https://www.microsoft.com/windows)

</div>

---

## 📖 Lexora Hakkında

**Lexora**, Windows 10 ve Windows 11 işletim sistemleri için geliştirilmiş, tamamen ücretsiz ve çevrimdışı çalışabilen profesyonel bir belge çeviri uygulamasıdır.

TXT ve DOCX formatındaki belgelerinizi farklı dillere çevirirken orijinal belge yapısını ve biçimlendirmelerini mümkün olduğunca korumayı hedefler. Yazı tipleri, yazı renkleri, kalın ve italik metinler, tablolar, paragraflar ve diğer belge bileşenleri çeviri sürecinde korunacak şekilde tasarlanmıştır.

Lexora, çeviri işlemlerinde açık kaynaklı **Argos Translate** teknolojisini kullanır. Ücretli API, abonelik veya kullanıcı hesabı gerektirmez. İhtiyaç duyulan dil paketleri bir kez indirildikten sonra çeviri işlemleri internet bağlantısı olmadan doğrudan bilgisayarınızda gerçekleştirilir.

### Temel yaklaşım

- Ücretsiz ve erişilebilir belge çevirisi.
- İnternet bağlantısına bağımlı olmayan çalışma.
- Orijinal belge biçimlendirmesini koruma.
- Kullanıcı dosyalarının güvenliğini ön planda tutma.
- Modern, anlaşılır ve tamamen Türkçe kullanıcı arayüzü.

> **Geliştirici:** Engin ARSLAN | Software Developer

---

## ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
| :--- | :--- |
| **DOCX Biçimlendirme Koruması** | Word belgelerindeki yazı tipi, renk, kalınlık, italik, tablolar ve paragraf yapısını korumayı hedefler. |
| **TXT ve DOCX Desteği** | Metin ve Microsoft Word belgelerini çevirebilir. |
| **Tamamen Ücretsiz** | API ücreti, abonelik veya kullanıcı hesabı gerektirmez. |
| **Çevrimdışı Çeviri** | Dil paketleri indirildikten sonra internet bağlantısı olmadan çalışır. |
| **Otomatik Dil Algılama** | Lingua kütüphanesi ile kaynak dilin otomatik tespit edilmesini sağlar. |
| **Modern Arayüz** | PySide6 ile geliştirilmiş, macOS tasarım anlayışından esinlenen özel pencere yapısı sunar. |
| **Açık ve Koyu Tema** | Kullanıcı tercihine göre değiştirilebilen iki farklı görünüm sunar. |
| **Güvenli Dosya İşlemleri** | Kaynak dosyaları değiştirmeden çıktı oluşturur ve atomik dosya yazma yaklaşımını kullanır. |
| **ZIP Bomb Koruması** | DOCX dosyalarındaki kötü amaçlı sıkıştırma saldırılarına karşı doğrulama mekanizmaları içerir. |
| **Çeviri Geçmişi** | Önceki çeviri işlemlerini yerel JSON tabanlı depolamada saklar. |
| **İşlem İptali** | Uzun süren çeviri işlemlerinin arayüzü dondurmadan iptal edilmesini destekler. |

---

# 🚀 1. Son Kullanıcılar İçin

Bu bölüm, Lexora'yı yalnızca bilgisayarına indirip kullanmak isteyen kullanıcılar için hazırlanmıştır.

Python, Git veya herhangi bir yazılım geliştirme bilgisine ihtiyacınız yoktur.

## 1.1. Uygulamayı İndirin

Lexora'nın güncel sürümüne GitHub Releases sayfasından ulaşabilirsiniz.

**[Lexora – Güncel Sürümü İndir](https://github.com/EnginArslan49/lexora-offline-document-translator/releases/latest)**

1. Yukarıdaki bağlantıyı açın.
2. İlgili sürümün **Assets** bölümünü bulun.
3. `Lexora_Setup_1.0.1.exe` kurulum dosyasını indirin.

## 1.2. Uygulamayı Kurun

1. İndirdiğiniz `Lexora_Setup_1.0.1.exe` dosyasına çift tıklayın.
2. Windows güvenlik uyarısı görüntülenirse dosyanın kaynağını ve dijital imza durumunu kontrol edin.
3. Türkçe kurulum sihirbazındaki adımları takip edin.
4. Kurulum tamamlandığında Lexora'yı masaüstü veya Başlat menüsündeki kısayoldan açın.

## 1.3. Dil Paketlerini İndirin

**Önemli:** Lexora çevrimdışı çalıştığı için ihtiyaç duyduğunuz çeviri modellerini ilk kullanımda indirmeniz gerekir.

Bu işlem yalnızca dil paketini bilgisayarınıza yüklemek için internet bağlantısı gerektirir.

1. Lexora uygulamasını açın.
2. Sol menüden **Ayarlar** sekmesine girin.
3. Dil Paketi Yönetimi bölümünü bulun.
4. İhtiyacınız olan kaynak ve hedef dil paketini seçin.

   Örnek: İngilizce → Türkçe

5. **İndir ve Kur** butonuna basın.
6. İndirme ve kurulum işleminin tamamlanmasını bekleyin.

Dil paketleri yüklendikten sonra belgelerinizi internet bağlantısı olmadan çevirebilirsiniz.

## 1.4. Belge Çevirisi Yapın

1. Ana ekrandan çevirmek istediğiniz TXT veya DOCX dosyasını seçin.
2. Kaynak ve hedef dil ayarlarınızı kontrol edin.
3. Çeviri işlemini başlatın.
4. İşlem tamamlandığında oluşturulan çıktı dosyasını kaydedin.

**Not:** Çeviri kalitesi kullanılan dil modeline ve kaynak metnin niteliğine bağlıdır. Özellikle teknik, hukuki ve akademik belgelerde sonuçların kontrol edilmesi önerilir.

---

# 💻 2. Geliştiriciler İçin

Lexora açık kaynaklı bir projedir. Kaynak kodunu inceleyebilir, geliştirebilir, hata bildiriminde bulunabilir veya kendi bilgisayarınızda çalıştırabilirsiniz.

Bu bölüm, projeyi sıfırdan bilgisayarına indirmek ve kaynak kod üzerinden çalıştırmak isteyen geliştiriciler için hazırlanmıştır.

## 2.1. Gerekli Yazılımlar

Projeyi geliştirme ortamında çalıştırabilmek için aşağıdaki yazılımlara ihtiyacınız vardır.

| Yazılım | Gereksinim | Açıklama |
| :--- | :--- | :--- |
| Python | 3.12 veya üzeri | Projenin ana programlama dili |
| Git | Güncel sürüm | Kaynak kodu GitHub üzerinden indirmek için |
| pip | Python ile birlikte gelir | Python paketlerini yüklemek için |
| Inno Setup 6 | İsteğe bağlı | Windows kurulum dosyası oluşturmak için |

İndirme bağlantıları:

- [Python İndir](https://www.python.org/downloads/)
- [Git İndir](https://git-scm.com/downloads)
- [Inno Setup 6 İndir](https://jrsoftware.org/isinfo.php)

## 2.2. Projeyi Bilgisayarınıza İndirin

Öncelikle Git'in bilgisayarınızda kurulu olduğundan emin olun.

Windows PowerShell veya terminal açarak aşağıdaki komutları çalıştırın:

```bash
# Lexora kaynak kodlarını GitHub üzerinden bilgisayarınıza indirin.
git clone https://github.com/EnginArslan49/lexora-offline-document-translator.git

# Proje klasörüne geçiş yapın.
cd lexora-offline-document-translator
```

Bu işlem tamamlandığında projenin kaynak kodları bilgisayarınızda bulunacaktır.

## 2.3. Sanal Ortam Oluşturun

Python projelerinde sanal ortam kullanmak, projenin bağımlılıklarını sistemdeki diğer Python projelerinden ayırır.

Bu sayede farklı projelerde kullanılan kütüphane sürümlerinin birbirleriyle çakışması önlenir.

```powershell
# Proje için bağımsız bir Python sanal ortamı oluşturun.
python -m venv .venv

# Sanal ortamı Windows PowerShell üzerinde etkinleştirin.
.\.venv\Scripts\Activate.ps1
```

PowerShell komut dosyası çalıştırma politikası nedeniyle aktivasyon engellenirse mevcut terminal oturumu için aşağıdaki komutu kullanabilirsiniz:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Sanal ortamı yeniden etkinleştirin.
.\.venv\Scripts\Activate.ps1
```

## 2.4. Gerekli Kütüphaneleri Yükleyin

Projenin ihtiyaç duyduğu Python kütüphaneleri `requirements.txt` dosyasında tanımlanmıştır.

```bash
# Projenin bağımlılıklarını yükleyin.
python -m pip install -r requirements.txt
```

Kurulum tamamlandığında gerekli Python paketleri sanal ortamınıza yüklenmiş olacaktır.

## 2.5. Uygulamayı Çalıştırın

Gerekli bağımlılıkları yükledikten sonra uygulamayı doğrudan kaynak kod üzerinden başlatabilirsiniz.

```bash
# Lexora masaüstü uygulamasını başlatın.
python app.py
```

Uygulama başarıyla açıldığında geliştirme ortamınız kullanıma hazırdır.

---

# 📁 3. Proje Klasör Yapısı

Lexora, sorumlulukları birbirinden ayrılmış modüler bir proje yapısıyla geliştirilmiştir.

Aşağıdaki yapı, projenin temel bileşenlerini ve kullanım amaçlarını açıklamaktadır.

```text
lexora-offline-document-translator/
│
├── app.py
│   └── Uygulamanın başlangıç noktası.
│
├── requirements.txt
│   └── Python bağımlılıkları.
│
├── lexora.spec
│   └── PyInstaller derleme yapılandırması.
│
├── installer/
│   └── Windows kurulum paketi yapılandırmaları.
│
├── resources/
│   ├── images/
│   │   └── Uygulama logo ve görselleri.
│   │
│   └── Diğer uygulama kaynakları.
│
├── tests/
│   └── Otomatik test dosyaları.
│
├── README.md
│   └── Proje dokümantasyonu.
│
├── LICENSE
│   └── MIT lisans metni.
│
└── .gitignore
    └── Git tarafından takip edilmeyecek dosyalar.
```

> **Not:** Bu liste projenin temel bileşenlerini göstermektedir. Gerçek klasör ve dosya yapısı, GitHub deposundaki güncel kaynak kod üzerinden incelenebilir.

---

# 🛠️ 4. Teknik Özellikler ve Kullanılan Teknolojiler

Lexora, masaüstü uygulama geliştirme, doğal dil işleme ve belge işleme teknolojileri kullanılarak geliştirilmiştir.

| Teknoloji | Kullanım Amacı |
| :--- | :--- |
| **Python 3.12** | Ana programlama dili |
| **PySide6 (Qt 6)** | Masaüstü kullanıcı arayüzü |
| **Argos Translate** | Çevrimdışı nöral makine çevirisi |
| **Lingua** | Otomatik kaynak dil algılama |
| **python-docx** | Microsoft Word belgelerini okuma ve yazma |
| **lxml** | XML ve OOXML belge yapılarının işlenmesi |
| **JSON** | Yerel ayarlar ve çeviri geçmişinin saklanması |
| **PyInstaller** | Python uygulamasını çalıştırılabilir EXE dosyasına dönüştürme |
| **Inno Setup 6** | Windows kurulum paketi oluşturma |
| **pytest** | Otomatik yazılım testleri |

## 4.1. Belge Biçimlendirme Mimarisi

DOCX belgeleri, yalnızca metinlerden oluşmaz. İçerisinde farklı biçimlendirme özellikleri, tablolar, paragraflar ve XML tabanlı belge bileşenleri bulunur.

Lexora, belge yapısını korumak amacıyla `python-docx` ve doğrudan OOXML manipülasyonu sağlayan `lxml` teknolojilerinden yararlanır.

Bu yaklaşım sayesinde çeviri sırasında orijinal belgenin biçimsel özelliklerinin korunması hedeflenir.

## 4.2. Çevrimdışı Çeviri Mimarisi

Çeviri işlemlerinde Argos Translate kullanılır.

Dil modelleri bilgisayara indirildikten sonra çeviri işlemleri yerel ortamda gerçekleştirilir. Böylece her çeviri işleminde harici bir API servisine veya internet bağlantısına ihtiyaç duyulmaz.

## 4.3. Veri Saklama

Lexora, kullanıcı ayarlarını ve çeviri geçmişini JSON tabanlı yerel dosyalarda saklar.

Bu mimari sayesinde uygulama için ayrıca bir veritabanı sunucusu kurulmasına gerek kalmaz.

---

# 🧪 5. Otomatik Testleri Çalıştırma

Lexora'nın test süreçlerinde `pytest` kullanılmaktadır.

Testler; dosya işleme, DOCX güvenliği, JSON veri kalıcılığı ve dil algılama gibi önemli bileşenleri kapsar.

Proje klasöründe sanal ortam etkin durumdayken aşağıdaki komutu çalıştırın:

```bash
# Projedeki otomatik testleri çalıştırın.
pytest
```

Testlerin daha ayrıntılı sonuçlarını görmek için:

```bash
# Testleri ayrıntılı çıktı ile çalıştırın.
pytest -v
```

**Önerilen test senaryoları:**

- Geçerli ve boş TXT dosyalarının işlenmesi.
- Geçerli DOCX dosyalarının çevrilmesi.
- Bozuk veya geçersiz DOCX dosyalarının reddedilmesi.
- Aşırı sıkıştırılmış veya şüpheli ZIP içeriklerinin kontrol edilmesi.
- JSON ayarlarının ve çeviri geçmişinin kalıcılığı.
- Desteklenmeyen dil çiftlerinin yönetimi.
- Çeviri işleminin iptal edilmesi.
- Çıktı dosyası oluşturulurken oluşabilecek yazma hatalarının yönetimi.

---

# 📦 6. Kaynak Koddan EXE ve Setup.exe Oluşturma

Lexora'yı kendi kaynak kodunuz üzerinden derleyerek başka bilgisayarlarda kullanılabilecek Windows uygulama dosyaları oluşturabilirsiniz.

Bu bölüm, kendi Lexora sürümünü oluşturmak isteyen geliştiriciler içindir.

## 6.1. Derleme Ön Koşulları

İşleme başlamadan önce:

- Python 3.12 veya üzeri kurulu olmalıdır.
- Proje bağımlılıkları yüklenmiş olmalıdır.
- PyInstaller kurulu olmalıdır.
- Setup.exe oluşturmak için Inno Setup 6 kurulu olmalıdır.

PyInstaller kurulu değilse:

```bash
# PyInstaller paketini yükleyin.
python -m pip install pyinstaller==6.11.1
```

## 6.2. Taşınabilir EXE Oluşturma

Proje ana dizininde aşağıdaki komutu çalıştırın:

```bash
# lexora.spec yapılandırmasını kullanarak uygulamayı derleyin.
pyinstaller lexora.spec --noconfirm
```

Derleme işlemi tamamlandığında uygulamanın EXE dosyaları, `lexora.spec` yapılandırmasında belirtilen çıktı klasöründe oluşturulur.

## 6.3. Windows Kurulum Dosyası (Setup.exe) Oluşturma

Taşınabilir uygulamayı bir Windows kurulum paketine dönüştürmek için Inno Setup 6 kullanılır.

Inno Setup'ın varsayılan kurulum dizini kullanılıyorsa PowerShell üzerinden şu komutu çalıştırın:

```powershell
# Inno Setup Compiler ile kurulum dosyasını oluşturun.
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\lexora_setup.iss"
```

Inno Setup farklı bir dizine kurulduysa komuttaki `ISCC.exe` yolunu kendi bilgisayarınıza göre güncelleyin.

Derleme tamamlandığında kurulum dosyası, `installer\lexora_setup.iss` içerisinde tanımlanan çıktı dizininde oluşturulur.

**Önemli:** EXE ve Setup.exe dosyalarının çıktı konumları ile dosya adları, kullanılan derleme yapılandırmalarına bağlıdır. Bu nedenle `lexora.spec` ve `lexora_setup.iss` dosyalarındaki ayarları kontrol edin.

---

# 🔒 7. Güvenlik ve Veri Koruma

Lexora geliştirilirken kullanıcı dosyalarının güvenliği ve veri bütünlüğü dikkate alınmıştır.

Öne çıkan güvenlik yaklaşımları:

- **Kaynak Dosya Koruması:** Çeviri işlemleri sırasında orijinal dosyanın değiştirilmemesi hedeflenir.
- **Atomik Dosya Yazma:** Çıktı dosyalarının geçici dosya üzerinden oluşturulması ve işlem tamamlandığında hedef konuma aktarılması yaklaşımı kullanılır.
- **ZIP Bomb Kontrolü:** DOCX dosyalarının ZIP tabanlı yapısında kötü amaçlı sıkıştırma içeriklerine karşı kontroller uygulanır.
- **Yerel İşleme:** Çeviriler, dil paketleri yüklendikten sonra bilgisayar üzerinde gerçekleştirilir.
- **Veri Gizliliği:** Çeviri işlemleri için ücretli üçüncü taraf API hizmetlerine ihtiyaç duyulmaz.

> Çevrimdışı çalışma, uygulamanın bütün güvenlik risklerinden tamamen arındırıldığı anlamına gelmez. Bilinmeyen kaynaklardan edinilen belgelerin açılmadan önce kontrol edilmesi önerilir.

---

# 🤝 8. Açık Kaynak ve Katkıda Bulunma

Lexora, geliştiricilerin inceleyebileceği ve katkıda bulunabileceği açık kaynaklı bir projedir.

Projeyi geliştirmek, hata bildirmek veya yeni özellik önerilerinde bulunmak isteyen kullanıcılar GitHub deposunu ziyaret edebilir.

**Katkıda bulunmak için:**

1. Projeyi GitHub üzerinden Fork edin.
2. Kendi geliştirme ortamınızda değişikliklerinizi gerçekleştirin.
3. Yeni özellikler için gerekli testleri ekleyin.
4. Değişikliklerinizi test edin.
5. GitHub üzerinden Pull Request oluşturun.

Hata bildirimleri ve özellik önerileri için:

**[GitHub Issues – Hata Bildir ve Öneri Gönder](https://github.com/EnginArslan49/lexora-offline-document-translator/issues)**

---

# 👨‍💻 9. Geliştirici ve İletişim

**Engin ARSLAN**  
Software Developer

Lexora, tamamen ücretsiz olarak geliştirilen ve kullanıma sunulan bir yazılım projesidir.

Diğer yazılım projelerimi, eğitim içeriklerimi ve çalışmalarımı aşağıdaki platformlardan takip edebilirsiniz.

| Platform | Bağlantı |
| :--- | :--- |
| **GitHub** | [@EnginArslan49](https://github.com/EnginArslan49) |
| **LinkedIn** | [Engin ARSLAN](https://www.linkedin.com/) |
| **YouTube** | [@ramkafe](https://www.youtube.com/@ramkafe) |
| **Instagram** | [@49engn04](https://www.instagram.com/49engn04/) |

---

# 📜 10. Lisans

Lexora, **MIT Lisansı** altında açık kaynak olarak sunulmaktadır.

Projeyi kullanabilir, inceleyebilir, değiştirebilir ve lisans koşullarına uygun şekilde dağıtabilirsiniz.

Detaylı bilgi için proje içerisindeki [LICENSE](LICENSE) dosyasını inceleyebilirsiniz.

Ayrıca Argos Translate, PySide6 ve projede kullanılan diğer üçüncü taraf kütüphanelerin kendi lisans koşulları geçerlidir.

---

<div align="center">

  **Lexora – Translate Documents. Preserve Formatting.**

  *Ücretsiz. Çevrimdışı. Kullanıcı odaklı.*

  **Developed by Engin ARSLAN**

  [GitHub](https://github.com/EnginArslan49/lexora-offline-document-translator) · [Releases](https://github.com/EnginArslan49/lexora-offline-document-translator/releases) · [YouTube](https://www.youtube.com/@ramkafe)

</div>