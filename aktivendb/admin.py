from django.contrib import admin

# Register your models here.
from .models import Member, MemberRole, Team, TeamMember, User


class MembershipInline(admin.TabularInline):
    model = TeamMember
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name"]
    search_fields = ["first_name", "last_name"]
    exclude = ("name",)
    inlines = [MembershipInline]


class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    inlines = [MembershipInline]
    exclude = ("members",)


admin.site.register(Member, MemberAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(MemberRole)
admin.site.register(User)
