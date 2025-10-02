from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

# Create the API instance
api = NinjaExtraAPI()

# Register the default JWT controllers for login, refresh, etc.
api.register_controllers(NinjaJWTDefaultController)

# Include the API in your project's urls.py
# from .api import api
# urlpatterns = [
#     path('api/auth/', api.urls),
# ]   