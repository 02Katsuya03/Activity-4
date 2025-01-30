from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    FormView,
    UpdateView,
    DeleteView,
    View,
)
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import (
    RegistrationUserForm,
    LoginUserForm,
    LoginAdminForm,
    LostItemForm,
    FoundItemForm,
    F2FClaimProcedureForm,
    OnlineClaimProcedureForm,
    SchoolForm,
)
from Appli.models import (
    Profile,
    LostItem,
    School,
    FoundItem,
    F2FClaim,
    OnlineClaim,
    ClaimProcedure,
    OnlineClaimProcedure,
)
from django.contrib.auth.models import User
from datetime import date
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin


def logout_view(request):
    logout(request)
    return redirect("intro")


class RegisterUserView(FormView):
    template_name = "app/register_user.html"
    form_class = RegistrationUserForm
    success_url = reverse_lazy("intro")

    def form_valid(self, form):

        user = form.save()

        Profile.objects.create(
            user=user,
            middle_name=form.cleaned_data["middle_name"],
            sex=form.cleaned_data["sex"],
            phone_number=form.cleaned_data["phone_number"],
            school=form.cleaned_data["school"],
            role="USER",
        )

        login(self.request, user)

        messages.success(
            self.request, "Registration successful! You are now logged in."
        )

        return redirect("intro")


class RegisterAdminView(FormView):
    template_name = "app/register_admin.html"
    form_class = RegistrationUserForm
    success_url = reverse_lazy("intro")

    def form_valid(self, form):

        user = form.save()

        Profile.objects.create(
            user=user,
            middle_name=form.cleaned_data["middle_name"],
            sex=form.cleaned_data["sex"],
            phone_number=form.cleaned_data["phone_number"],
            school=form.cleaned_data["school"],
            role="ADMIN",
        )

        login(self.request, user)

        messages.success(
            self.request, "Registration successful! You are now logged in as an admin."
        )

        return redirect("intro")


class LoginUserView(FormView):
    template_name = "app/login_user.html"
    form_class = LoginUserForm
    success_url = reverse_lazy("user_home")

    def form_valid(self, form):
        user = form.get_user()
        role = form.cleaned_data["role"]
        school = form.cleaned_data["school"]

        try:
            profile = Profile.objects.get(user=user)
            if profile.role.lower() != role.lower():
                messages.error(
                    self.request,
                    f"Incorrect role. Expected {profile.role}, but got {role}.",
                )
                return redirect("login_user")
            if profile.school != school:
                messages.error(self.request, "User does not belong to this school.")
                return redirect("login_user")
            login(self.request, user)
            messages.success(
                self.request, "Login successful! Welcome to your dashboard."
            )

            return super().form_valid(form)

        except Profile.DoesNotExist:
            messages.error(self.request, "No profile associated with this user.")
            return redirect("login_user")


class LoginAdminView(FormView):
    template_name = "app/login_admin.html"
    form_class = LoginAdminForm
    success_url = reverse_lazy("administrator")

    def form_valid(self, form):
        user = form.get_user()
        school_id = form.cleaned_data["school"]

        try:
            profile = Profile.objects.get(user=user)

            if profile.role.lower() != "admin":
                messages.error(
                    self.request, "You cannot access this; it is for admin only."
                )
                return redirect("login_user")

            if profile.school.id != int(school_id):
                messages.error(self.request, "Admin does not belong to this school.")
                return redirect("login_user")
            user.first_name = profile.user.first_name
            user.last_name = profile.user.last_name
            user.save()
            self.request.session["user_first_name"] = user.first_name
            self.request.session["user_last_name"] = user.last_name
            self.request.session["user_role"] = profile.role

            login(self.request, user)
            return super().form_valid(form)

        except Profile.DoesNotExist:
            messages.error(self.request, "No profile associated with this user.")
            return redirect("login_user")


class IntroPageView(TemplateView):
    template_name = "app/intro.html"


class LoginBasePageView(TemplateView):
    template_name = "app/login_base.html"


class AdminPageView(TemplateView):
    template_name = "app/administrator.html"


