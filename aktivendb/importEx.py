from re import X
import openpyxl
from .models import Member, Team, TeamMember, MemberRole


def none2Empty(a):
    if a is None:
        return ""
    return a


class ImpEx:
    phase = 3

    def impEx(self, req):
        path = req.GET["file"]
        wb = openpyxl.load_workbook(filename=path)
        sheetnames = wb.get_sheet_names()
        ws = wb.active
        headerMap = {}
        entries = []
        amembers = Member.objects.all()
        self.ateams = Team.objects.all()
        self.mitgliedRole = MemberRole.objects.get(title="Mitglied")
        emembers = set()
        for (i, row) in enumerate(ws.rows):
            if i == 0:
                row0 = row
                for (j, v) in enumerate(row0):
                    headerMap[v.value] = j
                print("hdr", headerMap)
                continue
            emember = {x: row[headerMap[x]].value for x in headerMap.keys()}
            emember["Vorname"] = "" if emember.get(
                "Vorname") is None else emember["Vorname"].strip()
            # print("emember", emember)
            emembers.add(emember.get("Nachname") +
                         ", " + emember.get("Vorname"))
            amembers2 = [m for m in amembers if m.first_name == emember.get(
                "Vorname") and m.last_name == emember.get("Nachname")]
            if len(amembers2) != 1:
                print("no member", emember.get(
                    "Vorname"), emember.get("Nachname"))
                if self.phase == 1:
                    continue
                print("emember", emember)
                amember = self.createMember(emember)
                continue
            amember = amembers2[0]
            amember = self.updateMember(amember, emember)
            # print("amember", amember)
        if self.phase != 3:
            return
        for member in amembers:
            if (member.last_name + ", " + member.first_name) not in emembers:
                member.delete()

    def createMember(self, emember):
        eags = emember.get("AGs")
        aags = []
        for ag in self.ateams:
            if eags.find(ag.name) >= 0:
                aags.append(ag)
        member = Member(
            name=emember.get("Nachname") + ", " + emember.get("Vorname"),
            email_adfc=emember.get("Email-ADFC"),
            email_private=emember.get("Email-Privat"),
            phone_primary=emember.get("Telefon"),
            phone_secondary=emember.get("Telefon-Alternative"),
            address=emember.get("Postleitzahl"),
            adfc_id=emember.get("ADFC-Mitgliedsnummer"),
            admin_comments=None,
            reference="",
            latest_first_aid_training=emember.get(
                "Letztes Erste-Hilfe-Training"),
            gender=emember.get("Geschlecht"),
            interests=emember.get("Interessen"),
            latest_contact=None,
            active=emember.get("Aktiv"),
            birthday=none2Empty(emember.get("Geburtsjahr")),
            status="",
            registered_for_first_aid_training=emember.get(
                "Registriert für Erste-Hilfe-Training"),
            first_name=emember.get("Vorname"),
            last_name=emember.get("Nachname"),
        )
        member.save()

        for ag in aags:
            tm = TeamMember(
                team=ag, member=member,
                member_role=self.mitgliedRole, admin_comments="")
        tm.save()
        return member

    def updateMember(self, member, emember):
        name = emember.get("Nachname") + ", " + emember.get("Vorname")
        if name != member.name:
            member.name = name

        email_adfc = emember.get("Email-ADFC")
        if email_adfc != member.email_adfc:
            member.email_adfc = email_adfc

        email_private = emember.get("Email-Privat")
        if email_private != member.email_private:
            member.email_private = email_private

        phone_primary = emember.get("Telefon")
        if phone_primary != member.phone_primary:
            member.phone_primary = phone_primary

        phone_secondary = emember.get("Telefon-Alternative")
        if phone_secondary != member.phone_secondary:
            member.phone_secondary = phone_secondary

        address = emember.get("Postleitzahl")
        if address != member.address:
            member.address = address

        adfc_id = str(emember.get("ADFC-Mitgliedsnummer"))
        if adfc_id != member.adfc_id:
            member.adfc_id = adfc_id

        latest_first_aid_training = emember.get(
            "Letztes Erste-Hilfe-Training")
        if latest_first_aid_training is not None:
            latest_first_aid_training = latest_first_aid_training.date()  # datetime -> date
        if latest_first_aid_training != member.latest_first_aid_training:
            member.latest_first_aid_training = latest_first_aid_training

        gender = emember.get("Geschlecht")
        if gender != member.gender:
            member.gender = gender

        interests = emember.get("Interessen")
        if interests != member.interests:
            member.interests = interests

        active = emember.get("Aktiv")
        if active != member.active:
            member.active = active

        birthday = none2Empty(emember.get("Geburtsjahr"))
        if birthday != member.birthday:
            member.birthday = birthday

        registered_for_first_aid_training = emember.get(
            "Registriert für Erste-Hilfe-Training")
        if registered_for_first_aid_training != member.registered_for_first_aid_training:
            member.registered_for_first_aid_training = registered_for_first_aid_training

        first_name = emember.get("Vorname")
        if first_name != member.first_name:
            member.first_name = first_name

        last_name = emember.get("Nachname")
        if last_name != member.last_name:
            member.last_name = last_name

        member.save()

        eags = none2Empty(emember.get("AGs"))
        newTeams = []
        for ag in self.ateams:
            if eags.find(ag.name) >= 0:
                newTeams.append(ag)
        oldTeams = member.teams.all()
        oldTeamNames = [team.name for team in oldTeams]
        newTeamNames = [team.name for team in newTeams]
        for ag in newTeams:
            if ag.name not in oldTeamNames:
                tm = TeamMember(
                    team=ag, member=member,
                    member_role=self.mitgliedRole, admin_comments="")
                tm.save()
        for ag in oldTeams:
            if ag.name not in newTeamNames:
                tm = TeamMember.objects.get(team=ag, member=member)
                tm.delete()
        return member
