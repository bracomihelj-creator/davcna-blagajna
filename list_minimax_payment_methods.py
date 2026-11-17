"""Enkratni pregled načinov plačila za org iz blagajna_minimax_settings.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import DavcnaBlagajna as b  # noqa: E402

SETTINGS = SCRIPT_DIR / "blagajna_minimax_settings.json"


def main() -> None:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    tok = b.minimax_password_oauth_login(
        data["minimax_auth_url"],
        client_id=data["minimax_client_id"],
        client_secret=data["minimax_client_secret"],
        username=data["minimax_api_username"],
        password=data["minimax_api_password"],
        scope=data["minimax_scope"],
    )
    token = tok.get("access_token") or tok.get("AccessToken")
    org = int(data["minimax_org_id"])
    api = data["minimax_api_base"]
    items = b.minimax_fetch_all_payment_methods_paginated(api, token, org)
    print(f"Org {org}: {len(items)} načinov plačila\n")
    for it in items:
        pm_id = b.minimax_payment_method_id_from_item(it)
        code = b.minimax_payment_method_code_from_item(it)
        name = b.minimax_payment_method_name_from_item(it)
        typ = b.minimax_payment_method_type_from_item(it)
        cash = " <-- GOTOVINA" if typ == "G" or b.minimax_payment_method_matches_cash_name(it) else ""
        print(f"  ID {pm_id} | Code '{code}' | Name '{name}' | Type {typ}{cash}")
    found = b.minimax_find_cash_payment_method(items)
    if found:
        print(f"\nPriporočeno za blagajno (Gotovina): Code '{found[1]}' (ID {found[0]}, {found[2]})")
    else:
        print("\nGotovina (Type G) ni bila najdena — preveri šifrant v Minimaxu.")


if __name__ == "__main__":
    main()
