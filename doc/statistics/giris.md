Kural şu:

Std Dev > Mean → verinde ciddi outlier var

Senin veride:

Mean: $234M
Std Dev: $1.45 milyar → mean'in 6 katı 🚨

Normal bir LC portföyünde Std Dev mean'in belki 2-3 katı olur. 6 kat? O $10 milyarlık canavar iş yapıyor 😄

Bankacılık bağlantısı:
Risk masası tam bunu izler — Coefficient of Variation (CV):
CV = Std Dev / Mean = 1.45B / 234M = 6.2
CV > 1 → yüksek risk, dağınık portföy
CV > 3 → "kim bu portföyü onayladı?" soruşturması 😄
CV = 6.2 → sen test datasısın, gerçek banka değilsin, neyse ki 😂


Banka A: $20M, $21M, $19M, $20M, $22M
Banka B: $1M, $200M, $5M, $300M, $50M

Banka A → her değer mean'e yakın → düşük variance
Banka B → değerler her yere saçılmış → yüksek variance

Variance nasıl hesaplanır?
Her değerin mean'den farkını al, karesi al, ortala:
Banka A mean = $20.4M
(20-20.4)² + (21-20.4)² + (19-20.4)² + (20-20.4)² + (22-20.4)²
→ çok küçük sayılar → düşük variance ✅
Neden kare alıyoruz?
Çünkü farklar negatif olabilir — $15M - $20M = -$5M. Toplarsan sıfırlanır, anlamsız olur. Kare alınca hepsi pozitif 😄

Şimdi kendi verine uygulayalım. Yeni cell:
pythonprint(f"Variance: ${df['amount'].var():>25,.2f}")
print(f"Std Dev:  ${df['amount'].std():>25,.2f}")

Variance → toplam dağınıklık miktarı,
büyük outlier'ları abartarak vurgular.
Kare aldığın için büyük farklar çok daha büyük görünür.
Std Dev → "tipik uzaklık",
günlük hayatta kullanılır,
mean ile aynı birimde konuşur.

Bankacılık örneği:
Risk modelleri Variance kullanır —
çünkü büyük kayıpları abartmak istiyorlar.
$100M kayıp, $10M kaybın 100 katı değil,
variance'da 10,000 katı görünür.
Bu kasıtlı — riski küçümseme! 🚨
Günlük raporda ise Std Dev kullanırsın —
"tipik LC mean'den $1.4 milyar sapıyor"
diye müdürüne anlatırsın. 😄

Variance  → risk modellemesi, 
            büyük sapmaları vurgula
Std Dev   → insan dili, 
            "tipik sapma ne kadar?"

Day 2 özeti:
- Variance → dağınıklığı ölçer, birimi dolar²
- Std Dev  → Variance'ın karekökü, birimi dolar
- CV = Std Dev/Mean → 6.2 çıktı, outlier var
- Variance risk modellemesi için, 
  Std Dev insan dili için



Quartile veriyi 4'e böler:
Q1 → verinin %25'i burada biter
Q2 → verinin %50'si (= Median!)
Q3 → verinin %75'i burada biter

25%  →  $4,899,627    = Q1
50%  →  $20,690,823   = Q2 (Median)
75%  →  $36,277,731   = Q3


Q1 = $4.9M, Q3 = $36.2M
Aradaki fark ne? Ve bu farka ne diyoruz?

Q1 = $4.9M, Q3 = $36.2M
Aradaki fark ne? Ve bu farka ne diyoruz?

* Interquartile range
Ortadaki %50'yi kapsıyor — buna IQR (Interquartile Range) diyoruz:
IQR = Q3 - Q1
IQR = $36.2M - $4.9M = $31.3M

IQR outlier'ları yakalamak için kullanılır.
Kural şu:

Alt sınır = Q1 - 1.5 × IQR
Üst sınır = Q3 + 1.5 × IQR

Bu sınırların dışındaki her şey → OUTLIER 🚨

quantile (kuantil)

İstatistik ve matematikte quantile (kuantil), sıralanmış bir veri setini veya olasılık dağılımını 
eşit parçalara bölen kesme noktalarıdır.Kullanım amacına ve ayrılan parça sayısına göre özel isimler alırlar:
Çeyreklik (Quartile): Veriyi 4 eşit parçaya bölen noktalardır (Örn: %25, %50, %75).
Ondalık (Decile): Veriyi 10 eşit parçaya bölen noktalardır.
Yüzdelik (Percentile): Veriyi 100 eşit parçaya bölen noktalardır.


Day 3 özeti:
- Quartiles → veriyi 4 eşit yüzdeye böler
- Q1 = %25, Q2 = Median, Q3 = %75
- IQR = Q3 - Q1 = ortadaki %50
- Outlier sınırı = Q1 - 1.5×IQR / Q3 + 1.5×IQR
- 1.5 → Tukey'in 1977 standardı
- Eşit yüzde, eşit sayı değil!
