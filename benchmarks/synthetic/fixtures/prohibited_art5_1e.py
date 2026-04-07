# synthetic-test-fixture
"""Synthetic fixture: prohibited untargeted facial database scraping (Article 5(1)(e)).
Expected: classifier should return 'prohibited'."""

def harvest_faces_from_internet():
    """Mass facial collect from public webpages."""
    images = face_scrape_public_sites()
    return build_facial_database_untargeted(images)
