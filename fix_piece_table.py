from app import app, db, Piece
from sqlalchemy import text

with app.app_context():
    # 1. Sauvegarder les données existantes (sauf id)
    pieces = db.session.query(Piece).all()
    sauvegarde = []
    for p in pieces:
        sauvegarde.append({
            'reference_ste': p.reference_ste,
            'reference_magasin': p.reference_magasin,
            'item': p.item,
            'description': p.description,
            'lieu_stockage_id': p.lieu_stockage_id,
            'quantite_stock': p.quantite_stock,
            'stock_mini': p.stock_mini,
            'stock_maxi': p.stock_maxi
        })

    # 2. Supprimer la table piece
    db.session.commit()
    with db.engine.connect() as conn:
        conn.execute(text('DROP TABLE piece'))
        conn.commit()

    # 3. Recréer la table piece avec la bonne structure
    db.create_all()  # recrée toutes les tables manquantes selon les modèles

    # 4. Réinsérer les données sauvegardées
    for data in sauvegarde:
        piece = Piece(**data)
        db.session.add(piece)
    db.session.commit()
    print('Table piece réparée avec succès !') 