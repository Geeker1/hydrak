"""
HANDLING AUTENTICATION

Rest has the following backends for authentication

BasicAuthentication: The user and password are sent by the client 
in Authorization HTTP header encoded with Base64

TokenAuthentication: Token-based authentication. Token model used to store user
tokens which are included in the Authorization HTTP header for authentication


SessionAuthentication: Uses Django's session backend for authentication.
This is useful in performing authenticated AJAX Requests to the API from your websites 
frontend


Viewsets lets you define the interaction with API
 while REST builds the urls dynamically

"""