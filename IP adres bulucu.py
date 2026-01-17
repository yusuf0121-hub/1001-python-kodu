import requests
import sys


class IPInfoFetcher:
    """
    ipinfo.io API'sini kullanarak IP adresi bilgilerini getirmek için bir sınıf.
    """

    def __init__(self):
        self.api_url = 'https://ipinfo.io/'

    def get_ip_info(self, ip=None):
        """
        Belirtilen IP adresinin veya kendi IP'mizin bilgilerini getirir.
        """
        url = self.api_url
        if ip:
            url += ip
        url += '/json'

        print(f"Sorgulanıyor: {url}")

        try:
            # İstek gönderilir ve zaman aşımı eklenir
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # HTTP hataları için istisna fırlatır

            ip_info = response.json()

            # API'den gelen veride bir hata mesajı olup olmadığını kontrol et
            if 'error' in ip_info:
                print(f"API'den hata yanıtı alındı: {ip_info.get('error', 'Bilinmeyen Hata')}")
                return None

            return ip_info

        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Hatası oluştu (Hata Kodu: {errh.response.status_code}): {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Bağlantı Hatası oluştu: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Zaman Aşımı Hatası oluştu: {errt}")
        except requests.exceptions.RequestException as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")

        return None

    def format_ip_info(self, ip_info):
        """
        IP bilgilerini ekrana yazdırmak için metin olarak hazırlar.
        """
        if not ip_info:
            return "Sorgulama sırasında bir hata oluştu veya veri alınamadı."

        metin = f"--- IP Bilgileri Raporu ---\n\n"
        metin += f"IP Adresi: {ip_info.get('ip', 'Bilinmiyor')}\n"
        metin += f"Hostname: {ip_info.get('hostname', 'Bilinmiyor')}\n"
        metin += f"Şehir: {ip_info.get('city', 'Bilinmiyor')}\n"
        metin += f"Bölge (Eyalet/İl): {ip_info.get('region', 'Bilinmiyor')}\n"
        metin += f"Ülke: {ip_info.get('country', 'Bilinmiyor')}\n"
        metin += f"Konum (Lat/Lon): {ip_info.get('loc', 'Bilinmiyor')}\n"
        metin += f"Zaman Dilimi: {ip_info.get('timezone', 'Bilinmiyor')}\n"
        metin += f"İnternet Servis Sağlayıcı (ISP): {ip_info.get('org', 'Bilinmiyor')}\n"
        metin += f"Posta Kodu: {ip_info.get('postal', 'Bilinmiyor')}\n"

        return metin


def main():
    """
    Programın ana çalışma mantığını içeren fonksiyon.
    """
    fetcher = IPInfoFetcher()

    while True:
        choice = input(
            "\nKendi IP bilginizi mi (kendi) yoksa bir IP adresini mi (ip) sorgulamak istersiniz? (Çıkmak için 'exit' yazın) ").strip().lower()

        ip_info = None

        if choice == 'kendi':
            print("\nKendi IP bilginiz getiriliyor...")
            ip_info = fetcher.get_ip_info()
            break

        elif choice == 'ip':
            ip = input("Lütfen sorgulamak istediğiniz IP adresini girin: ").strip()
            if not ip:
                print("IP adresi boş bırakılamaz.")
                continue
            print(f"\n{ip} adresi için bilgi getiriliyor...")
            ip_info = fetcher.get_ip_info(ip)
            break

        elif choice in ('exit', 'cikis', 'çıkış'):
            print("Program sonlandırılıyor...")
            sys.exit(0)

        else:
            print("Geçersiz seçim! Lütfen 'kendi', 'ip' veya 'exit' girin.")
    if ip_info:
        formatted_info = fetcher.format_ip_info(ip_info)
        print("\n" + "=" * 40)
        print(formatted_info)
        print("=" * 40 + "\n")
    else:
        print("\nBilgi alma işlemi başarısız oldu.")
if __name__ == '__main__':
    main()
