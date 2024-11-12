

def inbox(request):
    """
    This function is responsible for handling the inbox of the user. 
    It will return all the notifications that the user has received. 
    """
    user = get_object_or_404(User, pk=user_id)
    notifications = Notification.objects.filter(user=user)
    return render(request, 'inbox.html', {'notifications': notifications})