from ninja import Router
from core.utils.security import AuthBearer, BasicAuth
from django.http import JsonResponse
from core.models.Credential import CREDENTIALS_TYPES
from core.utils.tasks import load_plugins

router = Router(tags=["Utils"], auth=[AuthBearer(), BasicAuth()])

TYPES = {
    "scanners": [t for t in load_plugins("scanners").keys()],
    "pullers": [t for t in load_plugins("pullers").keys()],
    "credentials": [t for t in CREDENTIALS_TYPES.keys() if t not in ["PublicGit", "PublicSvn"]]
}


@router.get('/types/{type_to_list}')
def get_types(request, type_to_list: str):
    t = TYPES.get(type_to_list, None)
    if t:
        return JsonResponse({"items": t, "total_count": len(t)})
    elif type_to_list == "all":
        data = {}
        for key in TYPES.keys():
            data[key] = {"items": TYPES[key], "total_count": len(TYPES[key])}
        return JsonResponse(data)
    return JsonResponse({}, status=404)
