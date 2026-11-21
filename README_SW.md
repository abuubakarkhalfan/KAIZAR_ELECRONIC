# KAIZAR ELOCTRONIC — Django storefront

Mfano kamili wa kuanzia wa duka la simu kwa Django. Jina limehifadhiwa kama ulivyoliandika: **KAIZAR ELOCTRONIC**. Tovuti ina Kiswahili na English, katalogi, kikapu, oda, risiti, picha za bidhaa, login ya wafanyakazi, ripoti ya mauzo na kitufe cha WhatsApp.

## Mahitaji

- Python 3.10 au mpya zaidi
- Django 5.2
- Pillow kwa kupokea na kuonyesha picha

## Kuwasha kwenye Windows

Fungua PowerShell kwenye folda ya `kaizar_electronic`, kisha tumia:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Fungua `http://127.0.0.1:8000/` kuona duka.

## Kuingia kama admin au mfanyakazi

- Login ya wafanyakazi: `http://127.0.0.1:8000/staff/login/`
- Dashibodi: `http://127.0.0.1:8000/staff/`
- Usimamizi wa akaunti na ruhusa: `http://127.0.0.1:8000/django-admin/`

Tengeneza akaunti kuu kwa `createsuperuser`. Ili kuongeza mfanyakazi, ingia Django Admin, fungua **Users**, ongeza akaunti, weka nenosiri na washa **Staff status**. Wafanyakazi wasio na `is_staff` hawawezi kuingia kwenye dashibodi ya duka. Usimpe kila mfanyakazi ruhusa ya superuser.

## Bidhaa na picha

Kutoka dashibodi bonyeza **Weka bidhaa**. Weka chapa, jina, maelezo, bei na picha ya JPG, PNG au WebP (hadi MB 5). Bidhaa inaweza kufichwa au kuonyeshwa tena bila kuifuta.

## Oda, risiti na ripoti

Mteja huweka idadi, hukagua jumla, kisha hutuma oda. Risiti ya kila oda ina namba ya kipekee. Oda mpya huanza katika hali ya **Inasubiri malipo**; mteja anaweza kuighairi ikiwa bado haijalipiwa. Mfanyakazi akishathibitisha malipo, abonyeze **Thibitisha malipo**. Ripoti hujumlisha oda zilizothibitishwa tu.

**Malipo ya M-Pesa/Tigo Pesa/Airtel Money hayajaunganishwa** kwa sababu provider na akaunti ya biashara havijatolewa. Oda hazibadiliki kuwa imelipiwa moja kwa moja; wafanyakazi huthibitisha baada ya kuona malipo. SMS kwa admin pia inahitaji SMS gateway na namba itakayopokea ujumbe.

## WhatsApp

Vitufe vya WhatsApp vinafungua `https://wa.me/255612660381`, ambacho ni namba ya Tanzania inayolingana na `0612660381`.

## Muundo wa folda

```text
kaizar_electronic/
  manage.py
  requirements.txt
  kaizar_store/       # settings, URL routing, WSGI/ASGI
  shop/               # models, forms, views, staff dashboard
    migrations/
    templates/shop/   # kurasa za duka, oda, login na risiti
    static/shop/      # CSS
  media/              # picha zilizopakiwa wakati wa matumizi
```

## Kabla ya kuweka mtandaoni

Weka `DJANGO_SECRET_KEY` ya siri, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` yenye domain yako, HTTPS na hifadhidata ya uzalishaji. Badili SQLite kwenda PostgreSQL inapowekwa hadharani. Picha zilizopakiwa zinahitaji media storage ya kudumu. Usitumie `runserver` kwa uzalishaji.
