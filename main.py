# ===============================
# MAIN
# ===============================
from pipeline import ETLPipeline

if __name__ == "__main__":
    API_URL = "https://randomuser.me/api/"
    N_USERS = 5000

    etl = ETLPipeline(API_URL, N_USERS)
    etl.run()