class LostPageView(LoginRequiredMixin, TemplateView):
    template_name = "app/lost.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["first_name"] = user.first_name if user.first_name else "Unknown"
        context["last_name"] = user.last_name if user.last_name else "User"
        return context


class UserPageView(TemplateView):
    template_name = "app/user.html"


class LostView(TemplateView):
    template_name = "app/lost.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        first_name = self.request.session.get("user_first_name")
        last_name = self.request.session.get("user_last_name")
        role = self.request.session.get("user_role")
        school_name = self.request.session.get("user_school")
        context["first_name"] = first_name
        context["last_name"] = last_name
        context["role"] = role
        context["school_name"] = school_name

        return context


@method_decorator(login_required, name="dispatch")
class LostDashboardView(ListView):
    template_name = "app/lost_dashboard.html"
    model = LostItem
    context_object_name = "recent_claims"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = (
            User.objects.exclude(is_superuser=True)
            .exclude(profile__role="ADMIN")
            .count()
        )
        context["total_lost_items"] = LostItem.objects.count()
        total_claimed_items = F2FClaim.objects.count() + OnlineClaim.objects.count()
        total_found_items = FoundItem.objects.count()
        context["total_found_items"] = total_found_items - total_claimed_items

        context["total_claims"] = total_claimed_items
        recent_days = 7
        recent_date = now() - timedelta(days=recent_days)
        context["recent_claims"] = LostItem.objects.filter(
            date_added__gte=recent_date
        ).order_by("-date_added")

        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class LostSchool(TemplateView):
    template_name = "app/lost_school.html"


@method_decorator(login_required, name="dispatch")
class LostListView(ListView):
    template_name = "app/lost_listview.html"
    model = LostItem
    context_object_name = "items"
    paginate_by = 15
    queryset = LostItem.objects.all()

    def get_queryset(self):
        queryset = LostItem.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LostItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class LostViewItem(ListView):
    template_name = "app/lost_viewitem.html"
    model = LostItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = LostItem.objects.all()

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LostItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.only("id", "name")
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class LostDetailView(DetailView):
    model = LostItem
    template_name = "app/lost_detailview.html"
    context_object_name = "item"

    def get_object(self, queryset=None):

        item_id = self.kwargs.get("item_id")
        return LostItem.objects.get(item_id=item_id)


@method_decorator(login_required, name="dispatch")
class LostAddItemView(CreateView):
    model = LostItem
    form_class = LostItemForm
    template_name = "app/lost_additem.html"
    success_url = reverse_lazy("lost_listview")

    def form_valid(self, form):

        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        response = super().form_valid(form)
        return response

    def form_valid(self, form):
        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        response = super().form_valid(form)

        return response


