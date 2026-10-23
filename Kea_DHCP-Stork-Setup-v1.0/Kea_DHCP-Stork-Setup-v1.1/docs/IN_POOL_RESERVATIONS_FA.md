# رزرو IP داخل Dynamic Pool در Kea

تنظیم این پروژه:

```yaml
kea_pool_start: "192.168.252.100"
kea_pool_end: "192.168.252.200"
kea_reservations_out_of_pool: false
```

و در Kea:

```json
"reservations-lookup-first": true,
"ip-reservations-unique": true
```

بنابراین می‌توان IPهایی مثل `192.168.252.120`، `192.168.252.150` یا
`192.168.252.199` را از داخل همان Pool برای یک Host Reservation رزرو کرد.

## نکته مهم درباره Lease موجود

اگر IP موردنظر قبل از ایجاد Reservation به یک Client دیگر Lease شده باشد،
Reservation جدید نمی‌تواند آن Lease فعال را به‌صورت جادویی پس بگیرد.

قبل از رزرو یک IP داخل Pool بررسی کنید:

```bash
grep '^192\.168\.252\.150,' /var/lib/kea/kea-leases4.csv
```

اگر رکورد فعال برای Client دیگری وجود دارد، یکی از روش‌های امن زیر را انجام دهید:

1. Client قبلی DHCPRELEASE ارسال کند و سپس Reservation ساخته شود.
2. منتظر انقضای Lease بمانید.
3. فقط اگر مطمئن هستید Client قبلی دیگر از آن IP استفاده نمی‌کند، Lease را از
   Stork/Kea حذف کنید و Client رزروشده را Renew کنید.

حذف خودکار Leaseهای فعال در این Role عمداً انجام نمی‌شود، چون می‌تواند باعث
قطع ارتباط Client فعال شود.

## ساخت Reservation

در Stork، Reservation را برای Subnet زیر بسازید:

- Subnet: `192.168.252.0/24`
- Subnet ID: `1`
- Identifier: ترجیحاً `hw-address`
- IPv4: هر IP آزاد داخل `192.168.252.100-200`

مثال:

- MAC: `08:00:27:aa:bb:cc`
- IPv4: `192.168.252.150`
- Hostname: `example-server`

بعد Client را Renew/Reboot کنید.

## کنترل سلامت

```bash
sudo systemctl is-active isc-kea-dhcp4-server
sudo ss -lunp | grep ':67 '
sudo journalctl -u isc-kea-dhcp4-server -n 100 --no-pager
```

نباید `DHCP4_CONFIG_LOAD_FAIL` یا `DHCP4_INIT_FAIL` مشاهده شود.
