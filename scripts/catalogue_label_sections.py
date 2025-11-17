# scripts/catalogue_label_sections.py

from pathlib import Path
import csv
from collections import Counter
from datetime import datetime

# Input from previous step; output for next step
CATALOG_IN = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram.csv")
CATALOG_OUT = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_labeled.csv")

# SECTION_KEYWORDS, ORIGAMI_SUBSECTIONS, SECTION_PRIORITY
"""Label the "Catalogue" items with Sections and Subsections which will be used on the webpage"""

SECTION_KEYWORDS = {
    "origami": [
        # existing
        "origami", "paper", "tessellation", "tesselation", "modular", "fold", "crease",
        # extra general origami-ish
        "advancedorigami", "complexorigami", "supercomplexorigami",
        "paperart", "paperartwork", "papercraft", "paperflowers", "paperfolding",
        "tissuefoil", "methylcellulose", "grid", "geometric", "geometricart",
        "pattern", "patterns", "diagrams",
        # modular / special
        "kusudama", "sonobe", "shadowfold",
        # hashtaggy origami variants (many already caught via "origami")
        "origamiart", "origamianimals", "origamibugs", "origamiflower",
        "origamiflowers", "origamifrog", "origamiinsect", "origamiinsects",
        "origamiphoenix", "origamitessellation", "origamitessellations",
        "origamitesselations", "origamitreefrog", "origamiturtle", "origamiwolf",
    ],

    "powerlifting": [
        # existing
        "powerlifting", "squat", "deadlift", "bench", "benchpress", "bench press",
        "deadlifted", "squatted",
        # lifting context
        "powerlifters", "britishpowerlifting", "britishpowerliftingladies",
        "britishpowerliftingwomen", "ipf", "theipf", "wilks",  "lifted", "lifting", "lifts",
        "bodyweight", "bodybuilding", "bodybuildingprogress", "bulkingup",
        "gym", "gymwear", "gymclothing",
        "strength", "strong", "strongwomen", "hench",
        # community tags
        "girlswholift", "girlswhopowerlift",
        "ironladies", "ironladiesuk", "ipreferpowerlifting",
        "over40fitness", "over40strength", "fitover40",
        # training / coaching
        "athlete", "athletes", "coach", "coaching",
        "training", "trainhard", "workout",
        "natrualbodybuilder",  # keeping your actual typo to catch it
    ],

    "makeup": [
        # existing
        "makeup", "eyeshadow", "eye shadow", "eyeliner", "lipstick", "blush", "contour",
        "highlighter", "palette", "brightmakeup", "ilovemakeup", "brightcolours","multichrome"
        # brands / meta
        "ilovemakeup", "makeupobsession", "makeuprevolution", "makeupbytammi",
        "gothmakeup", "sleekmakeup", "iheartrevolution", "joliebeauty","kaleidosmakeup"
        # eye-related
        "eyelid", "eyebrow", "eyemakeup",
        "eyeshadows", "eyeshadowlooks", "eyeshadowismorefun",
        "brighteyeshadow", "eyesinfive",
        # lips / face
        "lips", "lipsticks", "blacklipstick", "bluelipstick", "darklipstick",
        "contouring",
        # colour / finish
        "palette", "palettes", "pigment", "pigmented", "pigments",
        "glitter", "glittery", "shimmer", "shimmers", "shimmery",
        "duochrome", "duochromeeyeshadow",
        # named palettes
        "sorceresspalette", "tropicalcarnivalpalette", "slimepalette",
    ],

    "activism": [
        # existing + some obvious extras from your list
        "nova", "trans", "transgender", "transition",
        "racism", "racist", "antiracism", "antiracismuk", "antiracistpractice",
        "blm", "blacklivesmatter",
        "systemicracism", "decoloniseyourmindfirst", "unlearnandrelearn",
        "representationmatters",
        "activism", "activist", "activists", "protest", "protests",
        "march", "ukblackpride", "wowfestival", "wowglobal", "wowldn",
        "birthrights", "birthrightsorg", "grenfell",
    ],

        "craft": [
        # existing + some obvious extras from your list
        "crochet",
    ],

    "singing": [
        # existing
        "sang", "sung", "singing", "song", "karaoke", "cover",
        # music / performance
        "exmusician", "musician", "musicians",
        "performance", "performed", "performer",
        # busking / tunes
        "busk", "busking", "oldbuskingtunes", "tune", "tunes",
        "robsingers",
        "viola",  # if your viola posts are in this category
    ],
}