@method_decorator(login_required, name="dispatch")
class LostUpdateItemView(UpdateView):
    model = LostItem
    fields = [
        "item_name",
        "description",
        "category",
        "location_lost",
        "lost_by",
        "contact_information",
        "photo",
        "school",
    ]
    template_name = "app/lost_updateitem.html"
    success_url = reverse_lazy("lost_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(LostItem, item_id=self.kwargs["item_id"])


@method_decorator(login_required, name="dispatch")
class LostDeleteItemView(DeleteView):
    model = LostItem
    success_url = reverse_lazy("lost_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(LostItem, item_id=self.kwargs["item_id"])

    def delete(self, request, *args, **kwargs):
        item = self.get_object()

        profile = self.request.user.profile
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class FoundView(TemplateView):
    template_name = "app/found.html"


class LostUsersListView(ListView):
    model = Profile
    template_name = "app/lost_userlist.html"
    context_object_name = "profiles"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        sex_filter = self.request.GET.get("sex", "")
        school_filter = self.request.GET.get("school", "")
        order_by = self.request.GET.get("order_by", "asc")
        profiles = Profile.objects.exclude(role="ADMIN").select_related(
            "user", "school"
        )

        if query:
            profiles = profiles.filter(
                user__first_name__icontains=query
            ) | profiles.filter(user__last_name__icontains=query)

        if sex_filter:
            profiles = profiles.filter(sex=sex_filter)

        if school_filter:
            profiles = profiles.filter(school_id=school_filter)

        if order_by == "asc":
            profiles = profiles.order_by("user__first_name")
        else:
            profiles = profiles.order_by("-user__first_name")

        return profiles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Appli.models import School

        context["schools"] = School.objects.only("id", "name")
        return context


@method_decorator(login_required, name="dispatch")
class FoundDashboardView(ListView):
    template_name = "app/found_dashboard.html"
    model = FoundItem
    context_object_name = "recent_claims"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = (
            User.objects.exclude(is_superuser=True)
            .exclude(profile__role="ADMIN")
            .count()
        )
        context["total_lost_items"] = LostItem.objects.count()
        total_claimed_items = F2FClaim.objects.count() + OnlineClaim.objects.count()
        total_found_items = FoundItem.objects.count()
        context["total_found_items"] = total_found_items - total_claimed_items

        context["total_claims"] = total_claimed_items
        recent_days = 7
        recent_date = now() - timedelta(days=recent_days)
        context["recent_claims"] = FoundItem.objects.filter(
            date_added__gte=recent_date
        ).order_by("-date_added")

        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class FoundListView(ListView):
    template_name = "app/found_listview.html"
    model = FoundItem
    context_object_name = "items"
    paginate_by = 15

    def get_queryset(self):
        queryset = FoundItem.objects.filter(is_claimed=False)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = FoundItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.only("id", "name")
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class FoundViewItem(ListView):
    template_name = "app/found_viewitem.html"
    model = FoundItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):

        queryset = FoundItem.objects.filter(is_claimed=False)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = FoundItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.only("id", "name")
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


@method_decorator(login_required, name="dispatch")
class FoundDetailView(DetailView):
    model = FoundItem
    template_name = "app/found_detailview.html"
    context_object_name = "item"

    def get_object(self, queryset=None):

        item_id = self.kwargs.get("item_id")
        return FoundItem.objects.get(item_id=item_id)


@method_decorator(login_required, name="dispatch")
class FoundAddItemView(CreateView):
    model = FoundItem
    form_class = FoundItemForm
    template_name = "app/found_additem.html"
    success_url = reverse_lazy("found_listview")

    def form_valid(self, form):

        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        response = super().form_valid(form)
        return response

    def form_valid(self, form):
        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        response = super().form_valid(form)

        return response


@method_decorator(login_required, name="dispatch")
class FoundUpdateItemView(UpdateView):
    model = FoundItem
    fields = [
        "item_name",
        "description",
        "category",
        "location_found",
        "found_by",
        "contact_information",
        "photo",
        "school",
    ]
    template_name = "app/found_updateitem.html"
    success_url = reverse_lazy("found_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(FoundItem, item_id=self.kwargs["item_id"])


@method_decorator(login_required, name="dispatch")
class FoundDeleteItemView(DeleteView):
    model = FoundItem
    success_url = reverse_lazy("found_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(FoundItem, item_id=self.kwargs["item_id"])

    def delete(self, request, *args, **kwargs):
        item = self.get_object()

        profile = self.request.user.profile
        return super().delete(request, *args, **kwargs)


class FoundUsersListView(ListView):
    model = Profile
    template_name = "app/found_userlist.html"
    context_object_name = "profiles"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        sex_filter = self.request.GET.get("sex", "")
        school_filter = self.request.GET.get("school", "")
        order_by = self.request.GET.get("order_by", "asc")
        profiles = Profile.objects.exclude(role="ADMIN").select_related(
            "user", "school"
        )

        if query:
            profiles = profiles.filter(
                user__first_name__icontains=query
            ) | profiles.filter(user__last_name__icontains=query)

        if sex_filter:
            profiles = profiles.filter(sex=sex_filter)

        if school_filter:
            profiles = profiles.filter(school_id=school_filter)

        if order_by == "asc":
            profiles = profiles.order_by("user__first_name")
        else:
            profiles = profiles.order_by("-user__first_name")

        return profiles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Appli.models import School

        context["schools"] = School.objects.only("id", "name")
        return context


class ClaimDashboardView(ListView):
    template_name = "app/claim_dashboard.html"
    model = F2FClaim
    context_object_name = "recent_claims"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = (
            User.objects.exclude(is_superuser=True)
            .exclude(profile__role="ADMIN")
            .count()
        )
        context["total_lost_items"] = LostItem.objects.count()
        total_claimed_items = F2FClaim.objects.count() + OnlineClaim.objects.count()
        total_found_items = FoundItem.objects.count()
        context["total_found_items"] = total_found_items - total_claimed_items

        context["total_claims"] = total_claimed_items
        recent_days = 7
        recent_date = now() - timedelta(days=recent_days)
        context["recent_claims"] = F2FClaim.objects.filter(
            claimed_at__gte=recent_date
        ).order_by("-claimed_at")

        return context


class ClaimViewItem(ListView):
    template_name = "app/claim_viewitem.html"
    model = FoundItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = FoundItem.objects.filter(is_claimed=False)

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = FoundItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


class ClaimItemListView(ListView):
    template_name = "app/claim_claimitem.html"
    context_object_name = "claims"
    paginate_by = 10

    def get_queryset(self):
        f2f_claims = F2FClaim.objects.all()
        online_claims = OnlineClaim.objects.all()
        query = self.request.GET.get("q", "")
        if query:
            f2f_claims = f2f_claims.filter(
                Q(found_item__item_name__icontains=query)
                | Q(claimed_by__icontains=query)
            )
            online_claims = online_claims.filter(
                Q(found_item__item_name__icontains=query)
                | Q(claimed_by__icontains=query)
            )
        school_id = self.request.GET.get("school", "")
        if school_id:
            f2f_claims = f2f_claims.filter(found_item__school_id=school_id)
            online_claims = online_claims.filter(found_item__school_id=school_id)
        order_by = self.request.GET.get("order_by", "asc")
        if order_by == "desc":
            f2f_claims = f2f_claims.order_by("-claimed_at")
            online_claims = online_claims.order_by("-claimed_at")
        else:
            f2f_claims = f2f_claims.order_by("claimed_at")
            online_claims = online_claims.order_by("claimed_at")
        combined_claims = list(f2f_claims) + list(online_claims)
        return combined_claims

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Appli.models import School

        context["schools"] = School.objects.all()

        return context


@method_decorator(login_required, name="dispatch")
class ClaimDetailView(DetailView):
    model = FoundItem
    template_name = "app/claim_detailview.html"
    context_object_name = "item"

    def get_object(self, queryset=None):
        item_id = self.kwargs.get("item_id")
        return get_object_or_404(FoundItem, item_id=item_id)


class F2FListView(ListView):
    model = F2FClaim
    template_name = "app/claim_f2fclaim.html"
    context_object_name = "f2f_claims"
    paginate_by = 10

    def get_queryset(self):
        return F2FClaim.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_claims"] = F2FClaim.objects.filter(
            claim_type="Face-to-Face"
        ).count()
        return context


class ClaimUsersListView(ListView):
    model = Profile
    template_name = "app/claim_userlist.html"
    context_object_name = "profiles"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        sex_filter = self.request.GET.get("sex", "")
        school_filter = self.request.GET.get("school", "")
        order_by = self.request.GET.get("order_by", "asc")
        profiles = Profile.objects.exclude(role="ADMIN").select_related(
            "user", "school"
        )

        if query:
            profiles = profiles.filter(
                user__first_name__icontains=query
            ) | profiles.filter(user__last_name__icontains=query)

        if sex_filter:
            profiles = profiles.filter(sex=sex_filter)

        if school_filter:
            profiles = profiles.filter(school_id=school_filter)

        if order_by == "asc":
            profiles = profiles.order_by("user__first_name")
        else:
            profiles = profiles.order_by("-user__first_name")

        return profiles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Appli.models import School

        context["schools"] = School.objects.all()
        return context


class UserHomeView(TemplateView):
    template_name = "app/user_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_days = 7
        recent_date = now() - timedelta(days=recent_days)
        context["recent_lost_items"] = LostItem.objects.filter(
            date_added__gte=recent_date
        ).order_by("-date_added")
        context["recent_found_items"] = FoundItem.objects.filter(
            date_added__gte=recent_date
        ).order_by("-date_added")

        return context


class UserLostAddItemView(LoginRequiredMixin, CreateView):
    model = LostItem
    form_class = LostItemForm
    template_name = "app/user_lostadditem.html"
    success_url = reverse_lazy("user_lostlistview")

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        return super().form_valid(form)


class UserLostListView(LoginRequiredMixin, ListView):
    template_name = "app/user_lostlistview.html"
    model = LostItem
    context_object_name = "items"
    paginate_by = 15

    def get_queryset(self):

        queryset = LostItem.objects.filter(user=self.request.user)

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LostItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School
        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


class UserLostUpdateItemView(UpdateView):
    model = LostItem
    fields = [
        "item_name",
        "description",
        "category",
        "location_lost",
        "lost_by",
        "contact_information",
        "photo",
        "school",
    ]
    template_name = "app/user_lostupdateitem.html"
    success_url = reverse_lazy("user_lostlistview")

    def get_object(self, queryset=None):

        return get_object_or_404(LostItem, item_id=self.kwargs["item_id"])


class UserLostDeleteItemView(DeleteView):
    model = LostItem
    success_url = reverse_lazy("user_lostlistview")

    def get_object(self, queryset=None):

        return get_object_or_404(LostItem, item_id=self.kwargs["item_id"])

    def delete(self, request, *args, **kwargs):
        item = self.get_object()

        profile = self.request.user.profile
        return super().delete(request, *args, **kwargs)


class UserLostViewItem(LoginRequiredMixin, ListView):
    template_name = "app/user_lostviewitem.html"
    model = LostItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        """Show only items added by the logged-in user."""
        queryset = LostItem.objects.all()

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            LostItem.objects.filter(user=self.request.user)
            .values_list("category", flat=True)
            .distinct()
        )
        from Appli.models import School
        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


class UserLostDetailView(DetailView):
    model = LostItem
    template_name = "app/user_lostdetailview.html"
    context_object_name = "item"

    def get_object(self, queryset=None):

        item_id = self.kwargs.get("item_id")
        return LostItem.objects.get(item_id=item_id)


class UserFoundAddItemView(LoginRequiredMixin, CreateView):
    model = FoundItem
    form_class = FoundItemForm
    template_name = "app/user_foundadditem.html"
    success_url = reverse_lazy("user_foundlistview")

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.item_id:
            form.instance.item_id = form.instance._generate_unique_item_id()

        return super().form_valid(form)


class UserFoundListView(LoginRequiredMixin, ListView):
    template_name = "app/user_foundlistview.html"
    model = FoundItem
    context_object_name = "items"
    paginate_by = 15

    def get_queryset(self):
        queryset = FoundItem.objects.filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = FoundItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School
        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


class UserFoundUpdateItemView(UpdateView):
    model = FoundItem
    fields = [
        "item_name",
        "description",
        "category",
        "location_found",
        "found_by",
        "contact_information",
        "photo",
        "school",
    ]
    template_name = "app/found_updateitem.html"
    success_url = reverse_lazy("found_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(FoundItem, item_id=self.kwargs["item_id"])


class UserFoundDeleteItemView(DeleteView):
    model = FoundItem
    success_url = reverse_lazy("found_listview")

    def get_object(self, queryset=None):

        return get_object_or_404(FoundItem, item_id=self.kwargs["item_id"])

    def delete(self, request, *args, **kwargs):
        item = self.get_object()

        profile = self.request.user.profile
        return super().delete(request, *args, **kwargs)


class UserFoundViewItem(ListView):
    template_name = "app/user_foundviewitem.html"
    model = FoundItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = FoundItem.objects.filter(is_claimed=False)

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) | Q(item_id__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        school_id = self.request.GET.get("school")
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        order_by = self.request.GET.get("order_by", "desc")
        if order_by == "asc":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = FoundItem.objects.values_list(
            "category", flat=True
        ).distinct()
        from Appli.models import School

        context["schools"] = School.objects.all()
        context["today"] = date.today()
        return context

    def is_new(self, item):
        """Returns True if the item was created today."""
        return item.created_at.date() == date.today()


class UserFoundDetailView(DetailView):
    model = FoundItem
    template_name = "app/user_founddetailview.html"
    context_object_name = "item"

    def get_object(self, queryset=None):
        item_id = self.kwargs.get("item_id")
        return get_object_or_404(FoundItem, item_id=item_id)


class ClaimProcedureView(CreateView):
    model = ClaimProcedure
    form_class = F2FClaimProcedureForm
    template_name = "app/claim_procedure.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_id = self.kwargs["item_id"]
        found_item = get_object_or_404(FoundItem, id=item_id)
        context["found_item"] = found_item
        return context

    def form_valid(self, form):
        found_item = get_object_or_404(FoundItem, id=self.kwargs["item_id"])

        existing_claim = ClaimProcedure.objects.filter(
            found_item=found_item, claimed_by=form.cleaned_data["claimed_by"]
        ).first()

        if existing_claim:
            messages.info(
                self.request, "You have already initiated a claim for this item."
            )
            return redirect("user_foundviewitem")
        if found_item.is_claimed:
            messages.error(self.request, "This item has already been claimed.")
            return redirect("claim_f2fstatus")
        claim = form.save(commit=False)
        claim.found_item = found_item
        claim.status = "pending"
        claim.claim_type = "F2F"
        claim.school = form.cleaned_data.get("school")
        claim.save()
        claim.claim_id = f"CLAIM-{claim.id}"
        claim.save()
        found_item.is_claimed = True
        found_item.save()

        messages.success(
            self.request,
            "Face-to-face claim procedure initiated successfully, waiting for approval.",
        )
        return redirect("claim_f2fstatus")


class OnlineClaimProcedureView(CreateView):
    model = OnlineClaimProcedure
    form_class = OnlineClaimProcedureForm
    template_name = "app/user_claimprocedure.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_id = self.kwargs["item_id"]
        found_item = get_object_or_404(FoundItem, id=item_id)
        context["found_item"] = found_item
        return context

    def form_valid(self, form):
        found_item = get_object_or_404(FoundItem, id=self.kwargs["item_id"])

        existing_claim = OnlineClaimProcedure.objects.filter(
            found_item=found_item, claimed_by=form.cleaned_data["claimed_by"]
        ).first()

        if existing_claim:
            messages.info(
                self.request, "You have already initiated a claim for this item."
            )
            return redirect("user_foundviewitem")
        claim = form.save(commit=False)
        claim.found_item = found_item
        claim.status = "pending"
        claim.claim_type = "Online"
        claim.school = form.cleaned_data.get("school")
        claim.save()
        claim.claim_id = f"CLAIM-{claim.id}"
        claim.save()
        found_item.is_claimed = True
        found_item.save()

        messages.success(
            self.request,
            "Online claim procedure initiated successfully, waiting for approval.",
        )
        return redirect("user_foundviewitem")


class ClaimF2FStatusView(ListView):
    model = ClaimProcedure
    template_name = "app/claim_f2fstatus.html"
    context_object_name = "claims"
    paginate_by = 10

    def get_queryset(self):
        queryset = ClaimProcedure.objects.filter(
            status__in=["approved", "in_progress", "pending"]
        )

        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        school_id = self.request.GET.get("school")
        claim_type = self.request.GET.get("claim_type")
        status = self.request.GET.get("status")
        if q:
            queryset = queryset.filter(
                Q(claimed_by__icontains=q) | Q(found_item__item_name__icontains=q)
            )
        if category:
            queryset = queryset.filter(found_item__category=category)
        if school_id:
            queryset = queryset.filter(found_item__school_id=school_id)

        if claim_type:
            queryset = queryset.filter(claim_type=claim_type)
        if status:
            queryset = queryset.filter(status=status)
        order_by = self.request.GET.get("order_by", "asc")
        if order_by == "desc":
            queryset = queryset.order_by("-claimed_at")
        else:
            queryset = queryset.order_by("claimed_at")

        return queryset


class OnlineClaimStatusView(ListView):
    model = OnlineClaimProcedure
    template_name = "app/claim_onlinestatus.html"
    context_object_name = "claims"
    paginate_by = 10

    def get_queryset(self):
        queryset = OnlineClaimProcedure.objects.filter(
            status__in=["approved", "in_progress", "pending"]
        )

        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        school_id = self.request.GET.get("school")
        claim_type = self.request.GET.get("claim_type")
        status = self.request.GET.get("status")
        if q:
            queryset = queryset.filter(
                Q(claimed_by__icontains=q) | Q(found_item__item_name__icontains=q)
            )
        if category:
            queryset = queryset.filter(found_item__category=category)
        if school_id:
            queryset = queryset.filter(found_item__school_id=school_id)
        if claim_type:
            queryset = queryset.filter(claim_type=claim_type)
        if status:
            queryset = queryset.filter(status=status)
        order_by = self.request.GET.get("order_by", "asc")
        if order_by == "desc":
            queryset = queryset.order_by("-claimed_at")
        else:
            queryset = queryset.order_by("claimed_at")

        return queryset


@login_required
def update_f2f_claim_status(request, claim_id):
    claim = get_object_or_404(ClaimProcedure, id=claim_id, claim_type="F2F")

    if request.method == "POST":
        new_status = request.POST.get("status")
        claim.status = new_status
        claim.save()
        f2f_claim, created = F2FClaim.objects.get_or_create(
            found_item=claim.found_item,
            claimed_by=claim.claimed_by,
            defaults={
                "claimed_at": claim.claimed_at,
                "status": new_status,
                "school": claim.school,
                "claim_procedure": claim,
            },
        )

        if not created:
            f2f_claim.status = new_status
            f2f_claim.save()

        messages.success(
            request, f"Face-to-Face Claim updated with status '{new_status}'."
        )
        if new_status == "rejected":
            claim.found_item.is_claimed = False
            claim.found_item.save()
            claim.delete()
            f2f_claim.delete()

            messages.error(
                request, "Claim rejected, and item is now available for claiming again."
            )

    return redirect("claim_f2fstatus")


@login_required
def update_online_claim_status(request, claim_id):
    claim = get_object_or_404(OnlineClaimProcedure, id=claim_id, claim_type="Online")

    if request.method == "POST":
        new_status = request.POST.get("status")
        claim.status = new_status
        claim.save()
        online_claim, created = OnlineClaim.objects.get_or_create(
            found_item=claim.found_item,
            claimed_by=claim.claimed_by,
            defaults={
                "claimed_at": claim.claimed_at,
                "status": new_status,
                "school": claim.school,
                "claim_procedure": claim,
            },
        )

        if not created:
            online_claim.status = new_status
            online_claim.save()

        messages.success(request, f"Online Claim updated with status '{new_status}'.")
        if new_status == "rejected":
            claim.found_item.is_claimed = False
            claim.found_item.save()
            claim.delete()
            online_claim.delete()

            messages.error(
                request, "Claim rejected, and item is now available for claiming again."
            )

    return redirect("claim_onlinestatus")


class OnlineListView(ListView):
    model = OnlineClaim
    template_name = "app/user_onlineclaim.html"
    context_object_name = "online_claims"
    paginate_by = 10

    def get_queryset(self):
        return OnlineClaim.objects.filter(claim_type="Online")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_claims"] = OnlineClaim.objects.filter(
            claim_type="Online"
        ).count()
        return context


class School(TemplateView):
    template_name = "app/school.html"


class SchoolCreateView(CreateView):
    model = School
    form_class = SchoolForm
    template_name = "app/school_addschool.html"
    success_url = reverse_lazy("school_listview")


class SchoolListView(ListView):
    model = School
    template_name = "app/school_listview.html"
    context_object_name = "schools"
    paginate_by = 15

    def get_queryset(self):
        from Appli.models import School

        return School.objects.all().order_by("name")


class SchoolUpdateView(UpdateView):
    from Appli.models import School

    model = School
    template_name = "app/school_updateschool.html"
    form_class = SchoolForm
    context_object_name = "school"

    def get_success_url(self):
        return reverse_lazy("school_listview")


class SchoolDeleteView(DeleteView):
    from Appli.models import School

    model = School
    template_name = "app/school_deleteschool.html"
    context_object_name = "object"
    success_url = reverse_lazy("school_listview")
