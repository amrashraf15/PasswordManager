import streamlit as st

from vault.vault_manager import (
    initialize_user,
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
)
from vault.signer import verify_user_vault
from exchange.exporter import secure_export_vault


st.set_page_config(
    page_title="Secure Password Manager",
    page_icon="",
    layout="centered",
)


def safe_action(action):
    try:
        action()

    except FileNotFoundError as e:
        st.error(str(e))

    except ValueError as e:
        st.error(str(e))

    except KeyError:
        st.error("Invalid vault structure. The vault file may be corrupted.")

    except Exception as e:
        st.error("Unexpected error occurred.")
        st.exception(e)


def required(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")

    return value.strip()


st.title(" Secure Password Manager")
st.caption("AES-GCM Encryption | SHA-256 | ElGamal Digital Signature")

operation = st.sidebar.selectbox(
    "Choose Operation",
    [
        "Initialize User",
        "Add Credential",
        "Get Credential",
        "Update Credential",
        "Delete Credential",
        "Verify Vault",
        "Export Vault",
    ],
)


if operation == "Initialize User":
    st.header("Initialize New User")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")

    if st.button("Create User"):
        def action():
            clean_username = required(username, "Username")
            clean_master_password = required(master_password, "Master password")

            initialize_user(clean_username, clean_master_password)

            st.success("User initialized successfully.")

        safe_action(action)


elif operation == "Add Credential":
    st.header("Add Credential")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")
    site = st.text_input("Site")
    login_identifier = st.text_input("Login Identifier")
    password = st.text_input("Password", type="password")

    if st.button("Add Credential"):
        def action():
            clean_username = required(username, "Username")
            clean_master_password = required(master_password, "Master password")
            clean_site = required(site, "Site")
            clean_login_identifier = required(login_identifier, "Login identifier")
            clean_password = required(password, "Password")

            add_credential(
                clean_username,
                clean_master_password,
                clean_site,
                clean_login_identifier,
                clean_password,
            )

            st.success("Credential added successfully.")

        safe_action(action)


elif operation == "Get Credential":
    st.header("Get Credential")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")
    site = st.text_input("Site")

    if st.button("Get Credential"):
        def action():
            clean_username = required(username, "Username")
            clean_master_password = required(master_password, "Master password")
            clean_site = required(site, "Site")

            cred = get_credential(
                clean_username,
                clean_master_password,
                clean_site,
            )

            if cred is None:
                st.warning("Credential not found.")
            else:
                st.success("Credential found.")

                st.write("### Credential Details")
                st.write(f"**Site:** {cred['site']}")
                st.write(f"**Login Identifier:** {cred['login_identifier']}")
                st.code(cred["password"], language=None)

        safe_action(action)


elif operation == "Update Credential":
    st.header("Update Credential")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")
    site = st.text_input("Site")
    new_login_identifier = st.text_input("New Login Identifier")
    new_password = st.text_input("New Password", type="password")

    if st.button("Update Credential"):
        def action():
            clean_username = required(username, "Username")
            clean_master_password = required(master_password, "Master password")
            clean_site = required(site, "Site")
            clean_login_identifier = required(new_login_identifier, "New login identifier")
            clean_password = required(new_password, "New password")

            update_credential(
                clean_username,
                clean_master_password,
                clean_site,
                clean_login_identifier,
                clean_password,
            )

            st.success("Credential updated successfully.")

        safe_action(action)


elif operation == "Delete Credential":
    st.header("Delete Credential")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")
    site = st.text_input("Site")

    confirm_delete = st.checkbox("I confirm that I want to delete this credential.")

    if st.button("Delete Credential"):
        def action():
            if not confirm_delete:
                raise ValueError("Please confirm deletion first.")

            clean_username = required(username, "Username")
            clean_master_password = required(master_password, "Master password")
            clean_site = required(site, "Site")

            delete_credential(
                clean_username,
                clean_master_password,
                clean_site,
            )

            st.success("Credential deleted successfully.")

        safe_action(action)


elif operation == "Verify Vault":
    st.header("Verify Vault Integrity")

    username = st.text_input("Username")

    if st.button("Verify Vault"):
        def action():
            clean_username = required(username, "Username")

            result = verify_user_vault(clean_username)

            if result:
                st.success("Vault signature is valid.")
            else:
                st.error("Vault signature is INVALID! The vault may have been tampered with.")

        safe_action(action)


elif operation == "Export Vault":
    st.header("Export Vault")

    sender_username = st.text_input("Sender Username")
    sender_password = st.text_input("Sender Master Password", type="password")
    recipient_username = st.text_input("Recipient Username")
    recipient_password = st.text_input("Recipient Master Password", type="password")

    if st.button("Export Vault"):
        def action():
            clean_sender = required(sender_username, "Sender username")
            clean_sender_pwd = required(sender_password, "Sender master password")
            clean_recipient = required(recipient_username, "Recipient username")
            clean_recipient_pwd = required(recipient_password, "Recipient master password")

            success = secure_export_vault(clean_sender, clean_sender_pwd, clean_recipient, clean_recipient_pwd)

            if success:
                st.success("Vault exported and imported successfully.")
            else:
                st.error("Export failed.")

        safe_action(action)
