from pipeline import ETLPipeline

def main():
    api_url = "https://randomuser.me/api/"
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
    pipeline = ETLPipeline(api_url=api_url, n_users=n_users)
    pipeline.run()

if __name__ == "__main__":
    main()
