from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from django.conf import settings

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&') if param)
        token = query_params.get('token', None)
        

        # Default to AnonymousUser
        scope['user'] = AnonymousUser()

        
        
        if token:
            try:
                # Verify the token
                valid_token = AccessToken(token)
                user_id = valid_token['user_id']
                
                # Get the user model outside the try block
                User = get_user_model()
                
                try:
                    # Get the user instance
                    user = await database_sync_to_async(User.objects.get)(id=user_id)
                    scope['user'] = user
                except User.DoesNotExist:
                    # Keep the default AnonymousUser if user doesn't exist
                    pass
                    
            except (InvalidToken, TokenError):
                # Keep the default AnonymousUser if token is invalid
                pass
        
        return await super().__call__(scope, receive, send)