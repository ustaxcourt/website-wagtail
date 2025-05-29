from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import RoleSwitchForm, RevertRoleForm

User = get_user_model()

# Session Keys
SESSION_ORIGINAL_GROUPS_KEY = "original_groups_pks"
SESSION_ORIGINAL_IS_SUPERUSER_KEY = "original_is_superuser"
SESSION_ORIGINAL_IS_STAFF_KEY = "original_is_staff"
SESSION_IS_ASSUMING_ROLE_KEY = "is_assuming_role"
SESSION_ASSUMED_ROLE_NAME_KEY = "assumed_role_name"


@login_required
def switch_role_view(request):
    user = request.user
    is_currently_assuming_role = request.session.get(
        SESSION_IS_ASSUMING_ROLE_KEY, False
    )
    was_originally_superuser_when_switched = request.session.get(
        SESSION_ORIGINAL_IS_SUPERUSER_KEY, False
    )

    form_to_pass_in_context = None  # Initialize

    if request.method == "POST":
        if "assume_role" in request.POST:
            if not (user.is_superuser and not is_currently_assuming_role):
                messages.error(
                    request,
                    "Only active superusers who are not currently assuming another role can initiate a switch.",
                )
                return redirect(reverse("switch_role"))

            form = RoleSwitchForm(request.POST)
            if form.is_valid():
                selected_group = form.cleaned_data["role"]
                request.session[SESSION_ORIGINAL_GROUPS_KEY] = list(
                    user.groups.all().values_list("pk", flat=True)
                )
                request.session[SESSION_ORIGINAL_IS_SUPERUSER_KEY] = user.is_superuser
                request.session[SESSION_ORIGINAL_IS_STAFF_KEY] = user.is_staff

                current_user_in_db = User.objects.get(pk=user.pk)
                current_user_in_db.groups.clear()
                current_user_in_db.groups.add(selected_group)
                current_user_in_db.is_superuser = False
                current_user_in_db.is_staff = True
                current_user_in_db.save()

                request.session[SESSION_IS_ASSUMING_ROLE_KEY] = True
                request.session[SESSION_ASSUMED_ROLE_NAME_KEY] = selected_group.name
                messages.success(
                    request,
                    f"You are now assuming the role: {selected_group.name}. Your superuser status has been temporarily removed.",
                )
                return redirect(reverse("wagtailadmin_home"))
            else:
                form_to_pass_in_context = form  # Pass invalid form back to template

        elif "revert_role" in request.POST:
            if not (
                is_currently_assuming_role and was_originally_superuser_when_switched
            ):
                messages.error(
                    request,
                    "Revert action is not applicable or not permitted for your account.",
                )
                return redirect(reverse("wagtailadmin_home"))

            revert_form = RevertRoleForm(request.POST)
            if revert_form.is_valid():
                original_groups_pks = request.session.get(
                    SESSION_ORIGINAL_GROUPS_KEY, []
                )

                current_user_in_db = User.objects.get(pk=user.pk)
                current_user_in_db.is_superuser = request.session.get(
                    SESSION_ORIGINAL_IS_SUPERUSER_KEY, False
                )
                current_user_in_db.is_staff = request.session.get(
                    SESSION_ORIGINAL_IS_STAFF_KEY, False
                )

                current_user_in_db.groups.clear()
                if original_groups_pks:
                    original_groups = Group.objects.filter(pk__in=original_groups_pks)
                    current_user_in_db.groups.set(original_groups)
                current_user_in_db.save()

                for key in [
                    SESSION_ORIGINAL_GROUPS_KEY,
                    SESSION_ORIGINAL_IS_SUPERUSER_KEY,
                    SESSION_ORIGINAL_IS_STAFF_KEY,
                    SESSION_IS_ASSUMING_ROLE_KEY,
                    SESSION_ASSUMED_ROLE_NAME_KEY,
                ]:
                    request.session.pop(key, None)

                messages.success(
                    request, "Your original permissions have been restored."
                )
                return redirect(reverse("switch_role"))
            # else: an invalid revert_form POST will just re-render the GET page with default forms

    # --- GET request handling (or POST that falls through) ---
    can_initiate_new_switch = user.is_superuser and not is_currently_assuming_role

    context = {
        "request": request,  # Needed by SidebarController and other admin components
        "user": user,  # Explicitly pass user
        "is_assuming_role": is_currently_assuming_role,
        "assumed_role_name": request.session.get(SESSION_ASSUMED_ROLE_NAME_KEY, None),
        "title": "Switch User Role for Testing",  # Your page title
        "can_initiate_new_switch": can_initiate_new_switch,
        "role_switch_form": form_to_pass_in_context
        if form_to_pass_in_context
        else (RoleSwitchForm() if can_initiate_new_switch else None),
        "revert_role_form": RevertRoleForm(),
    }

    return render(request, "switch_role.html", context)
