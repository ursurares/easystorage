from django.core.exceptions import ValidationError

def validate_file_size(source):
    filesize=source.size
    if filesize>1073741824:
        raise ValidationError("The maximum file size that can be uploaded is 1GB")
    else:
        return source