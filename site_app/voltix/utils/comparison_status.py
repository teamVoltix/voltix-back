from django.db.models import Case, When, Value, CharField, Exists, OuterRef
from ..models import InvoiceComparison

def annotate_comparison_status(queryset, related_field):
    """
    Annotates a queryset with a 'comparison_status' field based on related comparisons.

    :param queryset: The queryset to annotate.
    :param related_field: The field linking the model to the InvoiceComparison (e.g., 'invoice' or 'measurement').
    :return: The annotated queryset.
    """
    comparison_subquery = InvoiceComparison.objects.filter(**{f"{related_field}_id": OuterRef('pk')})

    return queryset.annotate(
        comparison_status=Case(
            When(~Exists(comparison_subquery), then=Value("Sin comparacion")),
            When(Exists(comparison_subquery.filter(is_comparison_valid=True)), then=Value("Sin discrepancia")),
            When(Exists(comparison_subquery.filter(is_comparison_valid=False)), then=Value("Con discrepancia")),
            default=Value("unknown"),
            output_field=CharField(),
        )
    )
