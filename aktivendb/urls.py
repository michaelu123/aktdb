from django.urls import path
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="starting"),
    path("aktive", views.AllMembersView.as_view(), name="members-all"),
    path("aktive/<int:pk>", views.MemberDetailView.as_view(),
         name="member-detail"),
    path("teams", views.AllTeamsView.as_view(), name="teams-all"),
    path("teams/<int:pk>", views.TeamDetailView.as_view(),
         name="team-detail"),
    path("addteam", views.AddTeamView.as_view(), name="add-team"),
    path("addmember", views.AddMemberView.as_view(), name="add-team"),
    path("accounts/", include('django.contrib.auth.urls')),
    path("excel", views.Excel.as_view(), name="excel-members"),
    path("excel/<int:pk>", views.Excel.as_view(), name="excel-team"),
]
