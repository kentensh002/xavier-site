"""Génère images optimisées + pages HTML du site photographe (sortie : HTML statique).
Usage : python -I build_site.py <dossier_extraction> <dossier_site>

- Photos sources : <dossier_extraction>/<dossier>/<nom>.jpeg ; une entrée de `files` peut s'écrire "dossier/nom" pour
  piocher dans un autre dossier que celui de la série.
- docs/images-manifest.json garde l'empreinte (md5) de chaque photo source : une image n'est régénérée que si sa source a
  changé ou n'existe pas encore. Si la source est absente, l'image déjà générée est conservée telle quelle.
- XS_BOOTSTRAP=1 : à la toute première utilisation du manifeste, considère les images existantes comme à jour.
- Rangées de la galerie : `rows` (listes d'indices) ou `pattern` (nombre de photos par rangée, dans l'ordre).
"""
import sys, os, re, html, json, hashlib
from PIL import Image, ImageOps, ImageCms

SRC, SITE = sys.argv[1], sys.argv[2]
BASE_URL = "https://xavieryou.com"
SIZES = [800, 1400, 2400]  # grand côté, en px

# ordre = ordre voulu (chronologique) ; cover = photo de la carte d'accueil ; q = qualité WebP (68 pour les scans argentiques)
SERIES = [
    dict(slug="soir", title="Un soir entre amis", place="Cannes", year=2018, folder="new_serie7",
         files=["IMG_0010", "IMG_9924", "ajouterunsoirentreamis/IMG_4654", "ajouterunsoirentreamis/IMG_4655"],
         rows=[[0, 1], [2, 3]], cover=1, cover_pos="50% 28%"),
    dict(slug="nacre", title="À fleur de nacre", place="Cannes", year=2019, folder="uneautresriemettreaussi",
         files=["HY3Q9132", "HY3Q9164", "HY3Q9165", "HY3Q9169", "HY3Q9173", "extras/IMG_6676"],
         rows=[[0, 1], [2, 3], [4, 5]], cover=4, cover_pos="50% 50%"),
    dict(slug="rouge", title="Sous le rouge, à dessein", place="Cannes", year=2019, folder="new_serie41",
         files=["HY3Q9282", "HY3Q9287", "HY3Q9298"],
         rows=[[0, 1, 2]], cover=2, cover_pos="50% 40%"),
    dict(slug="isis", title="Isis à demi dévoilée", place="Cannes", year=2019, folder="new_serie6",
         files=["HY3Q9019", "HY3Q9020", "IMG_0900"],
         rows=[[0, 1, 2]], cover=1, cover_pos="50% 50%"),
    dict(slug="pose", title="Le temps d’une pose", place="Paris", year=2021, folder="photosmettresurlesitexavieryou",
         files=["11980007", "11970032", "11980020", "12360031",
                "aajouterlasrieletempsdunepose/11980008", "aajouterlasrieletempsdunepose/12360023",
                "aajouterlasrieletempsdunepose/12360025", "aajouterlasrieletempsdunepose/12360028",
                "aajouterlasrieletempsdunepose/12360029", "aajouterlasrieletempsdunepose/12360034"],
         rows=[[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], cover=1, cover_pos="50% 50%", q=68),
    dict(slug="nuit", title="La nuit lui appartient", place="Montpellier", year=2021, folder="autresrie",
         files=["HY3Q9671", "HY3Q9672", "HY3Q9675", "extras/IMG_5098"],
         rows=[[0], [1, 2, 3]], cover=1, cover_pos="50% 50%"),
    dict(slug="pink", title="Pink Flow", place="Festival de Cannes", year=2021, folder="pinkflow",
         files=["IMG_4650", "IMG_6312", "IMG_6314"],
         rows=[[0], [1, 2]], cover=1, cover_pos="50% 25%"),
    dict(slug="figures", title="Figures sur fond noir", place="Genève", year=2021, folder="nouvellessrie",
         files=["IMG_6361", "IMG_6362", "IMG_6370", "IMG_6360"],
         rows=[[0, 1], [2, 3]], cover=1, cover_pos="50% 50%"),
    dict(slug="heures", title="Les heures sans rendez-vous", place="Concarneau", year=2021, folder="concarneau",
         files=["concarneausuite3/12350015", "concarneausuite1/12350018", "concarneau/12350019", "concarneausuite3/12350020",
                "concarneausuite1/12350021", "concarneausuite3/12350022", "concarneausuite2/12350023", "concarneausuite1/12350024",
                "concarneausuite1/12360001", "concarneausuite1/12360002", "concarneausuite1/12360004", "concarneausuite2/12360005",
                "concarneausuite2/12360007", "concarneau/12360008", "concarneausuite2/12360009", "concarneau/12360013",
                "concarneau/12360015", "concarneau/12360016", "concarneausuite2/12360018", "concarneausuite1/12360019",
                "concarneau/12360020"],
         pattern=[3, 2, 3, 2, 3, 2, 3, 2, 1], cover=15, cover_pos="62% 50%", q=68),
    dict(slug="chapelle", title="Séjour dans une ancienne chapelle", place="Nantes", year=2021, folder="mathildeshooting",
         files=["5b450a11-1ce4-46b2-9f17-897a9f0462dd", "5fdb2f37-9c94-4e14-a819-0c0048ee6b4c",
                "99d55800-977a-4802-ae30-f97c8f056937"],   # 6 photos prévues par Xavier : 3 reçues (1024 px) à ce jour
         rows=[[0, 1, 2]], cover=0, cover_pos="80% 50%"),
    dict(slug="lianes", title="La chambre des lianes", place="Cannes", year=2022, folder="serie4",
         files=["IMG_6958", "3EA3002F-985C-4B55-8003-1A559231FF43",
                "4DFF6CA7-C472-48E4-978F-4B5217E8804D", "78599995-7E84-43E0-BB59-736A15728337"],
         rows=[[0], [1, 2, 3]], cover=0, cover_pos="42% 50%", q=68),
    dict(slug="snow", title="Snow Queen", place="Verbier", year=2023, folder="nouvellesrie",
         files=["554A9367", "554A9368", "554A9396", "554A9402", "554A9542", "554A9553"],
         rows=[[0, 1], [2, 3], [4, 5]], cover=1, cover_pos="60% 30%"),
]
for s in SERIES:
    if "pattern" in s:
        rows, i = [], 0
        for n in s["pattern"]:
            rows.append(list(range(i, i + n))); i += n
        s["rows"] = rows
    assert sorted(sum(s["rows"], [])) == list(range(len(s["files"]))), f"rangées incomplètes : {s['slug']}"

IG_URL = "https://www.instagram.com/xavieryou_officiel/"
IG_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
           '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/>'
           '<circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>')
