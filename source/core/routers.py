from fastapi import APIRouter

from source.app.auth.views   import auth_router
from source.app.users.views  import users_router
from source.app.access.views import access_router
from source.app.predictions.views import predictions_router
from source.app.subscriptions import subscriptions_router
from source.app.admin.views import router as admin_router
from source.app.payments.views import router as revolut_return_router
from source.app.MAX.views import max_router
from source.app.MAX.api.max_enhanced_endpoints import router as max_enhanced_router
from source.app.dev.views import dev_router

api_router = APIRouter()

api_router.include_router(auth_router)

api_router.include_router(users_router)

api_router.include_router(access_router)

api_router.include_router(predictions_router)

api_router.include_router(subscriptions_router)

api_router.include_router(admin_router)

api_router.include_router(revolut_return_router)

api_router.include_router(max_router)

# Development endpoints - only active when DEBUG=True
api_router.include_router(dev_router)

api_router.include_router(max_enhanced_router)