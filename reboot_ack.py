#!/usr/bin/env python3
"""
Acquitte l'alerte de reboot inattendu affichee par le dashboard.

Usage sur le Raspberry :
    python3 reboot_ack.py
"""

from reboot_alert import acknowledge_current_reboot


def main():
    report = acknowledge_current_reboot()
    if report is None:
        print("Aucune alerte de reboot recente a acquitter.")
        return

    print(f"Alerte reboot acquittee : {report}")


if __name__ == "__main__":
    main()
