from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .models import ForagingReport, ForagingReportSpecies
from .forms import ForagingReportForm, SPECIES_FORMSET_FIELDS
from basket.basket import Basket


@login_required
def report_create(request):
    """Create a new foraging report for the logged-in user."""
    basket = Basket(request)
    basket_items = list(basket)

    ForagingReportSpeciesFormSet = modelformset_factory(
        ForagingReportSpecies,
        fields=SPECIES_FORMSET_FIELDS,
        extra=len(basket_items),
    )

    if request.method == 'POST':
        report_form = ForagingReportForm(request.POST)
        species_formset = ForagingReportSpeciesFormSet(
            request.POST,
            queryset=ForagingReportSpecies.objects.none(),
        )

        if report_form.is_valid() and species_formset.is_valid():
            report = report_form.save(commit=False)
            report.user = request.user
            report.save()

            species_items = species_formset.save(commit=False)
            for item in species_items:
                item.report = report
                item.save()

            basket.clear()
            return redirect('fieldnotes:report_detail', pk=report.pk)
    else:
        report_form = ForagingReportForm()
        initial = [
            {'species': item['species'], 'quantity': item.get('quantity', 1)}
            for item in basket_items
        ]
        species_formset = ForagingReportSpeciesFormSet(
            queryset=ForagingReportSpecies.objects.none(),
            initial=initial,
        )

    return render(request, 'fieldnotes/report_create.html', {
        'form': report_form,
        'species_formset': species_formset,
    })

@login_required
def report_list(request):
    """List all foraging reports for the logged-in user."""
    reports = ForagingReport.objects.filter(user=request.user)

    # Optional date filters from query params
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if date_from:
        reports = reports.filter(date_foraged__gte=date_from)
    if date_to:
        reports = reports.filter(date_foraged__lte=date_to)

    return render(request, 'fieldnotes/report_list.html', {
        'reports':reports,
        'date_from':date_from,
        'date_to':date_to,
    })


@login_required
def report_detail(request, pk):
    """View a single foraging report (must belong to the logged-in user)."""
    report = ForagingReport.objects.get(pk=pk, user=request.user)
    return render(request, 'fieldnotes/report_detail.html', {'report': report})


