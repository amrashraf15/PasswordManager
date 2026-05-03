from cli.commands import (
    handle_init_user,
    handle_add_credential,
    handle_get_credential,
    handle_update_credential,
    handle_delete_credential,
    handle_verify_vault,
    handle_export_vault,
    handle_import_vault,
)


def run_cli():
    while True:
        print("\n=== Secure Password Manager ===")
        print("1. init-user")
        print("2. add-credential")
        print("3. get-credential")
        print("4. update-credential")
        print("5. delete-credential")
        print("6. verify-vault")
        print("7. export-vault")
        print("8. exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            handle_init_user()

        elif choice == "2":
            handle_add_credential()

        elif choice == "3":
            handle_get_credential()

        elif choice == "4":
            handle_update_credential()

        elif choice == "5":
            handle_delete_credential()

        elif choice == "6":
            handle_verify_vault()

        elif choice == "7":
            handle_export_vault()

        elif choice == "8":
            print("Goodbye.")
            break

        else:
            print("Invalid choice. Please choose a number from 1 to 8.")


if __name__ == "__main__":
    run_cli()