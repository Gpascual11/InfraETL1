# ===============================
# MAIN ETL PIPELINE EXECUTION
# ===============================

from extractor import Extractor
from transformer import Transformer
from loader import Loader


def main():
    """
    Entry point of the ETL system.
    Allows the user to choose between a custom number of users
    or a default option (10,000 EU/LATAM users).
    """
    API_URL = "https://randomuser.me/api/"

    print("=================================")
    print("        ETL SYSTEM START         ")
    print("=================================")
    print("1. Choose number of users manually")
    print("2. Use default: 10,000 EU/LATAM users")
    print("---------------------------------")

    # Ask the user which mode to use
    choice = input("Enter your option (1 or 2): ").strip()

    # Option 1 → user inputs number manually
    if choice == "1":
        try:
            n_users = int(input("Enter the number of EU/LATAM users to collect: "))
            if n_users <= 0:
                raise ValueError
        except ValueError:
            print("Invalid number, using default (10,000).")
            n_users = 10000
    else:
        n_users = 10000

    print(f"\nTarget: {n_users} users from EU and LATAM countries.\n")

    # ===============================
    # STEP 1: EXTRACT
    # ===============================
    extractor = Extractor(API_URL, total_users=n_users)
    users = extractor.extract()

    # ===============================
    # STEP 2: TRANSFORM
    # ===============================
    transformer = Transformer(users)
    transformer.validate_data()   # Double validation + anomaly check
    stats = transformer.generate_stats()
    users_processed = transformer.get_users()

    # ===============================
    # STEP 3: LOAD
    # ===============================
    loader = Loader("output")
    loader.save_to_files(users_processed, stats)

    # ===============================
    # FINISH
    # ===============================
    print("\nETL process finished successfully.")
    print(f"Total valid users saved: {len(users_processed)}")
    print("Output files stored in the 'output' folder.\n")


# Standard Python convention — runs only if executed directly
if __name__ == "__main__":
    main()
