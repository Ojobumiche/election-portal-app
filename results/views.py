from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from .models import PollingUnit, AnnouncedPUResult, LGA


def polling_unit_result(request):
    polling_units = PollingUnit.objects.all().order_by('polling_unit_name')[:100]
    selected_unit = None
    results = None

    pu_id = request.GET.get('pu')

    if pu_id:
        selected_unit = get_object_or_404(PollingUnit, uniqueid=pu_id)
        results = AnnouncedPUResult.objects.filter(
            polling_unit_uniqueid=pu_id
        ).order_by('party_abbreviation')

    context = {
        'polling_units': polling_units,
        'selected_unit': selected_unit,
        'results': results
    }

    return render(request, 'results/polling_unit_result.html', context)

def lga_summed_result(request):

    # Load all LGAs
    lgas = LGA.objects.all().order_by('lga_name')

    summed_results = None
    selected_lga = None

    lga_id = request.GET.get('lga')

    if not lga_id:
        for candidate_lga_id in (
            PollingUnit.objects
            .values_list('lga_id', flat=True)
            .distinct()
            .order_by('lga_id')
        ):
            candidate_unit_ids = PollingUnit.objects.filter(
                lga_id=candidate_lga_id
            ).values_list('uniqueid', flat=True)
            has_results = AnnouncedPUResult.objects.filter(
                polling_unit_uniqueid__in=candidate_unit_ids
            ).exists()
            if has_results:
                lga_id = candidate_lga_id
                break

    if lga_id:

        # Get selected LGA safely
        selected_lga = get_object_or_404(LGA, lga_id=lga_id)

        # Get polling units under selected LGA
        polling_units = PollingUnit.objects.filter(
            lga_id=lga_id
        )

        # Extract polling unit IDs
        pu_ids = polling_units.values_list(
            'uniqueid',
            flat=True
        )

        # Sum party scores
        summed_results = (
            AnnouncedPUResult.objects
            .filter(polling_unit_uniqueid__in=pu_ids)
            .values('party_abbreviation')
            .annotate(total_score=Sum('party_score'))
            .order_by('-total_score')
        )

    context = {
        'lgas': lgas,
        'selected_lga': selected_lga,
        'summed_results': summed_results,
    }

    return render(request, 'results/lga_result.html', context)


def add_polling_unit_result(request):
    parties = ['PDP', 'DPP', 'ACN', 'PPA', 'CDC', 'JP', 'ANPP', 'LABO', 'CPP']
    polling_units = PollingUnit.objects.all().order_by('polling_unit_name')

    if request.method == 'POST':
        polling_unit_uniqueid = request.POST.get('polling_unit_uniqueid')

        if not polling_unit_uniqueid:
            messages.error(request, "Polling Unit ID is required.")
            return redirect('add_result')

        for party in parties:
            score = int(request.POST.get(party, 0) or 0)

            AnnouncedPUResult.objects.create(
                polling_unit_uniqueid=polling_unit_uniqueid,
                party_abbreviation=party,
                party_score=score,
                entered_by_user=request.POST.get('entered_by_user', '').strip() or 'Anonymous',
                date_entered=timezone.now(),
                user_ip_address=request.META.get('REMOTE_ADDR', ''),
            )

        messages.success(request, "Polling unit result added successfully.")
        return redirect('polling_unit_result')

    return render(request, 'results/add_result.html', {
        'parties': parties,
        'polling_units': polling_units,
    })
