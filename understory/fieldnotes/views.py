from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ForagingReport, ForagingReportSpecies
from .forms import ForagingReportForm
from basket.basket import Basket


@login_required
def report_create(request):
    """Create a new foraging report for the logged-in user."""
    basket = Basket(request)

    if request.method == 'POST':
        form = ForagingReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            # Save each species in the basket as a ForagingReportSpecies item
            for item in basket:
                ForagingReportSpecies.objects.create(
                    report=report,
                    species=item['species'],
                    quantity=1,
                )
            basket.clear()
            return redirect('fieldnotes:report_detail', pk=report.pk)
            
    else:
        form = ForagingReportForm()
    return render(request, 'fieldnotes/report_create.html', {'form': form})


@login_required
def report_list(request):
    """List all foraging reports for the logged-in user."""
    reports = ForagingReport.objects.filter(user=request.user)
    return render(request, 'fieldnotes/report_list.html', {'reports': reports})


@login_required
def report_detail(request, pk):
    """View a single foraging report (must belong to the logged-in user)."""
    report = ForagingReport.objects.get(pk=pk, user=request.user)
    return render(request, 'fieldnotes/report_detail.html', {'report': report})
