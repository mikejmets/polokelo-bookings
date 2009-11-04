from google.appengine.api import users

def get_authentication_urls(dest_url):
    user = users.get_current_user()
    if user:
        return users.create_logout_url('/index'), 'Sign Out'
    else:
        return users.create_login_url(dest_url), 'Sign In'



