from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login
from ssoready.client import SSOReady

# Do not hard-code or leak your SSOReady API key in production!
#
# In production, instead you should configure a secret SSOREADY_API_KEY
# environment variable. The SSOReady SDK automatically loads an API key from
# SSOREADY_API_KEY.
#
# This key is hard-coded here for the convenience of logging into a test app,
# which is hard-coded to run on http://localhost:8000. It's only because of
# this very specific set of constraints that it's acceptable to hard-code and
# publicly leak this API key.
ssoready = SSOReady(api_key="ssoready_sk_3hb8m7tr22zqcg0sx9f0gg3e3")


# This demo just renders plain old HTML with no client-side JavaScript. This is
# only to keep the demo minimal. SSOReady works with any frontend stack or
# framework you use.
#
# This demo keeps the HTML minimal to keep things as simple as possible here.
def index(request):
    return render(request, "exampleapp/index.html")


# This is the page users visit when they submit the "Log in with SAML" form in
# this demo app.
def saml_redirect(request):
    # To start a SAML login, you need to redirect your user to their employer's
    # particular Identity Provider. This is called "initiating" the SAML login.
    #
    # Use `saml.get_saml_redirect_url` to initiate a SAML login.
    redirect_url = ssoready.saml.get_saml_redirect_url(
        # OrganizationExternalId is how you tell SSOReady which company's
        # identity provider you want to redirect to.
        #
        # In this demo, we identify companies using their domain. This code
        # converts "john.doe@example.com" into "example.com".
        organization_external_id=request.GET.get("email").split("@")[1]
    ).redirect_url

    # `saml.get_saml_redirect_url` returns an object like this:
    #
    # GetSamlRedirectUrlResponse(redirect_url="https:#...")
    #
    # To initiate a SAML login, you redirect the user to that redirect_url.
    return redirect(redirect_url)


# This is the page SSOReady redirects your users to when they've successfully
# logged in with SAML.
def ssoready_callback(request):
    # SSOReady gives you a one-time SAML access code under
    # ?saml_access_code=saml_access_code_... in the callback URL's query
    # parameters.
    #
    # You redeem that SAML access code using `saml.redeem_saml_access_code`,
    # which gives you back the user's email address. Then, it's your job to log
    # the user in as that email.
    email = ssoready.saml.redeem_saml_access_code(
        saml_access_code=request.GET.get("saml_access_code")
    ).email

    # SSOReady works with any user model / session model / authentication
    # backend you use. In this demo, we use the builtin django.contrib.auth
    # module to keep things simple and as vanilla as possible.

    # Find or create a user instance for this request, going off of the email
    # address.
    user, _ = get_user_model().objects.get_or_create(email=email, defaults={'username': email})

    # Log the user in as the acquired user.
    login(request, user)

    # Redirect back to the demo app homepage.
    return redirect("/")