OG_FILE = "og-logo.jpg"   # image de partage
OG_POS_X, OG_POS_Y = 1.0, 0.5   # position du recadrage de la photo dans l'image de partage (0 = gauche/haut, 1 = droite/bas)
HERO = ("pose", 3)           # portrait noir et blanc
HERO_POS = "100% 50%"
CONTACT_PHOTO = ("pose", 2)  # photo à droite sur la page Contact

esc = html.escape
SRGB = ImageCms.createProfile("sRGB")


def to_srgb(im):
    icc = im.info.get("icc_profile")
    if icc:
        try:
            import io
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, SRGB, outputMode="RGB")
        except Exception as e:
            print("  (profil ICC ignoré :", e, ")")
    return im.convert("RGB")


def src_path(s, entry):
    """chemin de la photo source ('nom' dans le dossier de la série, ou 'dossier/nom') ; None si absente"""
    folder, name = entry.split("/", 1) if "/" in entry else (s["folder"], entry)
    for ext in (".jpeg", ".jpg", ".JPEG", ".JPG", ".png"):
        p = os.path.join(SRC, folder, name + ext)
        if os.path.exists(p):
            return p
    return None


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 1. images ----------
MANIFEST_PATH = os.path.join(SITE, "docs", "images-manifest.json")
MANI = json.load(open(MANIFEST_PATH, encoding="utf-8")) if os.path.exists(MANIFEST_PATH) else {}
BOOTSTRAP = bool(os.environ.get("XS_BOOTSTRAP"))
NEW_MANI = {}
IMG = {}  # (slug, idx) -> {'sizes': {L: (w,h)}, 'ratio': r}
for s in SERIES:
    outdir = os.path.join(SITE, "images", s["slug"])
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):          # série raccourcie : retire les images en trop
        m = re.match(r"(\d+)-\d+\.webp$", f)
        if m and int(m.group(1)) > len(s["files"]):
            os.remove(os.path.join(outdir, f)); print("supprimée (en trop) :", s["slug"], f)
    for i, entry in enumerate(s["files"]):
        key = f"{s['slug']}/{i+1:02d}"
        outs = {L: os.path.join(outdir, f"{i+1:02d}-{L}.webp") for L in SIZES}
        have = all(os.path.exists(p) for p in outs.values())
        path = src_path(s, entry)
        md5 = md5_of(path) if path else None
        fresh = have and ((md5 is None and key in MANI) or
                          (md5 is not None and (MANI.get(key) == md5 or (BOOTSTRAP and key not in MANI))))
        if fresh:
            info = {}
            for L in SIZES:
                with Image.open(outs[L]) as t:
                    info[L] = t.size
            NEW_MANI[key] = md5 or MANI[key]
            status = "à jour"
        else:
            if path is None:
                raise SystemExit(f"Photo source introuvable pour {key} ({entry}) dans {SRC}")
            im = to_srgb(ImageOps.exif_transpose(Image.open(path)))   # aucune métadonnée EXIF / GPS n'est recopiée
            w0, h0 = im.size
            info = {}
            for L in SIZES:
                k = min(1.0, L / max(w0, h0))
                w, h = round(w0 * k), round(h0 * k)
                r = im if k == 1.0 else im.resize((w, h), Image.LANCZOS)
                r.save(outs[L], "WEBP", quality=s.get("q", 80), method=6)
                info[L] = (w, h)
            NEW_MANI[key] = md5
            status = "GENEREE"
        IMG[(s["slug"], i)] = dict(sizes=info, ratio=info[1400][0] / info[1400][1])
        print(f"{key:12} {entry[:46]:46} {status:8} {info[1400][0]}x{info[1400][1]}  2400: {os.path.getsize(outs[2400])//1024} Ko")
