from app import app, db
from sqlalchemy import text

with app.app_context():
    # Supprimer la contrainte d'unicité sur reference_ste
    try:
        with db.engine.connect() as conn:
            conn.execute(text("DROP INDEX IF EXISTS ix_piece_reference_ste"))
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text("CREATE TABLE piece_new AS SELECT * FROM piece"))
            conn.execute(text("DROP TABLE piece"))
            conn.execute(text("ALTER TABLE piece_new RENAME TO piece"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
        print("Contrainte d'unicité supprimée avec succès!")
    except Exception as e:
        print(f"Erreur lors de la suppression de la contrainte: {e}") 