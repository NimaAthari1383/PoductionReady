# ISC Kea DHCPv4 — استقرار کامل One‑Click با Ansible

## تغییر مهم در v1.3

در Kea 3.2، فرمان‌های Control Agent/Unix socket مربوط به Host Reservations با پیشوند
`reservation-*` ارائه می‌شوند، نه `host-*`. بنابراین health check اکنون وجود
`reservation-get`, `reservation-add`, `reservation-del`, و `reservation-update`
را بررسی می‌کند.


## تغییر مهم در v1.2

نسخه v1.2 دیگر به `dpkg-architecture` وابسته نیست. مسیر واقعی Hookهای Kea مستقیماً از فایل
`libdhcp_pgsql.so` روی سیستم کشف می‌شود. بنابراین روی Ubuntu minimal نیز بدون نصب `dpkg-dev`
کار می‌کند و به `amd64` یا `arm64` hardcode نشده است.

همچنین `group_vars/kea_servers.yml` به `inventory/group_vars/kea_servers.yml` منتقل شده تا
متغیرهای گروه به‌صورت inventory-scoped و قابل پیش‌بینی load شوند.


این پروژه سناریوی فعلی لابراتوار را از سرور خام تا Kea فعال و تست‌شده اتوماتیک می‌کند.

## معماری

- Ubuntu Server
- Kea 3.2 از repository رسمی ISC/Cloudsmith
- DHCPv4 روی interface مشخص
- Lease Backend: memfile
- Host Reservations Backend: PostgreSQL
- PostgreSQL local TCP روی 127.0.0.1
- Host/Lease/Subnet/PostgreSQL hooks
- Unix control socket برای Stork/management
- تست `kea-dhcp4 -t` و `kea-dhcp4 -T`
- تست واقعی UDP/67 و control socket

## خطاهایی که این Role جلوی آن‌ها را می‌گیرد

- باقی ماندن sample subnet `192.0.2.0/24`
- sample reservation مثل `192.0.2.201`
- `DHCPSRV_NO_SOCKETS_OPEN`
- interface/IP اشتباه
- server IP داخل dynamic pool
- نبود `isc-kea-pgsql`
- نبود `libdhcp_pgsql.so`
- `Host database not available`
- `illegal use of a default value as credential`
- passwordهای پیش‌فرض `1234`, `*****`, `keatest`
- PostgreSQL `peer authentication failed`
- schema ایجادنشده
- load نشدن host commands
- systemd restart loop
- active بودن service بدون UDP/67 listener

## نکته مهم درباره DHCP رقیب

هیچ automationای نمی‌تواند با اطمینان DHCP خارجی روی کل Broadcast Domain را خاموش کند.
برای شبکه Host-252 باید VirtualBox DHCP و Kea قدیمی خاموش باشند.
Role وجود DHCP محلی روی UDP/67 را چک می‌کند و یک broadcast probe اختیاری هم دارد.

## اجرای سریع

1. `inventory/hosts.yml` را تنظیم کن.
2. `group_vars/kea_servers.yml` را برای interface/IP/subnet/pool/DNS تنظیم کن.
3. اجرا:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

اگر sudo password می‌خواهد:

```bash
ASK_BECOME_PASS=1 ./scripts/deploy.sh
```

برای یک host:

```bash
LIMIT=it-tools-server-1 ./scripts/deploy.sh
```

## IP استاتیک

پیش‌فرض:

```yaml
kea_manage_netplan: false
```

یعنی Role قبل از ادامه الزام می‌کند IP سرور از قبل stable باشد.

اگر Ansible از NIC مدیریت جداگانه وصل می‌شود و می‌خواهی خودش IP DHCP NIC را static کند:

```yaml
kea_manage_netplan: true
```

## Password PostgreSQL

Password در Git یا inventory نیست.
در اولین اجرا با OpenSSL تولید و در:

`/etc/kea/.kea_pg_password`

ذخیره می‌شود، سپس همان secret برای PostgreSQL و `kea-dhcp4.conf` استفاده می‌شود.
مقادیر پیش‌فرض Kea عمداً reject می‌شوند و taskهای حاوی password با `no_log` اجرا می‌شوند.

## Idempotency

اجرای مجدد:
- secret را عوض نمی‌کند
- DB را پاک نمی‌کند
- schema را دوباره initialize نمی‌کند
- validation را دوباره اجرا می‌کند
- config را فقط در صورت نیاز تغییر می‌دهد

## AWX

Playbook: `playbooks/site.yml`

Machine Credential باید SSH + privilege escalation داشته باشد.
هیچ DB passwordی لازم نیست در AWX ذخیره شود.

## Health check

روی سرور:

```bash
sudo bash scripts/healthcheck.sh
```

مرحله منطقی بعدی: ساخت Role دوم برای Stork Server + Agent + PostgreSQL Stork + registration + lease tracking.


## Stork در v1.4
بعد از Kea، `isc-stork-server` و `isc-stork-agent` نصب می‌شوند. یک DB/Role مستقل PostgreSQL برای Stork ساخته می‌شود؛
Server صراحتاً با TCP `127.0.0.1:5432` وصل می‌شود تا خطای peer authentication رخ ندهد؛ Agent عضو `_kea` می‌شود؛
و در پایان سرویس‌ها، 8080/8081 و HTTP UI بررسی می‌شوند.

UI: `http://<kea_server_address>:8080`

## تغییر مهم v1.5 — Reservation داخل Dynamic Pool

در این نسخه مقدار زیر به‌صورت پیش‌فرض فعال شده است:

```yaml
kea_reservations_out_of_pool: false
```

Dynamic Pool همچنان:

```text
192.168.252.100 - 192.168.252.200
```

است، ولی اکنون Host Reservation می‌تواند از داخل همین بازه ساخته شود.
`reservations-lookup-first: true` نیز فعال است تا Kea ابتدا Reservation را
بررسی کند و سپس سراغ تخصیص Dynamic برود.

اگر IP موردنظر از قبل Lease فعال داشته باشد، Role آن Lease را خودکار حذف
نمی‌کند؛ این رفتار عمدی است تا Client فعال به‌اشتباه قطع نشود.
جزئیات در `docs/IN_POOL_RESERVATIONS_FA.md` آمده است.
