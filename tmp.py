from notes.models import Reference


for ref in Reference.objects.all():
    ref.generate_embedding()
    ref.save(update_fields=['embedding'])
