"""Seed the SQLite database with scheme data."""

import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db, insert_scheme, get_all_schemes
from app.schemes_data import SCHEMES


def main():
    print("🗄️  Initializing database...")
    init_db()

    print(f"📝 Inserting {len(SCHEMES)} schemes...")
    for scheme in SCHEMES:
        insert_scheme(scheme)
        print(f"  ✅ {scheme.id}: {scheme.name_en}")

    # Verify
    all_schemes = get_all_schemes()
    print(f"\n✅ Done! {len(all_schemes)} schemes in database.")
    print("\nSchemes loaded:")
    for s in all_schemes:
        print(f"  • {s['name_en']}")


if __name__ == "__main__":
    main()
