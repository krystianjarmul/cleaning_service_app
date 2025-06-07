import csv
import os
import io
import datetime

import xlsxwriter

from invoices.drive import GoogleDriveClient
from invoices.repositories import EmployersRepository

MWST = 0.19
START_INDEX = 10



EN_TO_DE_MONTHS_MAPPER = {
    "January": "Januar",
    "February": "Februar",
    "March": "März",
    "April": "April",
    "May": "Mai",
    "June": "Juni",
    "July": "Juli",
    "August": "August",
    "September": "September",
    "October": "Oktober",
    "November": "November",
    "December": "Dezember"
}

class GenerateOperatingIncomeExcelFileService:

    def __init__(self, drive: GoogleDriveClient, employer_repo: EmployersRepository):
        self.drive = drive
        self.employer_repo = employer_repo

    def generate(self, csv_file, output_file: io.BytesIO) -> None:

        workbook = xlsxwriter.Workbook(output_file, options={"in_memory": True})
        worksheet = workbook.add_worksheet()

        currency_format = workbook.add_format({"num_format": "0.00", "font": "Times New Roman"})
        border_format = workbook.add_format({"top": 1})
        header_format = workbook.add_format({"font": "Times New Roman", "bold": True})
        title_format = workbook.add_format({"font": "Times New Roman", "bold": True, "font_size": 13, "align": "left"})
        cell_format = workbook.add_format({"font": "Times New Roman"})

        employer = EmployersRepository().get()

        company = employer.data['company']
        owner = employer.data['name']
        street_address = employer.data['address']['street_name']
        city = employer.data['address']['city']
        zip_code = employer.data['address']['zip_code']

        worksheet.write("A2", company, header_format)
        worksheet.write("A3", owner, header_format)
        worksheet.write("A4", street_address, header_format)
        worksheet.write("A5", f"{zip_code} {city}", header_format)

        worksheet.write("D6", "  Betriebseinnahmen", title_format)

        worksheet.write("A9", "Bezeichnung", cell_format)
        worksheet.write("B9", "Rech,Nr.", cell_format)
        worksheet.write("C9", "Datum", cell_format)
        worksheet.write("D9", "Name", cell_format)
        worksheet.write("E9", "Netto", cell_format)
        worksheet.write("F9", "MwSt", cell_format)
        worksheet.write("G9", "Brutto", cell_format)

        reader = csv.DictReader(csv_file, delimiter=";")

        row_counter = 1
        for row in list(reader)[::-1]:

            if row_counter == 1:
                date_str = row.get("Buchungstag")
                date = datetime.datetime.strptime(date_str, "%d.%m.%y")
                month_en = date.strftime("%B")
                month_de = EN_TO_DE_MONTHS_MAPPER.get(month_en)
                worksheet.write("D7", f"       {month_de} {date.year}", title_format)

            brutto_str = row.get("Betrag")

            if brutto_str.startswith("-"):
                continue

            date_str = row.get("Buchungstag")
            name = row.get("Beguenstigter/Zahlungspflichtiger")
            brutto = float(brutto_str.replace(",", "."))
            row_idx = START_INDEX + row_counter

            worksheet.write(f"A{row_idx}", row_counter, cell_format)
            worksheet.write(f"B{row_idx}", "", cell_format)
            worksheet.write(f"C{row_idx}", date_str, cell_format)
            worksheet.write(f"D{row_idx}", name, cell_format)
            worksheet.write(f"E{row_idx}", f"=G{row_idx} / {1 + MWST}", currency_format)
            worksheet.write(f"F{row_idx}", f"=E{row_idx} * {MWST}", currency_format)
            worksheet.write(f"G{row_idx}", brutto, currency_format)
            row_counter += 1

        for col in range(0, 6 + 1):
            worksheet.write(row_idx, col, '', border_format)

        worksheet.write(f"E{row_idx + 2}", f"=SUM(E11:E{row_idx})", currency_format)
        worksheet.write(f"F{row_idx + 2}", f"=SUM(F11:F{row_idx})", currency_format)
        worksheet.write(f"G{row_idx + 2}", f"=SUM(G11:G{row_idx})", currency_format)

        workbook.close()