ORIGAMI_SUBSECTIONS = {
    "insects": [
        "insect", "insects", "bug", "bugs",
        "camel",
        "beetle", "beetles", "scarab",
        "wasp", "yellowjacket", "yellowjacketwasp",
        "camelspider", "spider", "tarantula", "scorpion",
        "silverfish", "pillbug", "woodlouse",
        "centipede",
        "eupatorus", "gracilicornis", "titanbeetle", "herculesbeetle",
        "rhinocerosbeetle", "titan",
        "acrocinus", "acrocinuslongimanus",
        "dragonfly", "origamidragonfly",
    ],

    "animals": [
        "animal", "animals", "adorableanimals", "easteranimals",
        "origamianimals",
        "bird", "birds", "birdsofparadise", "flyingbirds", "duck", "fish",
        "frog", "treefrog", "origamifrog", "origamitreefrog",
        "turtle", "seaturtle", "origamiturtle",
        "hedgehog", "crochethedgehog",
        "dormouse",
        "sloth", "sloths", "duncanthesloth", "crochetedsloth",
        "flamingos",
        "redpanda",
        "wolf", "greywolf", "graywolf", "origamiwolf",
        "unicorn",
        "mouse",
        "parrot",
        "dragon", "dragons", "phoenix", "origamiphoenix",
    ],

    "tessellations": [
        "tessellation", "tessellations",
        "tesselation", "tesselations",
        "tesselated", "tesselating",
        "origamitessellation", "origamitessellations", "origamitesselations",
        "grid", "hexagonal", "squares",
    ],

    "curved": [
        "curved", "curvedorigami",
        "swirly", "twirl", "circle", "circles",
    ],

    "modular": [
        "modular", "modularorigami",
        "unit", "units", "kusudama", "sonobe",
        "assemble", "assembled", "assembly",
    ],

    # default: "general" (handled in the function below)
}

SECTION_PRIORITY = [
    "activism",
    "origami",
    "powerlifting",
    "makeup",
    "craft",
    "singing",
]


def infer_section_and_matches(caption: str):
    """
    Return (section, debug_string), where:
      - section is the chosen top-level section (or 'general')
      - debug_string describes which keywords matched per section, e.g.
        'origami: origami, fold; powerlifting: squat'

    Strategy:
      1. Collect all keyword hits per section.
      2. Choose the section with the MOST hits.
      3. If there's a tie on count, break it using SECTION_PRIORITY.
    """
    if not caption:
        return "general", ""

    text = caption.lower()
    matches_per_section = {}

    for section, keywords in SECTION_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            matches_per_section[section] = hits

    if not matches_per_section:
        return "general", ""

    # --- majority-vote by number of hits ---
    # e.g. powerlifting: 1 hit, makeup: 5 hits -> choose makeup
    counts = {sec: len(hits) for sec, hits in matches_per_section.items()}
    max_count = max(counts.values())
    top_sections = [sec for sec, c in counts.items() if c == max_count]

    if len(top_sections) == 1:
        chosen_section = top_sections[0]
    else:
        # tie: use SECTION_PRIORITY to break it
        chosen_section = None
        for sec in SECTION_PRIORITY:
            if sec in top_sections:
                chosen_section = sec
                break
        if chosen_section is None:
            # fallback: just pick one deterministically
            chosen_section = sorted(top_sections)[0]

    # Build debug string: "section (N): kw1, kw2; section2 (M): kw3"
    parts = []
    for sec, hits in matches_per_section.items():
        parts.append(f"{sec} ({len(hits)}): {', '.join(hits)}")
    debug_string = "; ".join(parts)

    return chosen_section, debug_string


def infer_origami_subsection(caption: str) -> str:
    """Return origami subsection based on keywords. Default = 'general'."""
    if not caption:
        return "general"

    text = caption.lower()

    for subsection, keywords in ORIGAMI_SUBSECTIONS.items():
        for kw in keywords:
            if kw in text:
                return subsection

    return "general"

def infer_powerlifting_subsection(date_str: str) -> str:
    """Extract year as subsection. date_str usually an ISO string."""
    if not date_str:
        return ""
    try:
        year = datetime.fromisoformat(date_str).year
        return str(year)
    except Exception:
        # fallback: take first 4 digits if present
        if len(date_str) >= 4 and date_str[:4].isdigit():
            return date_str[:4]
        return ""


def label_catalogue(
    catalog_in: Path = CATALOG_IN,
    catalog_out: Path = CATALOG_OUT,
):
    section_counts = Counter()
    origami_subsection_counts = Counter()
    powerlifting_year_counts = Counter()
    total_rows = 0

    with catalog_in.open("r", encoding="utf-8", newline="") as f_in, \
         catalog_out.open("w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)

        if "section" not in fieldnames:
            fieldnames.append("section")
        if "subsection" not in fieldnames:
            fieldnames.append("subsection")
        if "section_keyword_hits" not in fieldnames:
            fieldnames.append("section_keyword_hits")

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total_rows += 1
            caption = row.get("caption", "") or ""
            date_str = row.get("post_datetime", "") or ""

            section, hits_debug = infer_section_and_matches(caption)
            row["section"] = section
            row["section_keyword_hits"] = hits_debug

            subsection = ""
            if section == "origami":
                subsection = infer_origami_subsection(caption)
                origami_subsection_counts[subsection] += 1
            elif section == "powerlifting":
                subsection = infer_powerlifting_subsection(date_str)
                powerlifting_year_counts[subsection] += 1
            elif section == "general":
                subsection = "general"

            row["subsection"] = subsection

            if section:
                section_counts[section] += 1

            writer.writerow(row)

    print(f"\nWrote {total_rows} rows → {catalog_out}\n")
    # (You can keep your summary prints if you like)

if __name__ == "__main__":
    label_catalogue()
