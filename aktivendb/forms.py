from django import forms

from .models import Member, Team


class MemberDetailForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["first_name", "last_name", "gender", "birthday", "email_adfc", "email_private",
                  "phone_primary", "phone_secondary",
                  "address", "adfc_id", "reference", "interests", "latest_contact", "admin_comments",
                  "active", "status", "latest_first_aid_training", "registered_for_first_aid_training", ]
        labels = {
            "first_name": "Vorname",
            "last_name": "Nachname",
            "gender": "Geschlecht",
            "birthday": "Geburtsjahr",
            "email_adfc": "Email (ADFC)",
            "email_private": "Email (Privat)",
            "phone_primary": "Telefon",
            "phone_secondary": "Telefon (alternativ)",
            "address": "Postleitzahl",
            "adfc_id": "Mitgliedsnummer",
            "reference": "Referenz",
            "interests": "Interessen",
            "latest_contact": "Letzter Kontakt",
            "admin_comments": "Kommentar",
            "active": "Aktiv",
            "status": "Status",
            "latest_first_aid_training": "Letzte 1. Hilfe Schulung",
            "registered_for_first_aid_training": "Registriert für Erste-Hilfe-Kurs",
        }


class TeamDetailForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "email", "description", "comments",
                  "reference", "needs_first_aid_training"]
        labels = {
            "name": "Name",
            "email": "E-mail",
            "description": "Beschreibung",
            "comments": "Kommentar",
            "reference": "Referenz",
            "needs_first_aid_training": "1. Hilfe Schulung notwendig",
        }
