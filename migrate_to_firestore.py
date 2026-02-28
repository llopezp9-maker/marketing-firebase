import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
import pandas as pd

# 1. Configuración de Firebase con Llave de Seguridad
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    # Si ya está inicializado, obtenemos el cliente
    try:
        db = firestore.client()
    except Exception:
        print(f"Error crítico al conectar con Firebase: {e}")

def interpolate(start, end, s_year, e_year, years, type='linear'):
    res = np.zeros(len(years))
    idx_s, idx_e = s_year - 1995, e_year - 1995
    if type == 'linear':
        res[idx_s:idx_e+1] = np.linspace(start, end, idx_e - idx_s + 1)
    else:
        t = idx_e - idx_s
        r = np.log(end / (start if start > 0 else 1)) / t
        res[idx_s:idx_e+1] = start * np.exp(r * np.arange(t + 1))
    return res

def upload_market_data():
    years = np.arange(1995, 2026)
    data = {'Año': years}
    
    data['TV Nacional'] = interpolate(198962, 908657, 1995, 2025, years)
    data['Digital'] = interpolate(40601, 3066685, 2008, 2025, years, 'exp')
    data['Radio'] = interpolate(224891, 560706, 1998, 2025, years)
    data['Prensa'] = interpolate(307647, 206962, 2003, 2025, years)
    data['Exterior'] = interpolate(145738, 328925, 2014, 2025, years)
    data['TV Local'] = interpolate(22970, 61115, 1995, 2025, years)
    data['Revistas'] = interpolate(32751, 6839, 1995, 2025, years)
    
    data['Internet_Penetration'] = interpolate(0.001, 0.757, 1995, 2024, years, 'exp')
    data['Internet_Penetration'][-1] = 0.757

    df = pd.DataFrame(data)
    
    # Subir a la colección 'market_data'
    print("🚀 Iniciando migración de datos a Firestore...")
    col_ref = db.collection('market_data')
    
    for _, row in df.iterrows():
        year_str = str(int(row['Año']))
        # Convertimos a tipos nativos de Python para Firestore
        doc_data = {
            'year': int(row['Año']),
            'tv_nacional': float(row['TV Nacional']),
            'digital': float(row['Digital']),
            'radio': float(row['Radio']),
            'prensa': float(row['Prensa']),
            'exterior': float(row['Exterior']),
            'tv_local': float(row['TV Local']),
            'revistas': float(row['Revistas']),
            'internet_penetration': float(row['Internet_Penetration'])
        }
        col_ref.document(year_str).set(doc_data)
        print(f"✅ Año {year_str} subido con éxito.")

    print("\n✨ Migración completada. Los datos ahora residen en la nube de Firebase.")

if __name__ == "__main__":
    upload_market_data()
