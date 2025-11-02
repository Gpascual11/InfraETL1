from pipeline import ETLPipeline

def main():
    API_URL = "https://randomuser.me/api/"
    print("1. Choose number of users manually")
    print("2. Use default: 10,000 EU/LATAM users")

    choice = input("Enter option (1 or 2): ").strip()

    if choice == "1":
        try:
            n_users = int(input("Enter number of users: "))
            if n_users <= 0:
                raise ValueError
        except ValueError:
            print("Invalid number, defaulting to 10,000.")
            n_users = 10000
    else:
        n_users = 10000

    # Run the unified pipeline
    pipeline = ETLPipeline(api_url=API_URL, n_users=n_users, output_dir="output")
    pipeline.run()

if __name__ == "__main__":
    main()
