# Analyse complète — blanchardelisa.com (reference site)

Capturee le 23 mars 2026.

## Stack technique
- Webflow (site genere)
- CSS : fichier webflow shared
- Fonts Google : Bricolage Grotesque, DM Sans, Outfit, Lato, Montserrat

## Design tokens

| Token | Valeur |
|-------|--------|
| Fond global | `rgb(253, 252, 250)` (blanc casse) |
| Couleur texte | `rgb(48, 48, 48)` |
| Typo titres (h1, h2) | Bricolage Grotesque, 500, 30px/22.4px |
| Typo body | DM Sans, 300, 15px, line-height 19px |
| Typo about | Outfit, 300, 17px |
| Grilles images | CSS Grid, 4 colonnes, gap 5px |
| Ratio images | ~2:3 (361x541px) |
| Boutons | border-radius 20px, bg rgba(255,255,255,0.5), padding 10px 15px |
| Navbar | position fixed, bg rgb(253,252,250) |

## Structure des pages

### 1. Accueil (/)
```
navbar-home-2025 (fixed)
  logo "ELISA BLANCHARD" (lien /)
  nav: PRESTATIONS (dropdown: Fashion, Commercial, Portrait, Evenementiel) | A PROPOS | CONTACT
  burger menu (mobile)

page-wrapper-home
  hero-heading-right-2 (section)
    container-13 (flex, justify-between)
      hero-wrapper-3 (flex row, h~604px)
        hero-split-2 (flex col, w~666px) -> IMG shadow-two-2 (grande image)
        hero-split-3 (flex col, w~666px) -> H1 + P + lien "me contacter"

  section-respiration (spacer)

  section-titre-home-1 -> H2 "Prestations"

  section-carte-4 (flex row, gap 16px)
    grid-book-4 (grid, 4 cols, gap 5px)
      carte-4 x4 (flex col)
        card-content-3 -> H2 "FASHION" / "COMMERCIAL" / "PORTRAIT ET BOOK" / "EVENEMENTIEL"
        lien vers page prestation (avec image de fond)

  section-respiration-8rem (spacer)

  section-titre-2
    H2 "Mon approche"
    P (texte description)
    lien "a propos" (bouton arrondi)

  section-banner-copy (marquee texte defilant, overflow hidden)
    "portrait . commercial . fashion . editorial . set design . reportage . corporate . evenementiel"

  section-6 (galerie)
    grid-3-home x4 (grid, 4 cols, gap 5px)
      img-grid x4 par grille = 16 images total

  section-respiration (spacer)
  s-prateur-footer (separateur)

footer-dark-2
  container-10
    footer-wrapper-2 (flex row)
      col gauche: texte descriptif + tel + email + Instagram + LinkedIn
      col centre: liens prestations
      col droite: liens utiles (Contact, A propos, Fiche google, CGV, Mentions legales, Politique confidentialite)
    copyright
```

### 2. Pages Prestations (template commun)
Pages: /photographe-fashion-editorial-paris-nantes, /photographe-commercial-brand-content-packshot-paris-nantes, /seances-photos-portrait-book-paris-nantes, /photographe-evenementiel-corporate-paris-nantes

```
navbar (identique)

page-wrapper
  hero-heading-right-2 (meme structure que accueil)
    image + H1 titre prestation + P description + lien "ME CONTACTER"

  section-respiration

  section-titre-home-1 -> H2 "Portfolio [nom]"

  section-6 (galerie)
    grid-3-home (grid 4 cols, gap 5px)
      images (quantite variable: 18-31 selon page)

  section-respiration
  s-prateur-footer

footer (identique)
```

Note: la page Portrait est plus riche (sections infos seance, polas, options, mariage).

### 3. A propos (/a-propos)
```
navbar (identique)

page-wrapper
  section-respiration-avant-footer

  secion-a-propos
    rt-component-section-4 (font: Outfit, 300, 17px)
      rt-component-container-4 (max-width 1290px)
        rt-about-two-expert-wrapper (flex row)
          col gauche: sous-titre "Qui suis-je ?"
          col droite: H2 + paragraphes bio + lien "me contacter"

  section-respiration
  s-prateur

  features-metrics-a-propos (bg rgb(253,252,250))
    titre "Medias, articles et collaborations"
    logo Art&facts
    liens podcast, articles, conferences, collaborations (Adobe, Sigma, SPOT FR)

  section-respiration
  s-prateur-footer

footer (identique)
```

### 4. Contact (/contact)
```
navbar (identique)

page-wrapper
  hero-heading-right-contact (section)
    H2 "Contact"
    P texte d'intro
    lien "ENVOYER MA DEMANDE" (vers tally.so)
    email: contact@blanchardelisa.com
    tel: +33 7 87 00 07 54
    formulaire (prenom, nom, email, type prestation, message, bouton envoyer)
    liens utiles: portfolios (fashion, commercial, portrait, evenementiel)

  section-cta-infos (spacer)

  section-6-contact
    4 images decoratives

  section-respiration
  s-prateur-footer

footer (identique)
```

## Adaptation pour Xavier You-Chirpaz

| Blanchard | Xavier |
|-----------|--------|
| Fond blanc casse | Fond noir / tres sombre |
| Photos couleur | N&B uniquement |
| Hero split 50/50 avec texte | Image plein ecran + nom superpose |
| 4 categories services | Series artistiques |
| Ton commercial (CTA, descriptions) | Zero texte commercial |
| Formulaire contact complet | Email + Instagram seulement |
| Footer complet (tel, liens, CGV) | Email discret + Instagram |
| Sans-serif (Bricolage Grotesque, DM Sans) | Serif fine, elegante |
| Boutons arrondis CTA | Pas de CTA |
