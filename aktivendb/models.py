from django.db import models
from django.urls import reverse

# Importieren von aktivendb:
# In AktivenDB Aktive als Excel runterladen, z.B. alle.xlsx
# in urls.py Eintrag für "import" aktivieren
# mit phase = 1, 2, 3 jeweils die URL http://.../import?file=.../alle.xlsx aufrufen
# phase 1: Meldungen wenn Name aus Excel-Datei nicht in der DB steht. Prüfen, ob Name geändert
# phase 2: Update oder Neuanlage von Membern (NICHT von teams, das ist Handarbeit!)
# phase 3: Löschen von Membern, die nicht im Excel vorkommen

# managed: FALSE => Django faßt die Tabellen nicht an


class Ability(models.Model):
    title = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    # Field renamed because it was a Python reserved word.
    global_field = models.IntegerField(db_column='global')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abilities'


class MemberRole(models.Model):
    title = models.CharField(max_length=255)
    abilities = models.ManyToManyField(Ability, through="AbilityMemberRole")
    description = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'member_roles'


class AbilityMemberRole(models.Model):
    # ability_id = models.IntegerField()
    ability = models.ForeignKey(
        Ability, db_column="ability_id", default=None, related_name="+", on_delete=models.CASCADE)
    # member_role_id = models.IntegerField()
    member_role = models.ForeignKey(
        MemberRole, db_column="member_role_id", default=None, related_name="+", on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ability_member_role'


class Member(models.Model):
    name = models.CharField(max_length=255, default="", blank=True, null=True)
    email_adfc = models.EmailField(max_length=255, blank=True, null=True)
    email_private = models.EmailField(max_length=255, blank=True, null=True)
    phone_primary = models.CharField(max_length=255, blank=True, null=True)
    phone_secondary = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    adfc_id = models.CharField(max_length=255, blank=True, null=True)
    admin_comments = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=False)
    latest_first_aid_training = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    latest_contact = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    birthday = models.CharField(max_length=255, blank=True, null=False)
    status = models.CharField(max_length=4000, blank=True, null=False)
    registered_for_first_aid_training = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.fullname()

    def get_absolute_url(self):
        return reverse("member-detail", args=[self.id])

    class Meta:
        managed = False
        db_table = 'members'


class Team(models.Model):
    members = models.ManyToManyField(
        Member, through="TeamMember", related_name="teams")
    name = models.CharField(max_length=255, default="", blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=False)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=False)
    needs_first_aid_training = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("team-detail", args=[self.id])

    class Meta:
        managed = False
        db_table = 'project_teams'


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team, db_column="project_team_id", default=None, on_delete=models.CASCADE)
    # member_id = models.PositiveIntegerField()
    member = models.ForeignKey(
        Member, db_column="member_id", default=None, on_delete=models.CASCADE)
    # member_role_id = models.PositiveIntegerField()
    member_role = models.ForeignKey(
        MemberRole, db_column="member_role_id", default=None, on_delete=models.CASCADE)
    admin_comments = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_team_member'


class User(models.Model):
    # member_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, default=None)
    abilities = models.ManyToManyField(Ability, through="AbilityUser")
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    remember_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.member.fullname()

    class Meta:
        managed = False
        db_table = 'users'


class AbilityUser(models.Model):
    # ability_id = models.IntegerField()
    ability = models.ForeignKey(
        Ability, db_column="ability_id", default=None, related_name="+", on_delete=models.CASCADE)
    # user_id = models.IntegerField()
    user = models.ForeignKey(User, db_column="user_id", default=None, related_name="+",
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ability_user'
