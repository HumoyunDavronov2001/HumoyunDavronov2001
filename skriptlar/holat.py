#!/usr/bin/env python3
"""Jonli tizimlar paneli: har bir saytni tekshirib, rasmlar/holat.svg ni yasaydi.

GitHub Actions har 6 soatda ishga tushiradi. Faqat standart kutubxona.
Sayt kirish sahifasiga yo'naltirsa yoki 401/403 qaytarsa ham «ishlayapti»
hisoblanadi — tizim javob beryapti, faqat login talab qiladi.
"""
import datetime
import html
import pathlib
import time
import urllib.error
import urllib.request

TIZIMLAR = [
    ("GEONAZORAT SRM", "geonazorat.uz"),
    ("Bozor kuzatuvi", "kuzatuv.geonazorat.uz"),
    ("Gulnoza AI", "gulnoza.geonazorat.uz"),
    ("Jizzax hisobot", "soliq.geonazorat.uz"),
    ("Mahalla 17", "17lik.geonazorat.uz"),
    ("To'yxona nazorati", "marosim.geonazorat.uz"),
    ("TRACE4D", "trace4d.geonazorat.uz"),
    ("TENDER RADAR", "tender.geonazorat.uz"),
    ("Ofis miya", "miya.geonazorat.uz"),
    ("Tarmoq markazi", "markaz.geonazorat.uz"),
    ("DAVOMAT", "davomat.unistart-hub.uz"),
    ("Vatan tuyg'usi", "vatan.unistart-hub.uz"),
    ("Chorva nazorat", "mol-bozor.unistart-hub.uz"),
    ("RASTA", "elektronbozor.uz"),
    ("tong", "tong.ipak-yoli.uz"),
]

YOL = pathlib.Path(__file__).resolve().parent.parent / "rasmlar" / "holat.svg"
TOSHKENT = datetime.timezone(datetime.timedelta(hours=5))


def tekshir(domen: str) -> tuple[bool, int]:
    """(ishlayaptimi, javob vaqti ms). Ikki marta uriniladi."""
    for urinish in range(2):
        boshi = time.monotonic()
        try:
            so_rov = urllib.request.Request(
                f"https://{domen}/",
                headers={"User-Agent": "Mozilla/5.0 (holat-paneli; +github.com/HumoyunDavronov2001)"},
            )
            with urllib.request.urlopen(so_rov, timeout=20) as javob:
                javob.read(2048)
                kod = javob.status
        except urllib.error.HTTPError as x:
            kod = x.code
        except Exception:
            kod = 0
        ms = int((time.monotonic() - boshi) * 1000)
        if 200 <= kod < 400 or kod in (401, 403):
            return True, ms
        if urinish == 0:
            time.sleep(5)
    return False, ms


def svg(natijalar: list[tuple[str, str, bool, int]], vaqt: str) -> str:
    ishlayapti = sum(1 for *_, ok, _ in natijalar if ok)
    ustun, qator_bal = 3, 92
    qatorlar = (len(natijalar) + ustun - 1) // ustun
    b = 150 + qatorlar * qator_bal + 20
    kartalar = []
    for i, (nom, domen, ok, ms) in enumerate(natijalar):
        x = 40 + (i % ustun) * 404
        y = 150 + (i // ustun) * qator_bal
        rang = "#34d399" if ok else "#f87171"
        holat = f"{ms} ms" if ok else "javob bermadi"
        kechikish = f"{(i % 5) * 0.3:.1f}s"
        kartalar.append(f"""
  <g transform="translate({x} {y})">
    <rect width="384" height="76" rx="14" fill="#111a2e" stroke="#1f2a44"/>
    <circle cx="30" cy="38" r="7" fill="{rang}"/>
    <circle cx="30" cy="38" r="7" fill="none" stroke="{rang}" stroke-width="2">
      <animate attributeName="r" values="7;17" dur="2s" begin="{kechikish}" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".9;0" dur="2s" begin="{kechikish}" repeatCount="indefinite"/>
    </circle>
    <text x="54" y="34" class="nom">{html.escape(nom)}</text>
    <text x="54" y="56" class="domen">{html.escape(domen)}</text>
    <text x="364" y="44" text-anchor="end" class="ms" fill="{rang}">{holat}</text>
  </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1292" height="{b}" viewBox="0 0 1292 {b}" role="img" aria-label="Jonli tizimlar: {ishlayapti} / {len(natijalar)} ishlayapti">
  <defs>
    <linearGradient id="fon" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#0f1d36"/></linearGradient>
    <style>
      .sarlavha{{font:800 30px 'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif;fill:#f8fafc}}
      .izoh{{font:500 16px 'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif;fill:#94a3b8}}
      .nom{{font:700 17px 'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif;fill:#e2e8f0}}
      .domen{{font:500 13px 'DejaVu Sans Mono',Consolas,monospace;fill:#64748b}}
      .ms{{font:700 15px 'DejaVu Sans Mono',Consolas,monospace}}
      .katta{{font:800 46px 'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif;fill:#34d399}}
    </style>
  </defs>
  <rect width="1292" height="{b}" rx="18" fill="url(#fon)"/>
  <text x="40" y="62" class="sarlavha">Jonli tizimlar</text>
  <text x="40" y="96" class="izoh">Har 6 soatda GitHub Actions avtomatik tekshiradi · oxirgi tekshiruv: {vaqt} (Toshkent)</text>
  <text x="1252" y="78" text-anchor="end" class="katta">{ishlayapti}/{len(natijalar)}</text>
  <text x="1252" y="104" text-anchor="end" class="izoh">ishlayapti</text>
{''.join(kartalar)}
</svg>
"""


def main() -> None:
    natijalar = []
    for nom, domen in TIZIMLAR:
        ok, ms = tekshir(domen)
        natijalar.append((nom, domen, ok, ms))
        print(f"{'✓' if ok else '✗'} {domen:28} {ms} ms")
    vaqt = datetime.datetime.now(TOSHKENT).strftime("%d.%m.%Y %H:%M")
    YOL.parent.mkdir(parents=True, exist_ok=True)
    YOL.write_text(svg(natijalar, vaqt), encoding="utf-8")


if __name__ == "__main__":
    main()
