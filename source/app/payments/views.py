# source/app/payments/views.py
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
from urllib.parse import urlencode

router = APIRouter()

DASHBOARD = "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app/payment-success"

@router.api_route("/payments/revolut/return", methods=["GET", "POST"])
async def revolut_return(request: Request):
    # Collect query params
    items = list(request.query_params.multi_items())

    # Also collect form params if it was a POST return
    if request.method == "POST":
        try:
            form = await request.form()
            items += list(form.multi_items())
        except Exception:
            pass

    qs = urlencode(items, doseq=True)
    # url = f"{DASHBOARD}?{qs}" if qs else DASHBOARD
    url = DASHBOARD
    return RedirectResponse(url=url, status_code=303)

@router.get("/payments/revolut/return/ping", include_in_schema=False)
async def ping():
    return PlainTextResponse("OK")