os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(NEW_MANI, f, indent=1, sort_keys=True)
    f.write("\n")

# image de partage (WhatsApp, etc.) 1200x630 : portrait noir et blanc à gauche, logo de Xavier sur fond crème à droite
# (panneau logo = docs/logo/og-panel.png, 600x630 ; nom du fichier versionné pour contourner le cache de WhatsApp)
hs, hi = HERO
hero_series = next(x for x in SERIES if x["slug"] == hs)
hp = src_path(hero_series, hero_series["files"][hi])
og_out = os.path.join(SITE, "images", OG_FILE)
panel = os.path.join(SITE, "docs", "logo", "og-panel.png")
if hp and os.path.exists(panel):
    im = to_srgb(ImageOps.exif_transpose(Image.open(hp)))
    w, h = im.size
    k = max(600 / w, 630 / h)   # la photo remplit toute la moitié gauche (600x630)
    im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    left = int((im.width - 600) * OG_POS_X)
    top = int((im.height - 630) * OG_POS_Y)
    og = Image.new("RGB", (1200, 630), (244, 241, 232))
    og.paste(im.crop((left, top, left + 600, top + 630)), (0, 0))
    og.paste(Image.open(panel).convert("RGB"), (600, 0))
    og.save(og_out, "JPEG", quality=86, optimize=True, progressive=True)
    print(OG_FILE, os.path.getsize(og_out) // 1024, "Ko")
elif os.path.exists(og_out):
    print(OG_FILE, "conservée (photo source ou panneau logo absents)")
else:
    raise SystemExit("image de partage impossible à créer")


# ---------- 2. langues ----------
# Le français reste à la racine (URLs inchangées) ; l'anglais est dans /en/, l'italien dans /it/.
LANGS = {
    "fr": dict(code="fr", dir="", prefix="", locale="fr_FR"),
    "en": dict(code="en", dir="en/", prefix="../", locale="en_GB"),
    "it": dict(code="it", dir="it/", prefix="../", locale="it_IT"),
}
PAGE_NAMES = {
    "fr": dict(about="a-propos.html", contact="contact.html", serie="serie-{slug}.html"),
    "en": dict(about="about.html", contact="contact.html", serie="series-{slug}.html"),
    "it": dict(about="chi-sono.html", contact="contatti.html", serie="serie-{slug}.html"),
}
SWITCH_LABEL = {"fr": "Français", "en": "English", "it": "Italiano"}

# Les titres des séries restent en français dans toutes les langues (ce sont des titres d'œuvres).
PLACES = {
    "fr": {"Cannes": "Cannes", "Paris": "Paris", "Montpellier": "Montpellier", "Festival de Cannes": "Festival de Cannes",
           "Genève": "Genève", "Concarneau": "Concarneau", "Verbier": "Verbier", "Nantes": "Nantes"},
    "en": {"Cannes": "Cannes", "Paris": "Paris", "Montpellier": "Montpellier", "Festival de Cannes": "Cannes Film Festival",
           "Genève": "Geneva", "Concarneau": "Concarneau", "Verbier": "Verbier", "Nantes": "Nantes"},
    "it": {"Cannes": "Cannes", "Paris": "Parigi", "Montpellier": "Montpellier", "Festival de Cannes": "Festival di Cannes",
           "Genève": "Ginevra", "Concarneau": "Concarneau", "Verbier": "Verbier", "Nantes": "Nantes"},
}

T = {
    "fr": dict(
        home_title="Xavier You — Photographe auteur",
        home_desc="Xavier You, photographe auteur. Portrait, mode et abstraction, en noir et blanc comme en couleur.",
        tagline="Photographe auteur.",
        hero_desc='Portrait, mode et abstraction, en noir et blanc comme en couleur. <span class="nowrap">France · Italie · Suisse.</span>',
        hero_alt="Portrait en noir et blanc, Paris, 2021",
        contact_btn="contact",
        series="Séries",
        nav_about="À PROPOS", mob_about="À propos", nav_contact="CONTACT", mob_contact="Contact",
        about_teaser="La peinture, la poésie et la musique nourrissent son regard. Sa photographie accueille aussi bien la sensualité et la mise en scène que le silence et la contemplation.",
        about_btn="lire la présentation",
        track="portrait · mode · abstraction · noir et blanc · couleur · argentique",
        footer_desc="France · Italie · Suisse.",
        home_label="Xavier You, accueil", logo_alt="Xavier You, photographe auteur",
        copyright="© Xavier You — Tous droits réservés",
        footer_about="À propos", footer_contact="Contact",
        kicker="Série {i} / {n}", other_series="Autres séries",
        prev="← Série précédente", next="Série suivante →",
        serie_desc="{title} — {meta}. Série photographique de Xavier You, photographe auteur.",
        photo_alt="{title}, {meta} — photographie {i} sur {n}",
        about_title="À propos — Xavier You",
        about_desc="Présentation de Xavier You, photographe auteur : portrait, mode et abstraction, entre la France, l'Italie et la Suisse.",
        about_label="Qui suis-je ?",
        about_btn2="contact",
        about_text=[
            "Xavier You est un photographe auteur qui partage son temps entre la France, l'Italie et la Suisse. Il explore le portrait, la mode et l'abstraction dans une pratique qui évolue avec les rencontres, les voyages et les périodes de sa vie.",
            "Son attention se porte sur les relations entre les corps, les matières et l'espace. Une courbe répond à une ligne architecturale&nbsp;; une ombre ou un reflet déplace la lecture d'un visage. Entre composition et imprévu, il recherche ce moment où une scène concrète devient une image ouverte à d'autres perceptions.",
            "La peinture, la poésie et la musique nourrissent son regard. Sa photographie accueille aussi bien la sensualité et la mise en scène que le silence et la contemplation. Elle est traversée par l'intuition que le visible ne livre pas tout&nbsp;: certaines images gardent une présence, une tension ou un mystère que les mots ne suffisent pas à saisir.",
            "Il travaille en noir et blanc comme en couleur, privilégiant l'argentique pour son grain, sa matière et la place qu'il laisse à l'imprévu. Le numérique participe à cette recherche et lui offre d'autres possibilités d'expérimentation. Le choix du procédé accompagne l'intention de chaque projet.",
            "À travers ces différentes approches, Xavier You cherche à créer des images qui traversent le temps&nbsp;: des photographies auxquelles on revient pour une émotion, un détail ou une énigme encore ouverte.",
        ],
        contact_title="Contact — Xavier You",
        contact_desc="Contacter Xavier You, photographe auteur.",
        contact_text="Pour toute demande, collaboration ou projet, vous pouvez écrire à Xavier You à l'adresse ci-dessous.",
        links_title="Liens utiles",
        contact_alt="Portrait, Paris, 2021",
    ),
    "en": dict(
        home_title="Xavier You — Fine-art photographer",
        home_desc="Xavier You, fine-art photographer. Portrait, fashion and abstraction, in black and white and in colour.",
        tagline="Fine-art photographer.",
        hero_desc='Portrait, fashion and abstraction, in black and white and in colour. <span class="nowrap">France · Italy · Switzerland.</span>',
        hero_alt="Black-and-white portrait, Paris, 2021",
        contact_btn="contact",
        series="Series",
        nav_about="ABOUT", mob_about="About", nav_contact="CONTACT", mob_contact="Contact",
        about_teaser="Painting, poetry and music nourish his gaze. His photography welcomes sensuality and staging as readily as silence and contemplation.",
        about_btn="read more",
        track="portrait · fashion · abstraction · black and white · colour · analogue film",
        footer_desc="France · Italy · Switzerland.",
        home_label="Xavier You, home", logo_alt="Xavier You, fine-art photographer",
        copyright="© Xavier You — All rights reserved",
        footer_about="About", footer_contact="Contact",
        kicker="Series {i} / {n}", other_series="Other series",
        prev="← Previous series", next="Next series →",
        serie_desc="{title} — {meta}. A photographic series by Xavier You, fine-art photographer.",
        photo_alt="{title}, {meta} — photograph {i} of {n}",
        about_title="About — Xavier You",
        about_desc="About Xavier You, fine-art photographer: portrait, fashion and abstraction, between France, Italy and Switzerland.",
        about_label="Who am I?",
        about_btn2="contact",
        about_text=[
            "Xavier You is a fine-art photographer who divides his time between France, Italy and Switzerland. He explores portraiture, fashion and abstraction in a practice that evolves with the encounters, the journeys and the different periods of his life.",
            "His attention turns to the relationships between bodies, materials and space. A curve answers an architectural line; a shadow or a reflection shifts the way a face is read. Between composition and the unforeseen, he looks for the moment when a concrete scene becomes an image open to other perceptions.",
            "Painting, poetry and music nourish his gaze. His photography welcomes sensuality and staging as readily as silence and contemplation. It is shot through with the intuition that the visible does not give everything away: some images hold a presence, a tension or a mystery that words cannot quite grasp.",
            "He works in black and white as well as in colour, favouring analogue film for its grain, its texture and the room it leaves for the unexpected. Digital takes part in this research and offers other possibilities for experimentation. The choice of process follows the intention of each project.",
            "Through these different approaches, Xavier You seeks to create images that outlast time: photographs one comes back to for an emotion, a detail or a riddle still left open.",
        ],
        contact_title="Contact — Xavier You",
        contact_desc="Get in touch with Xavier You, fine-art photographer.",
        contact_text="For any enquiry, collaboration or project, you can write to Xavier You at the address below.",
        links_title="Useful links",
        contact_alt="Portrait, Paris, 2021",
    ),
    "it": dict(
        home_title="Xavier You — Fotografo d'autore",
        home_desc="Xavier You, fotografo d'autore. Ritratto, moda e astrazione, in bianco e nero come a colori.",
        tagline="Fotografo d'autore.",
        hero_desc='Ritratto, moda e astrazione, in bianco e nero come a colori. <span class="nowrap">Francia · Italia · Svizzera.</span>',
        hero_alt="Ritratto in bianco e nero, Parigi, 2021",
        contact_btn="contatti",
        series="Serie",
        nav_about="CHI SONO", mob_about="Chi sono", nav_contact="CONTATTI", mob_contact="Contatti",
        about_teaser="La pittura, la poesia e la musica nutrono il suo sguardo. La sua fotografia accoglie tanto la sensualità e la messa in scena quanto il silenzio e la contemplazione.",
        about_btn="leggi la presentazione",
        track="ritratto · moda · astrazione · bianco e nero · colore · pellicola",
        footer_desc="Francia · Italia · Svizzera.",
        home_label="Xavier You, home", logo_alt="Xavier You, fotografo d'autore",
        copyright="© Xavier You — Tutti i diritti riservati",
        footer_about="Chi sono", footer_contact="Contatti",
        kicker="Serie {i} / {n}", other_series="Altre serie",
        prev="← Serie precedente", next="Serie successiva →",
        serie_desc="{title} — {meta}. Serie fotografica di Xavier You, fotografo d'autore.",
        photo_alt="{title}, {meta} — fotografia {i} di {n}",
        about_title="Chi sono — Xavier You",
        about_desc="Presentazione di Xavier You, fotografo d'autore: ritratto, moda e astrazione, tra Francia, Italia e Svizzera.",
        about_label="Chi sono?",
        about_btn2="contatti",
        about_text=[
            "Xavier You è un fotografo d'autore che divide il suo tempo tra la Francia, l'Italia e la Svizzera. Esplora il ritratto, la moda e l'astrazione in una pratica che evolve con gli incontri, i viaggi e le diverse stagioni della sua vita.",
            "La sua attenzione si concentra sulle relazioni tra i corpi, le materie e lo spazio. Una curva risponde a una linea architettonica; un'ombra o un riflesso sposta la lettura di un volto. Tra composizione e imprevisto, cerca il momento in cui una scena concreta diventa un'immagine aperta ad altre percezioni.",
            "La pittura, la poesia e la musica nutrono il suo sguardo. La sua fotografia accoglie tanto la sensualità e la messa in scena quanto il silenzio e la contemplazione. È attraversata dall'intuizione che il visibile non dica tutto: alcune immagini conservano una presenza, una tensione o un mistero che le parole non bastano a cogliere.",
            "Lavora in bianco e nero come a colori, privilegiando la pellicola per la sua grana, la sua materia e lo spazio che lascia all'imprevisto. Il digitale partecipa a questa ricerca e offre altre possibilità di sperimentazione. La scelta del procedimento accompagna l'intenzione di ogni progetto.",
            "Attraverso questi diversi approcci, Xavier You cerca di creare immagini che attraversano il tempo: fotografie a cui si torna per un'emozione, un dettaglio o un enigma ancora aperto.",
        ],
        contact_title="Contatti — Xavier You",
        contact_desc="Contattare Xavier You, fotografo d'autore.",
        contact_text="Per qualsiasi richiesta, collaborazione o progetto, potete scrivere a Xavier You all'indirizzo qui sotto.",
        links_title="Link utili",
        contact_alt="Ritratto, Parigi, 2021",
    ),
}

CUR = LANGS["fr"]


def tr(key):
    return T[CUR["code"]][key]


def fname(lang, kind, slug=None):
    if kind == "index":
        return "index.html"
    n = PAGE_NAMES[lang]
    return n["serie"].format(slug=slug) if kind == "serie" else n[kind]


def abs_url(lang, kind, slug=None):
    return BASE_URL + "/" + LANGS[lang]["dir"] + ("" if kind == "index" else fname(lang, kind, slug))


def href_to(lang_to, kind, slug=None):
    """lien relatif depuis la langue courante vers la page équivalente dans lang_to"""
    name = fname(lang_to, kind, slug)
    if lang_to == CUR["code"]:
        return name
    return CUR["prefix"] + LANGS[lang_to]["dir"] + ("" if kind == "index" else name)


def spage(s):
    return fname(CUR["code"], "serie", s["slug"])


def meta(s):
    return f"{PLACES[CUR['code']][s['place']]}, {s['year']}"


# ---------- 3. helpers HTML ----------
def srcset(slug, idx):
    sz = IMG[(slug, idx)]["sizes"]
    p = CUR["prefix"]
    return ", ".join(f"{p}images/{slug}/{idx+1:02d}-{L}.webp {sz[L][0]}w" for L in SIZES)


def img_tag(slug, idx, alt, sizes_attr, eager=False, extra=""):
    w, h = IMG[(slug, idx)]["sizes"][1400]
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{CUR["prefix"]}images/{slug}/{idx+1:02d}-1400.webp" srcset="{srcset(slug, idx)}" sizes="{sizes_attr}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" {load} decoding="async"{extra}>')


def by_slug(slug):
    return next(x for x in SERIES if x["slug"] == slug)


def head(title, desc, kind, slug=None, og_title=None, indexable=True):
    p = CUR["prefix"]
    ogt = og_title or title
    url = abs_url(CUR["code"], kind, slug)
    if indexable:
        alts = "\n".join(f'  <link rel="alternate" hreflang="{lc}" href="{abs_url(lc, kind, slug)}">' for lc in LANGS)
        alts += f'\n  <link rel="alternate" hreflang="x-default" href="{abs_url("fr", kind, slug)}">'
        seo = f'  <link rel="canonical" href="{url}">\n{alts}\n'
        og_url = f'  <meta property="og:url" content="{url}">\n'
        og_alt = "".join(f'  <meta property="og:locale:alternate" content="{v["locale"]}">\n'
                         for k, v in LANGS.items() if k != CUR["code"])
    else:
        seo = '  <meta name="robots" content="noindex">\n'
        og_url = ""
        og_alt = ""
    return f"""<!DOCTYPE html>
<html lang="{CUR['code']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
{seo}  <link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{p}favicon.png" sizes="96x96" type="image/png">
  <link rel="apple-touch-icon" href="{p}apple-touch-icon.png">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Xavier You">
  <meta property="og:locale" content="{CUR['locale']}">
{og_alt}  <meta property="og:title" content="{esc(ogt)}">
  <meta property="og:description" content="{esc(desc)}">
{og_url}  <meta property="og:image" content="{BASE_URL}/images/{OG_FILE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}css/style.css">
</head>
<body>
"""


def lang_switch(kind, slug, cls):
    parts = []
    for lc in LANGS:
        if lc == CUR["code"]:
            parts.append(f'<span aria-current="true">{lc.upper()}</span>')
        else:
            parts.append(f'<a href="{href_to(lc, kind, slug)}" hreflang="{lc}" lang="{lc}" title="{SWITCH_LABEL[lc]}">{lc.upper()}</a>')
    return parts


def nav(kind="index", slug=None):
    drop = "\n".join(f'          <a href="{spage(s)}">{esc(s["title"])}</a>' for s in SERIES)
    mob = "\n".join(f'    <a href="{spage(s)}">{esc(s["title"])}</a>' for s in SERIES)
    sw = lang_switch(kind, slug, "")
    sw_desk = "\n".join("        " + x for x in sw)
    sw_mob = "\n".join("      " + x for x in sw)
    about, contact = fname(CUR["code"], "about"), fname(CUR["code"], "contact")
    return f"""
  <!-- Navbar -->
  <nav class="navbar">
    <a href="index.html" class="navbar-brand" aria-label="{tr('home_label')}"><img src="{CUR['prefix']}images/logo-xy.svg" alt="Xavier You" width="605" height="324"></a>
    <ul class="navbar-links">
      <li class="dropdown">
        <button class="dropdown-toggle" type="button">PORTFOLIO</button>
        <div class="dropdown-menu">
{drop}
        </div>
      </li>
      <li><a href="{about}">{tr('nav_about')}</a></li>
      <li><a href="{contact}">{tr('nav_contact')}</a></li>
      <li class="nav-social"><a href="{IG_URL}" target="_blank" rel="noopener" aria-label="Instagram @xavieryou_officiel" title="Instagram @xavieryou_officiel">{IG_ICON}</a></li>
      <li class="lang-switch">
{sw_desk}
      </li>
    </ul>
    <button class="navbar-toggle" type="button" aria-label="Menu">
      <span></span>
      <span></span>
      <span></span>
    </button>
  </nav>

  <div class="mobile-menu">
{mob}
    <a href="{about}">{tr('mob_about')}</a>
    <a href="{contact}">{tr('mob_contact')}</a>
    <a href="{IG_URL}" class="mobile-insta" target="_blank" rel="noopener">Instagram @xavieryou_officiel</a>
    <div class="mobile-lang">
{sw_mob}
    </div>
  </div>
"""


def footer():
    lis = "\n".join(f'          <li><a href="{spage(s)}">{esc(s["title"])}</a></li>' for s in SERIES)
    about, contact = fname(CUR["code"], "about"), fname(CUR["code"], "contact")
    return f"""
  <!-- Footer -->
  <footer class="footer">
    <div class="footer-wrapper">
      <div class="footer-col">
        <a href="index.html" class="footer-logo-link"><img class="footer-logo" src="{CUR['prefix']}images/logo.svg" alt="{esc(tr('logo_alt'))}" width="605" height="580" loading="lazy"></a>
        <p class="footer-description">{tr('footer_desc')}</p>
        <a href="mailto:contact@xavieryou.com" class="footer-contact-link">contact@xavieryou.com</a>
        <a href="https://www.instagram.com/xavieryou_officiel/" class="footer-contact-link" target="_blank" rel="noopener">Instagram @xavieryou_officiel</a>
      </div>
      <div class="footer-col">
        <ul class="footer-nav">
{lis}
        </ul>
      </div>
      <div class="footer-col">
        <ul class="footer-nav">
          <li><a href="{contact}">{tr('footer_contact')}</a></li>
          <li><a href="{about}">{tr('footer_about')}</a></li>
        </ul>
      </div>
    </div>
    <p class="footer-copyright">{tr('copyright')}</p>
  </footer>

  <script src="{CUR['prefix']}js/main.js"></script>
</body>
</html>
"""


def row_html(items, indent="    "):
    """items : liste de (slug, idx, url_plein_format, caption, alt, eager)
    L'adresse de la photo en grand format est dans data-full (lue par la visionneuse) et non dans le lien :
    le clic droit « Enregistrer le lien sous » ne donne donc pas le fichier."""
    tot = sum(IMG[(a[0], a[1])]["ratio"] for a in items)
    out = [f'{indent}<div class="g-row">']
    for slug, idx, href, caption, alt, eager in items:
        r = IMG[(slug, idx)]["ratio"]
        share = max(1, round(100 * r / tot))
        sizes = f"(max-width: 640px) 100vw, {share}vw"
        lb = f' data-lb data-caption="{esc(caption)}"' if caption else ""
        out.append(f'{indent}  <a class="g-item" id="photo-{idx+1}" style="--r:{r:.4f}" href="#photo-{idx+1}" data-full="{href}"{lb}>'
                   f'{img_tag(slug, idx, alt, sizes, eager)}</a>')
    out.append(f"{indent}</div>")
    return "\n".join(out)


# ---------- 4. pages ----------
def write(name, content):
    path = os.path.join(SITE, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("écrit", name, len(content) // 1024, "Ko")


def cards_html():
    cards = []
    for s in SERIES:
        alt = f"{s['title']}, {meta(s)}"
        im = img_tag(s["slug"], s["cover"], alt, "(max-width: 480px) 100vw, (max-width: 1024px) 50vw, 25vw",
                     extra=f' class="card-image" style="object-position:{s["cover_pos"]}"')
        cards.append(f"""      <a href="{spage(s)}" class="card">
        {im}
        <div class="card-content">
          <h2>{esc(s['title'])}</h2>
          <p>{esc(meta(s))}</p>
        </div>
      </a>""")
    return chr(10).join(cards)


def series_cards_block():
    return f"""
  <!-- Séries -->
  <div class="section-title">
    <h2>{tr('series')}</h2>
  </div>

  <div class="cards-section">
    <div class="cards-grid">
{cards_html()}
    </div>
  </div>
"""


def absolutize(h):
    """chemins absolus (la page 404 peut s'afficher à n'importe quelle adresse)"""
    h = re.sub(r'href="(?!mailto:|https?:|/)', 'href="/', h)
    h = h.replace('src="js/', 'src="/js/').replace('src="images/', 'src="/images/')
    return h


def build_404():
    page = head("Page introuvable — Xavier You", "Cette page n'existe pas.", "index", indexable=False)
    page = page.replace('<link rel="stylesheet" href="css/style.css">', '<link rel="stylesheet" href="/css/style.css">')
    page = page.replace('href="favicon', 'href="/favicon').replace('href="apple-touch', 'href="/apple-touch')
    page += absolutize(nav("index"))
    page += """
  <main class="notfound-page">
    <p class="serie-kicker">Erreur 404</p>
    <h1>Page introuvable</h1>
    <p>La page que vous cherchez n'existe pas ou a été déplacée.</p>
    <a href="/index.html" class="btn">retour à l'accueil</a>
    <p class="notfound-alt" lang="en">Page not found. <a href="/en/">Back to the home page</a></p>
    <p class="notfound-alt" lang="it">Pagina non trovata. <a href="/it/">Torna alla home</a></p>
  </main>
"""
    page += absolutize(footer())
    write("404.html", page)


def build_seo():
    pages = [("index", None)] + [("serie", s["slug"]) for s in SERIES] + [("about", None), ("contact", None)]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for lc in LANGS:
        for kind, slug in pages:
            sm.append("  <url>")
            sm.append(f"    <loc>{abs_url(lc, kind, slug)}</loc>")
            for l2 in LANGS:
                sm.append(f'    <xhtml:link rel="alternate" hreflang="{l2}" href="{abs_url(l2, kind, slug)}"/>')
            sm.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("fr", kind, slug)}"/>')
            sm.append("  </url>")
    sm.append("</urlset>")
    write("sitemap.xml", chr(10).join(sm) + chr(10))
    write("robots.txt", f"User-agent: *{chr(10)}Allow: /{chr(10)}{chr(10)}Sitemap: {BASE_URL}/sitemap.xml{chr(10)}")


def build_index():
    hs_, hi_ = HERO
    hero_img = img_tag(hs_, hi_, tr("hero_alt"), "(max-width: 1024px) 100vw, 50vw", eager=True,
                       extra=f' style="object-position:{HERO_POS}"')
    page = head(tr("home_title"), tr("home_desc"), "index")
    page += nav("index")
    page += f"""
  <!-- Hero split 50/50 -->
  <section class="hero">
    <div class="hero-wrapper">
      <div class="hero-image-col">
        {hero_img}
      </div>
      <div class="hero-text-col">
        <h1 class="hero-title">{tr('tagline')}</h1>
        <p class="hero-description">{tr('hero_desc')}</p>
        <a href="{fname(CUR['code'], 'contact')}" class="btn">{tr('contact_btn')}</a>
      </div>
    </div>
  </section>

  <div class="spacer-md"></div>

  <!-- Séries -->
  <div class="section-title">
    <h2>{tr('series')}</h2>
  </div>

  <div class="cards-section">
    <div class="cards-grid">
{cards_html()}
    </div>
  </div>

  <div class="spacer-lg"></div>

  <!-- À propos (extrait du texte de Xavier) -->
  <div class="approche-section">
    <h2>{tr('mob_about')}</h2>
    <p>{tr('about_teaser')}</p>
    <a href="{fname(CUR['code'], 'about')}" class="btn">{tr('about_btn')}</a>
  </div>

  <div class="spacer-md"></div>
"""
    page += footer()
    write(CUR["dir"] + "index.html", page)


def build_series(i):
    s = SERIES[i]
    n_s = len(SERIES)
    prev, nxt = SERIES[(i - 1) % n_s], SERIES[(i + 1) % n_s]
    n = len(s["files"])
    rows = []
    for ri, r in enumerate(s["rows"]):
        items = []
        for idx in r:
            href = f"{CUR['prefix']}images/{s['slug']}/{idx+1:02d}-2400.webp"
            cap = f"{s['title']} — {idx+1} / {n}"
            alt = tr("photo_alt").format(title=s["title"], meta=meta(s), i=idx + 1, n=n)
            items.append((s["slug"], idx, href, cap, alt, ri == 0 and idx == r[0]))
        rows.append(row_html(items, "    "))
    page = head(f"{s['title']} — Xavier You",
                tr("serie_desc").format(title=s["title"], meta=meta(s)),
                "serie", s["slug"])
    page += nav("serie", s["slug"])
    page += f"""
  <main class="serie-page">
    <header class="serie-head">
      <p class="serie-kicker">{tr('kicker').format(i=i+1, n=n_s)}</p>
      <h1>{esc(s['title'])}</h1>
      <p class="serie-meta">{esc(meta(s))}</p>
    </header>

    <div class="serie-gallery">
{chr(10).join(rows)}
    </div>

    <nav class="serie-nav" aria-label="{esc(tr('other_series'))}">
      <a class="serie-nav-link" href="{spage(prev)}">
        <span class="serie-nav-label">{tr('prev')}</span>
        <span class="serie-nav-title">{esc(prev['title'])}</span>
      </a>
      <a class="serie-nav-link serie-nav-next" href="{spage(nxt)}">
        <span class="serie-nav-label">{tr('next')}</span>
        <span class="serie-nav-title">{esc(nxt['title'])}</span>
      </a>
    </nav>
  </main>

  <div class="spacer-md"></div>
"""
    page += footer()
    write(CUR["dir"] + spage(s), page)


def build_about():
    paras = "\n".join(f"          <p>{p}</p>" for p in tr("about_text"))
    page = head(tr("about_title"), tr("about_desc"), "about")
    page += nav("about")
    page += f"""
  <!-- About (layout Blanchard : label gauche, contenu droite) -->
  <main class="about-page">

    <div class="about-wrapper">
      <div class="about-label-col">
        <h3 class="about-label">{tr('about_label')}</h3>
      </div>
      <div class="about-content-col">
        <h1 class="about-title">{tr('tagline')}</h1>
        <div class="about-text">
{paras}
        </div>
        <div style="margin-top: 32px;">
          <a href="{fname(CUR['code'], 'contact')}" class="btn">{tr('about_btn2')}</a>
        </div>
      </div>
    </div>

  </main>

  <div class="spacer-lg"></div>
"""
    page += series_cards_block()
    page += chr(10) + '  <div class="spacer-lg"></div>' + chr(10)
    page += footer()
    write(CUR["dir"] + fname(CUR["code"], "about"), page)


def build_contact():
    cs, ci = CONTACT_PHOTO
    cphoto = img_tag(cs, ci, tr("contact_alt"), "(max-width: 1024px) 100vw, 40vw")
    links = "\n".join(f'          <a href="{spage(s)}">Portfolio — {esc(s["title"])}</a>' for s in SERIES)
    page = head(tr("contact_title"), tr("contact_desc"), "contact")
    page += nav("contact")
    page += f"""
  <!-- Contact -->
  <main class="contact-page">

    <div class="contact-wrapper">
      <div class="contact-info-col">
        <h1>Contact</h1>
        <p>{tr('contact_text')}</p>

        <div class="contact-details">
          <a href="mailto:contact@xavieryou.com">contact@xavieryou.com</a>
          <a href="https://www.instagram.com/xavieryou_officiel/" target="_blank" rel="noopener">Instagram @xavieryou_officiel</a>
        </div>

        <div class="contact-links-col">
          <h3>{tr('links_title')}</h3>
{links}
        </div>
      </div>

      <div class="contact-photo-col">
        {cphoto}
      </div>
    </div>

  </main>

  <div class="spacer-lg"></div>
"""
    page += footer()
    write(CUR["dir"] + fname(CUR["code"], "contact"), page)


for lc in LANGS:
    CUR = LANGS[lc]
    build_index()
    for i in range(len(SERIES)):
        build_series(i)
    build_about()
    build_contact()

CUR = LANGS["fr"]
build_404()
build_seo()

print("OK")
