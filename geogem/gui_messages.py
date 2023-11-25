from django.utils.translation import gettext_lazy as _


GUI_MESSAGES = {
    'accounts': {
        # Translators: this is a login title
        'login_title': _('Login'),
        # Translators: this is a login button
        'login_button': _('Login'),
        # Translators: this is a register title
        'register_title': _('Register'),
        # Translators: this is a register button
        'register_button': _('Register'),
        # Translators: this is an input form element
        'username': _('Username'),
        # Translators: this is an error message
        'username_taken': _('This username is already taken.'),
        # Translators: this is an input form element
        'password': _('Password'),
        # Translators: this is an input form element
        'password_repeat': _('Repeat Password'),
        # Translators: this is an input form element
        'password_forgot': _('Forgot Password?'),
        # Translators: this is an input form element
        'email': _('Email'),
        # Translators: this appears on the login page
        "do_not_have_account": _("Don't have an account?"),
        # Translators: this appears on the login page
        'register_now': _('Register Now!'),
        # Translators: this appears on the register page
        'already_have_account': _('Already have an account?'),
        # Translators: this appears on the register page
        'sign_in_now': _('Sign In Now!'),
        # Translators: this appears on the register page
        'registration_requirements': _('Registration requirements'),
        # Translators: this appears on the register page
        'registration_requirements_text': _("""<li>Only latin letters are allowed.</li>
<li>Username must contain only letters, digits and . + - _</li>
<li>Username must be at least 3 characters and no more than 15.</li>
<li>Your password can't be too similar to your other personal information.</li>
<li>Your password must contain at least 8 characters.</li>
<li>Your password can't be a commonly used password.</li>
<li>Your password can't be entirely numeric.</li>"""),
    },
    'base': {
        # Translators: this is a navbar item
        'home': _('Home'),
        # Translators: this is a navbar item
        'learn': _('Learn'),
        # Translators: this is a navbar item
        'my_words': _('My Words'),
        # Translators: this is a navbar item
        'about': _('About'),
        # Translators: this is a navbar item
        'premium': _('Premium'),
        # Translators: this appears in the navbar
        'greetings': _('Hi'),
        # Translators: this is a navbar item
        'my_profile': _('My Profile'),
        # Translators: this is a navbar item
        'logout': _('Log out'),
        # Translators: this is a navbar item
        'admin_panel': _('Admin'),
        # Translators: this is a navbar item
        'login': _('Login'),
        # Translators: this is a navbar item
        'register': _('Register'),
    },
    'messages': {
        'badge_earned': _('You have earned a badge! Check out your profile!'),
        'user_deleted': _('The user has been successfully deleted'),
        'email_subject': _('Confirm your account on GeoGem'),
        'email_sent': _('<b>{user}</b>, please check your email <b>{to_email}</b> to activate your account.'),
        'activation_successful': _('Thank you for confirming your email. You can now sign in to your account.'),
    },
    'error_messages': {
        'email_sent': _('Problem sending email to <b>{to_email}</b>, please try again.'),
        'activation_failed': _('Activation link is invalid! Please try again.'),
        'all_fields_required': _('Please fill out all the required fields.'),
    },
    'forms': {        
        'error_captcha': _('You must pass the reCAPTCHA test'),
        'error_username_contains_spaces': _('Username cannot contain spaces'),
        'error_username_contains_invalid_chars': _('Username contains invalid characters'),
        'error_username_too_short': _('Username is too short'),
        'error_username_too_long': _('Username is too long'),
        'error_invalid_email': _('Email contains invalid characters'),
        'error_password_too_short': _('Password is too short'),
        'error_passwords_do_not_match': _('Passwords do not match'),
        'error_invalid_credentials': _('Invalid username or password'),
    },
    'my_profile': {
        'welcome': _('Welcome'),
        'home': _('Home'),
        'profile': _('Profile'),
        'settings': _('Settings'),
        'achievements': _('Achievements'),
        'date_joined': _('Date joined'),
        'has_premium': _('You have premium status'),
        'no_premium': _('You have free status.'),
        'upgrade_to_premium': _('Upgrade to premium'),
        'delete_account': _('Delete account'),
        'delete_account_confirm': _('Are you sure you want to delete your account?'),
        'total_words': _('Number of learned words:'),
    },
    'about': {
        'about_geogem': _('About GeoGem'),
        'about_geogem_text': _('GeoGem is a project for learning Georgian words and exploring Georgian culture!'),
        'source_code': _('Source code is available on GitHub'),
    },
    'premium': {
        'not_authenticated': _('Premium is only available for registered users. Sign in and try again.'),
        # Translators: this is the title of the "Premium" page
        'premium_title': _('Premium'),
        'premium_description': _('Get access to the following premium features:'),
        'premium_features': _('''<li>Premium users can do some more</li>
<li>and later they'll do much more than that</li>
<li>And many more...</li>'''),
        # Translators: this is a "Get Premium" button
        'button_get_premium': _('Try out for free!'),
        'thank_you_premium': _('Thank you for upgrading to premium!<br>Enjoy all the features we have to offer!'),
        # Translators: this is a "Cancel Premium" button
        'button_cancel_premium': _('Cancel Premium'),
    },
    'tooltips': {
        'block_mastery_level_help': _('Every time you answer a question correctly, you get a point. Incorrect answers decrease points. The more points you have, the higher your mastery level is.'),
        'block_fully_learned': _('You have learned all words in this block!'),
        'log_in_to_review': _('Sign in to save your progress'),
        'no_review_words': _('No words to review'),
        'never_give_up': _('Never give up!'),
    },
    'column_titles': {
        # Translators: this is a column title
        'title_word_name': _('Name'),
        # Translators: this is a column title
        'title_image': _('Image'),
        # Translators: this is a column title
        'title_audio': _('Audio'),
        # Translators: this is a column title
        'title_points': _('Points'),
        # Translators: this is a column title
        'title_level': _('Level'),
        # Translators: this is a column title
        'title_mastery_level': _('Mastery level'),
        # Translators: this is a column title
        'title_transliteration': _('Transliteration'),
        # Translators: this is a column title
        'title_translation': _('Translation'),
        # Translators: this is a column title
        'title_example': _('Example'),
        # Translators: this is a column title
        'title_example_image': _('Example Image'),
        # Translators: this is a column title
        'title_added_at': _('Added at'),
    },
    'my_words_title': _('My Words'),
}