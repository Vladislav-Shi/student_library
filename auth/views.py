from django.shortcuts import render

# Create your views here.
from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        print(user_form.data)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'register_done.html', {'new_user': new_user})
        else:
            p = ''
            for field, errors in user_form.errors.items():
                # field содержит имя поля, а errors список ошибок для этого поля
                print(f"Errors in {field}: {', '.join(errors)}")
                p += f"Errors in {field}: {', '.join(errors)}\n"
            print('form is not valid')
            user_form = UserRegistrationForm()
            return render(request, 'register.html', {'user_form': user_form, 'error_message': p})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form, 'error_message': ''})
