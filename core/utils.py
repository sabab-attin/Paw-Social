from django.http import QueryDict
from io import BytesIO

def handle_uploaded_file(f):
    destination = BytesIO()
    for chunk in f.chunks():
        destination.write(chunk)
    return destination.getvalue()

def get_query_dict():
    return QueryDict(mutable=True)