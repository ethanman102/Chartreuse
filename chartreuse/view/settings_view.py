from django.views.generic.detail import DetailView
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import User

@login_required
def update_password(request):
    if request.method == "POST":

        original_password = request.POST.get("old_pass")
        new_password = request.POST.get("new_pass")

        current_user = request.user
        
        if not check_password(original_password,current_user.password):
            response = JsonResponse({"error": "Old password invalid"}, status=403)
            return response
        
        try:
            validate_password(new_password)
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)
        
        current_user.set_password(new_password)
        return JsonResponse({'success': 'Password successfully changed'},status=200)
            
@login_required
class SettingsView(DetailView):

    model = User
    template_name = "settings.html"
    context_object_name= "user"
        
    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
        authenticated_user = self.request.user
        return User.objects.filter(user=authenticated_user)

