from pipeline import ETLPipeline
from extractor import Extractor
from transformer import Transformer
from loader import Loader

def main():
    API_URL = "https://randomuser.me/api/"
    print("===== ETL System =====")
    print("1. Choose number of users manually")
    print("2. Use default: 10000 EU/LATAM users")
    choice = input("Enter your option (1 or 2): ").strip()

    if choice == "1":
        try:
            n_users = int(input("Enter the number of EU/LATAM users to collect: "))
        except ValueError:
            print("Invalid number, using default 10000.")
            n_users = 10000
    else:
        n_users = 10000

    extractor = Extractor(API_URL, total_users=n_users)
    users = extractor.extract()

    transformer = Transformer(users)
    stats = transformer.generate_stats()
    users_processed = transformer.get_users()

    loader = Loader("output")
    loader.save_to_files(users_processed, stats)

    print("ETL process finished successfully.")


if __name__ == "__main__":
    main()
