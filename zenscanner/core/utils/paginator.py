from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.core.paginator import Paginator as Django_Paginator, EmptyPage


MAX_VALUE = 100
MIN_VALUE = 0
DEFAULT_VALUE = 10


class Paginator():

    model = None
    count = 0
    default_order = None

    def __init__(self, model, default_order="-id"):
        self.default_order = default_order
        if isinstance(model, ModelBase):
            self.model = model.objects
        else:
            self.model = model

    def filter(self, *args, **kwargs):
        self.model = self.model.filter(*args, **kwargs)

    def paginated_response(self, items):
        return JsonResponse({
            "items": items,
            "total_count": self.count
        }, status=200, safe=False)

    def paginate(self, params):
        page = params.get("page", 1)
        per_page = params.get("per_page", DEFAULT_VALUE)

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = DEFAULT_VALUE

        if per_page < MIN_VALUE or per_page > MAX_VALUE:
            per_page = DEFAULT_VALUE

        elif per_page == MIN_VALUE:
            self.count = self.model.count()
            return []

        if params.get("order_by", None):
            direction = "" if params.get("ascending", "1") in ["1", True] else "-"
            self.model = self.model.order_by("{}{}".format(direction, params.get("order_by")))
        elif self.default_order:
            self.model = self.model.order_by(self.default_order)

        if not isinstance(self.model, QuerySet):
            self.model = self.model.all()

        p = Django_Paginator(self.model, per_page)
        self.count = p.count

        try:
            return p.page(page)
        except EmptyPage:
            return []
