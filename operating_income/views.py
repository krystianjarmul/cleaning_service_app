import io

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from invoices.repositories import EmployersRepository
from .services import GenerateOperatingIncomeExcelFileService


@csrf_exempt
def home(request):
    return render(request, 'operating_income/index.html', context={})

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return HttpResponseBadRequest('No file part')

        if uploaded_file.name == '':
            return HttpResponseBadRequest('No selected file')

        content = uploaded_file.read()
        input_file = io.StringIO(content.decode('ISO-8859-1'))
        output_file = io.BytesIO()

        employer_repo = EmployersRepository()
        service = GenerateOperatingIncomeExcelFileService(employer_repo=employer_repo)
        service.generate(input_file=input_file, output_file=output_file)
        output_file.seek(0)

        response = HttpResponse(output_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.name[:-4]}_processed.xlsx"'
        return response

    return HttpResponseBadRequest('Invalid request method')
