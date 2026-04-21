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
        print("8. import-vault")
        print("9. exit")

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
            handle_import_vault()
        elif choice == "9":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")