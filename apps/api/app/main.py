from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import admin, auth, billing, contracts, library, opportunities, organization, partners, past_performance, proposals
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-Id"],
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
    return response


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "grantatlas-api"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organization.router, prefix="/organization", tags=["organization"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
app.include_router(library.router, prefix="/library", tags=["library"])
app.include_router(partners.router, prefix="/partners", tags=["partners"])
app.include_router(past_performance.router, prefix="/past-performance", tags=["past-performance"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
