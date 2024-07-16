from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm, ProfileImageForm  # Import ProfileImageForm
from django.views.decorators.http import require_POST
from .models import WebsiteUser
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from .forms import UploadedItemForm
from .models import UploadedItem,Question,Answer, Notification
from django.conf import settings
from django.contrib.auth import logout
from django.urls import reverse



def custom_404(request, exception):
    # Redirect users to the login page
    return redirect(reverse('login'))
    
def index(request):
    return render(request,'index.html')

@require_POST
def check_username_availability(request):
    username = request.POST.get('username')
    data = {'available': not WebsiteUser.objects.filter(username=username).exists()}
    if not data['available']:
        data['error'] = 'This username is already taken.'
    return JsonResponse(data)
    
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Your account has been created! You can now log in.'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})

    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

from django.contrib.auth import authenticate, login as auth_login

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate against WebsiteUser model
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_verified:
                    auth_login(request, user)
                    return JsonResponse({'success': True, 'redirect_url': 'profile'})
                else:
                    return JsonResponse({'success': False, 'message': 'Your account is not verified. Please contact the administrator.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid username or password'})

        # Form is not valid
        error_messages = [error for field, errors in form.errors.items() for error in errors]
        return JsonResponse({'success': False, 'message': error_messages})
    
    # If the request is not POST, return the login form
    form = LoginForm()
    return render(request, 'login.html', {'form': form})



def logout_user(request):
    logout(request)
    return redirect('login')
 

@login_required
def profile(request):
    user = request.user
    
    if request.method == 'POST':
        if 'profile_image' in request.FILES:
            profile_form = ProfileImageForm(request.POST, request.FILES, instance=user)
            uploaded_item_form = UploadedItemForm(request.POST, request.FILES)

            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')  # Redirect to profile page after profile image upload

        elif 'image' in request.FILES:            # Process the uploaded item form
            name = request.POST.get('name')
            description = request.POST.get('description')
            location = request.POST.get('location')
            image = request.FILES.get('image')
            
            uploaded_item=UploadedItem.objects.create(
                uploader=user,
                name=name,
                description=description,
                location=location,
                image=image
            )
            uploaded_item.save()
            questions_data = request.POST.getlist('questions[]')
            for question_text in questions_data:
                question = Question(item=uploaded_item, text=question_text)
                question.save()

            return redirect('profile')  # Redirect to profile page after item upload

        elif 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            item = get_object_or_404(UploadedItem, pk=item_id)
            if item.uploader == user:  # Ensure the user owns the item
                item.delete()
                return redirect('profile')

    else:
        profile_form = ProfileImageForm(instance=user)
        uploaded_item_form = UploadedItemForm()
    
    notifications = Notification.objects.filter(user=user)
    uploaded_items = UploadedItem.objects.filter(uploader=user)
    claimed_items = UploadedItem.objects.filter(answers__user=user).distinct()  # Fetch claimed items by the current user


    return render(request, 'profile.html', {'user': user, 'uploaded_items': uploaded_items, 'profile_form': profile_form, 'uploaded_item_form': uploaded_item_form,'notifications': notifications, 'claimed_items': claimed_items})

@login_required
def main_page(request):
    user = request.user
    found_items = UploadedItem.objects.all()
    return render(request,'main.html',{'user': user,'found_items':found_items} )

def get_item_details(request, item_id):
    try:
        item = UploadedItem.objects.get(pk=item_id)
        item_details = {
            'name': item.name,
            'description': item.description,
            'location': item.location,
            'claimed': item.claimed,  # Include the claimed status in the response
            'questions': [{'text': question.text} for question in item.questions.all()]
        }
        return JsonResponse(item_details)
    except UploadedItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required
def submit_answers(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')
        item = get_object_or_404(UploadedItem, pk=item_id)
        user = request.user
        
        # Check if the user has already submitted answers for this item
        if Answer.objects.filter(item=item, user=user).exists():
            return JsonResponse({'success': False, 'message': 'You have already submitted answers for this item.'})

        answers = []

        for key, value in request.POST.items():
            if key.startswith('answer'):
                question_index = int(key[6:]) - 1  # Extract question index from key
                question = item.questions.all()[question_index]
                answer = Answer(item=item, user=user, question=question, answer_text=value)
                answers.append(answer)

        # Save answers
        Answer.objects.bulk_create(answers)

        # Update item status to claimed
        item.save()

        return JsonResponse({'success': True, 'message': 'Answers submitted successfully'})


        


@login_required
def get_claims_and_responses(request, item_id):
    try:
        claims = Answer.objects.filter(item_id=item_id).values(
            'user_id',
            'user__username',
            'user__profile_image',
            'question__text',
            'answer_text'
        )
        return JsonResponse(list(claims), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



import logging
logger = logging.getLogger(__name__)


@login_required
def approve_claim(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')
        user_id = request.POST.get('userId')  # Retrieve userId from POST data

        logger.debug(f"Received request to approve claim for User ID: {user_id}, Item ID: {item_id}")

        try:
            # Ensure that the claimed user exists in the system
            claimed_user = get_object_or_404(WebsiteUser, id=user_id)

            logger.debug(f"Found WebsiteUser with ID: {claimed_user.id}")

            # Retrieve the current logged-in user who approves the claims
            approver = request.user

            # Retrieve the item name
            item_name = UploadedItem.objects.get(id=item_id).name
            item = UploadedItem.objects.get(id=item_id)
            # Save the notification message
            notification_message = f"Your claim for item '{item_name}' has been approved by {approver.first_name}. " \
                                   f"You can contact at {approver.phone_number}."
            Notification.objects.create(user=claimed_user, message=notification_message,
                                         approver_username=approver.first_name, 
                                         approver_phone_number=approver.phone_number)

            # Additional actions related to approving the claim can be added here
            item.claimed=True
            item.save()
            return JsonResponse({'success': True})
        except WebsiteUser.DoesNotExist:
            logger.error('No WebsiteUser matches the given query.')
            return JsonResponse({'success': False, 'error': 'Claimed user does not exist'}, status=404)
        except Exception as e:
            logger.exception('Error approving claim')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)