from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from .models import Member, Team, TeamMember, MemberRole
from .forms import MemberDetailForm, TeamDetailForm
from .utils import is_admin, getMySelfId
from .excel import excelMembers, excelTeam


def index(req):
    return render(req, "aktivendb/index.html")


class AllMembersView(LoginRequiredMixin, ListView):
    template_name = "aktivendb/members.html"
    model = Member
    ordering = ["last_name", "first_name"]
    context_object_name = "members"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_admin"] = is_admin(self.request)
        ctx["search"] = self.request.session.get("search", "")
        return ctx

    def get_queryset(self):
        allMembers = Member.objects.all().order_by("last_name", "first_name")

        if is_admin(self.request):
            for member in allMembers:
                member.linked = True
        else:
            myselfId = getMySelfId(self.request)
            allTeams = Team.objects.all().order_by("name")
            vorsitz = MemberRole.objects.get(title="Vorsitz")
            allTMs = TeamMember.objects.all()
            myTeams = set()
            for team in allTeams:
                team.linked = False
                teammembers = [tm for tm in allTMs if tm.team_id == team.id]
                for tm in teammembers:
                    if tm.member_id != myselfId:
                        continue
                    if tm.member_role_id == vorsitz.id:
                        myTeams.add(tm.team_id)
                        break
            filteredTMs = [tm for tm in allTMs if tm.team_id in myTeams]
            for member in allMembers:
                member.linked = False
                for tm in filteredTMs:
                    if tm.member_id == member.id:
                        member.linked = True
                        break
        return allMembers

    def get(self, *args, **kwargs):
        self.memberIdToDelete = self.request.GET.get("delete")
        if self.memberIdToDelete != None and is_admin(self.request):
            member = Member.objects.get(id=int(self.memberIdToDelete))
            member.delete()
            self.memberIdToDelete = None
            return HttpResponseRedirect(redirect_to=reverse("members-all"))
        resp = super().get(*args, **kwargs)
        return resp


class MemberDetailView(LoginRequiredMixin, UpdateView):
    template_name = "aktivendb/member_detail.html"
    model = Member
    form_class = MemberDetailForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        member = self.object
        member.name = member.fullname()
        teams = {t.name: t.id for t in member.teams.all().order_by("name")}
        ctx["allteams"] = [t for t in Team.objects.all().order_by("name")
                           if teams.get(t.name) == None]
        teammembers = list(member.teammember_set.all().order_by("team__name"))
        ctx["teammembers"] = teammembers

        if is_admin(self.request):
            for teammember in teammembers:
                teammember.linked = True
        else:
            myselfId = getMySelfId(self.request)
            for teammember in teammembers:
                try:
                    tm = teammember.team.teammember_set.get(member_id=myselfId)
                    if tm.member_role.title == "Vorsitz":
                        teammember.linked = True
                except:
                    teammember.linked = False

        roles = list(MemberRole.objects.all())
        # so that "Mitglied" is first entry, then "Vorsitz", then "Formales Mitglied"
        ctx["roles"] = [roles[1], roles[0], *roles[2:]]
        self.teammemberIdToUpdate = self.request.GET.get("updtm")
        if self.teammemberIdToUpdate != None:
            ctx["teammember"] = TeamMember.objects.get(
                id=int(self.teammemberIdToUpdate))
        else:
            ctx["teammember"] = None
        ctx["is_admin"] = is_admin(self.request)
        return ctx

    def get(self, *args, **kwargs):
        if not is_admin(self.request):
            try:
                # is this member a member of a team where the logged in user has role="Vorsitz"
                myselfId = getMySelfId(self.request)
                allTeams = Team.objects.all()
                vorsitz = MemberRole.objects.get(title="Vorsitz")
                allTMs = TeamMember.objects.all()
                myTeams = set()
                memberId = kwargs["pk"]
                for team in allTeams:
                    teammembers = [
                        tm for tm in allTMs if tm.team_id == team.id]
                    for tm in teammembers:
                        if tm.member_id != myselfId:
                            continue
                        if tm.member_role_id == vorsitz.id:
                            myTeams.add(tm.team_id)
                            break
                memberTMs = [
                    tm for tm in allTMs if tm.team_id in myTeams and tm.member_id == memberId]
                if len(memberTMs) == 0:  # not a member in one of my teams
                    return HttpResponseRedirect(redirect_to=reverse("members-all"))
            except Exception as e:
                print(e)
                return HttpResponseRedirect(redirect_to=reverse("members-all"))

        self.request.session["search"] = self.request.GET.get("search", "")
        self.teammemberIdToDelete = self.request.GET.get("deltm")
        if self.teammemberIdToDelete != None:
            teammember = TeamMember.objects.get(
                id=int(self.teammemberIdToDelete))
            teammember.delete()
            return HttpResponseRedirect(redirect_to=reverse("member-detail", args=[kwargs["pk"]]))
        resp = super().get(*args, **kwargs)
        return resp

    def post(self, req, pk):
        p = req.POST
        if p["action"] == "update_member":
            return super().post(req, pk)
        if p["action"] == "make_user" and is_admin(self.request):
            user_pwd = p.get("user_pwd")
            member = Member.objects.get(pk=pk)
            email = member.email_adfc if member.email_adfc else member.email_private
            if email and user_pwd:
                try:
                    user = User(username=email, first_name=member.first_name,
                                last_name=member.last_name, email=email, password=make_password(user_pwd))
                    user.save()
                    group = Group.objects.get(name="leiter")
                    user.groups.set([group])
                except:
                    pass  # TODO: error message?
            else:
                pass  # TODO: error message?
        else:
            memberRoleId = p.get("role")
            memberRole = MemberRole.objects.get(pk=memberRoleId)
            comment = p.get("comment")
        if p["action"] == "add_team":
            teamId = p.get("team")
            team = Team.objects.get(pk=teamId)
            member = Member.objects.get(pk=pk)
            tm = TeamMember(team=team, member=member,
                            member_role=memberRole, admin_comments=comment)
            tm.save()
        if p["action"] == "update_teammember":
            teamMemberId = p.get("teammember_id")
            teamMember = TeamMember.objects.get(id=teamMemberId)
            teamMember.member_role = memberRole
            teamMember.admin_comments = comment
            teamMember.save()
        return HttpResponseRedirect(reverse("member-detail", args=[pk]))


