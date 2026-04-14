from config.db import init_db


def main() -> None:
	init_db()
	print("Database tables initialized successfully.")


if __name__ == "__main__":
	main()
