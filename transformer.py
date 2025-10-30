# ===============================
# CLASS 2: TRANSFORMER
# ===============================

import pandas as pd

class Transformer:
    """Class responsible for transforming user data and generating statistics"""

    def __init__(self, users: list):
        self.users = users
        self.df = pd.json_normalize(users)

    def generate_stats(self) -> dict:
        print(" Generating statistics...")
        stats = {
            "total_usuarios": len(self.df),
            "promedio_edad": round(self.df["dob.age"].mean(), 2),
            "edad_minima": int(self.df["dob.age"].min()),
            "edad_maxima": int(self.df["dob.age"].max()),
            "genero_mas_frecuente": self.df["gender"].mode()[0],
            "paises_distintos": self.df["location.country"].nunique(),
        }
        return stats

# Using type hinting for better clarity
    def get_dataframe(self) -> pd.DataFrame:
        return self.df