class AllTeamsView(LoginRequiredMixin, ListView):
    template_name = "aktivendb/teams.html"
    model = Team
    ordering = ["name"]
    context_object_name = "teams"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_admin"] = is_admin(self.request)
        return ctx

    def get_queryset(self):
        allTeams = Team.objects.all().order_by("name")
        if is_admin(self.request):
            for team in allTeams:
                team.linked = True
        else:
            myselfId = getMySelfId(self.request)
            allTMs = list(TeamMember.objects.all())
            vorsitz = MemberRole.objects.get(title="Vorsitz")
            for team in allTeams:
                team.linked = False
                teammembers = [tm for tm in allTMs if tm.team_id == team.id]
                for tm in teammembers:
                    if tm.member_id != myselfId:
                        continue
                    if tm.member_role_id == vorsitz.id:
                        team.linked = True
                        break
        return allTeams

    def get(self, *args, **kwargs):
        self.teamIdToDelete = self.request.GET.get("delete")
        if self.teamIdToDelete != None and is_admin(self.request):
            team = Team.objects.get(id=int(self.teamIdToDelete))
            team.delete()
            self.teamIdToDelete = None
            return HttpResponseRedirect(redirect_to=reverse("teams-all"))
        resp = super().get(*args, **kwargs)
        return resp


class TeamDetailView(LoginRequiredMixin, UpdateView):
    template_name = "aktivendb/team_detail.html"
    model = Team
    form_class = TeamDetailForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["members"] = list(self.object.members.all().order_by("name"))
        myMembers = {m.fullname(): m.id for m in ctx["members"]}
        ctx["allmembers"] = [m for m in Member.objects.all().order_by("last_name", "first_name")
                             if myMembers.get(m.fullname()) == None]
        ctx["teammembers"] = list(
            self.object.teammember_set.all().order_by("member__last_name", "member__last_name"))
        roles = list(MemberRole.objects.all())
        # so that "Mitglied" is first entry, then "Vorsitz", then "Formales Mitglied"
        ctx["roles"] = [roles[1], roles[0], *roles[2:]]
        self.teammemberIdToUpdate = self.request.GET.get("updtm")
        if self.teammemberIdToUpdate != None:
            ctx["teammember"] = TeamMember.objects.get(
                id=int(self.teammemberIdToUpdate))
        else:
            ctx["teammember"] = None
        ctx["is_admin"] = is_admin(self.request)
        return ctx

    def get(self, *args, **kwargs):
        if not is_admin(self.request):
            try:
                # has logged in user role="Vorsitz" in this team?
                teamId = kwargs["pk"]
                team = Team.objects.get(pk=teamId)
                myselfId = getMySelfId(self.request)
                teamMember = team.teammember_set.get(member_id=myselfId)
                role = teamMember.member_role
                if role.title != "Vorsitz":
                    return HttpResponseRedirect(redirect_to=reverse("teams-all"))
            except Exception as e:
                print(e)
                return HttpResponseRedirect(redirect_to=reverse("teams-all"))

        self.teammemberIdToDelete = self.request.GET.get("deltm")
        if self.teammemberIdToDelete != None:
            teammember = TeamMember.objects.get(
                id=int(self.teammemberIdToDelete))
            teammember.delete()
            return HttpResponseRedirect(redirect_to=reverse("team-detail", args=[kwargs["pk"]]))
        resp = super().get(*args, **kwargs)
        return resp

    def post(self, req, pk):
        p = req.POST
        if p["action"] == "update_team":
            return super().post(req, pk)
        memberRoleId = p.get("role")
        memberRole = MemberRole.objects.get(pk=memberRoleId)
        comment = p.get("comment")
        if p["action"] == "add_member":
            memberId = p.get("member")
            member = Member.objects.get(pk=memberId)
            team = Team.objects.get(pk=pk)
            tm = TeamMember(team=team, member=member,
                            member_role=memberRole, admin_comments=comment)
            tm.save()
        if p["action"] == "update_teammember":
            teamMemberId = p.get("teammember_id")
            teamMember = TeamMember.objects.get(id=teamMemberId)
            teamMember.member_role = memberRole
            teamMember.admin_comments = comment
            teamMember.save()
        return HttpResponseRedirect(reverse("team-detail", args=[pk]))


class AddTeamView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamDetailForm

    def get(self, *args, **kwargs):
        if is_admin(self.request):
            return super().get(*args, **kwargs)
        return HttpResponseRedirect(redirect_to=reverse("teams-all"))


class AddMemberView(LoginRequiredMixin, CreateView):
    model = Member
    form_class = MemberDetailForm

    def get(self, *args, **kwargs):
        if is_admin(self.request):
            return super().get(*args, **kwargs)
        return HttpResponseRedirect(redirect_to=reverse("members-all"))


class Excel(View):
    def post(self, *args, **kwargs):
        pk = kwargs.get("pk")
        file = self.request.POST.get("file")
        prefEmail = self.request.POST.get("pref-email")
        if pk:
            return excelTeam(self.request, pk, file, prefEmail)
        return excelMembers(self.request, file, prefEmail)
