import csv
import os
import random
import uuid
from faker import Faker
from slugify import slugify

from fake_csv_service import settings


def generate_csv(schema, rows):
    fake = Faker()
    columns = schema.columns.all()
    field_order = {column.order: column.name for column in columns}
    fieldnames = [field_order[order] for order in sorted(field_order.keys())]
    data = []

    for _ in range(rows):
        row = {}
        for column in columns:
            data_type = column.data_type
            range_from = column.range_from
            range_to = column.range_to
            if data_type == "Full name":
                row[column.name] = fake.name().replace("\n", " ").replace(",", "")
            elif data_type == "Job":
                row[column.name] = fake.job().replace("\n", " ").replace(",", "")
            elif data_type == "Email":
                row[column.name] = fake.email().replace("\n", " ").replace(",", "")
            elif data_type == "Domain name":
                row[column.name] = fake.domain_name().replace("\n", " ").replace(",", "")
            elif data_type == "Phone number":
                row[column.name] = fake.phone_number()
            elif data_type == "Company name":
                row[column.name] = fake.company().replace("\n", " ").replace(",", "")
            elif data_type == "Text":
                sentences_number = random.randint(range_from, range_to)
                row[column.name] = fake.paragraph(
                    variable_nb_sentences=True, nb_sentences=sentences_number
                ).replace("\n", " ").replace(",", "")
            elif data_type == "Integer":
                row[column.name] = fake.random_int(min=range_from, max=range_to)
            elif data_type == "Address":
                row[column.name] = fake.address().replace("\n", " ").replace(",", "")
            elif data_type == "Date":
                row[column.name] = fake.date().replace("\n", " ").replace(",", "")
        data.append(row)

    filename = f"{slugify(fake.word())}-{uuid.uuid4()}.csv"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            quotechar=schema.string_character,
            delimiter=schema.column_separator,
        )
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return filepath
