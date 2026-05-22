import os
import json
import genanki
import sys

BASE_DIR = os.path.dirname(__file__)
ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "decks")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "processed_data.json")

MODEL_ID = 1607392026
TERMS_DECK_ID = 2059381026
TECHNIQUES_DECK_ID = 1928301928

# Custom CSS styling for cards
CSS_STYLE = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 18px;
  color: #333333;
  background-color: #f9f9f9;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  max-width: 600px;
  margin: 0 auto;
}
.term-title {
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 15px;
  color: #1a73e8;
}
.definition-body {
  line-height: 1.6;
  margin-top: 15px;
  font-size: 19px;
}
.image-container {
  text-align: center;
  margin-top: 20px;
  border-top: 1px solid #eeeeee;
  padding-top: 15px;
}
.image-container img {
  max-width: 100%;
  max-height: 280px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
hr#answer {
  border: 0;
  height: 1px;
  background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.15), rgba(0, 0, 0, 0));
  margin: 20px 0;
}
.tag-badge {
  display: inline-block;
  background-color: #e8f0fe;
  color: #1a73e8;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 15px;
}
"""

# Define the Anki Model (Note Type)
# We have 4 fields: Term, Definition, ImageHTML, TypeTag
climbing_model = genanki.Model(
    MODEL_ID,
    'Climbing Term Model',
    fields=[
        {'name': 'Term'},
        {'name': 'Definition'},
        {'name': 'ImageHTML'},
        {'name': 'TypeTag'},
    ],
    templates=[
        {
            'name': 'Term -> Definition',
            'qfmt': '<div class="term-title">{{Term}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="definition-body">{{Definition}}</div>{{#ImageHTML}}<div class="image-container">{{ImageHTML}}</div>{{/ImageHTML}}<div class="tag-badge">{{TypeTag}}</div>',
        },
        {
            'name': 'Definition -> Term',
            'qfmt': '<div class="definition-body">{{Definition}}</div>{{#ImageHTML}}<div class="image-container">{{ImageHTML}}</div>{{/ImageHTML}}',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="term-title" style="color: #34a853;">{{Term}}</div><div class="tag-badge">{{TypeTag}}</div>',
        },
    ],
    css=CSS_STYLE
)

def generate():
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"Error: {PROCESSED_DATA_PATH} does not exist.")
        return

    with open(PROCESSED_DATA_PATH, "r") as f:
        data = json.load(f)

    # Initialize decks
    terms_deck = genanki.Deck(TERMS_DECK_ID, 'Climbing Terms')
    techniques_deck = genanki.Deck(TECHNIQUES_DECK_ID, 'Climbing Techniques')

    # Track media files to package
    media_files = []

    terms_count = 0
    techniques_count = 0

    for item in data:
        term = item["term"]
        definition = item["definition_cleaned"]
        image_file = item["image_file"]
        is_tech = item["is_technique"]

        # Prepare Image HTML
        image_html = ""
        if image_file:
            image_path = os.path.join(IMAGES_DIR, image_file)
            if os.path.exists(image_path):
                image_html = f'<img src="{image_file}">'
                media_files.append(image_path)
            else:
                print(f"Warning: Image file not found: {image_path}")

        type_tag = "Technique" if is_tech else "Term"

        # Create note
        note = genanki.Note(
            model=climbing_model,
            fields=[term, definition, image_html, type_tag]
        )

        # Add to terms deck (all terms)
        terms_deck.add_note(note)
        terms_count += 1

        # Add to techniques deck if applicable
        if is_tech:
            techniques_deck.add_note(note)
            techniques_count += 1

    # Ensure ARTIFACT_DIR exists.
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    # Write Terms Deck Package
    terms_package_path = os.path.join(ARTIFACT_DIR, "climbing terms.apkg")
    terms_package = genanki.Package(terms_deck)
    terms_package.media_files = media_files
    terms_package.write_to_file(terms_package_path)
    print(f"Generated {terms_package_path} with {terms_count} terms (packaged {len(media_files)} images).")

    # Write Techniques Deck Package
    # The techniques package only needs the media files that are actually used in the techniques deck.
    # Let's filter media files for techniques.
    tech_media_files = []
    for item in data:
        if item["is_technique"] and item["image_file"]:
            image_path = os.path.join(IMAGES_DIR, item["image_file"])
            if os.path.exists(image_path):
                tech_media_files.append(image_path)

    techniques_package_path = os.path.join(ARTIFACT_DIR, "climbing techniques.apkg")
    techniques_package = genanki.Package(techniques_deck)
    techniques_package.media_files = tech_media_files
    techniques_package.write_to_file(techniques_package_path)
    print(f"Generated {techniques_package_path} with {techniques_count} techniques (packaged {len(tech_media_files)} images).")

if __name__ == "__main__":
    generate()
