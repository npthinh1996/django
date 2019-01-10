from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from .forms import NoteModelForm

def create_view(request):
    form = NoteModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect('/note/list')
    context = {
        'form': form
    }
    return render(request, 'notepad/create.html', context)

def list_view(request):
    note = Note.objects.all()
    context = {
        'object_list': note
    }
    return render(request, 'notepad/list.html', context)

def delete_view(request, pk):
    item_to_delete = Note.objects.filter(pk=pk)
    if item_to_delete.exists():
        if request.user == item_to_delete[0].user:
            item_to_delete[0].delete()
    return redirect('/note/list')

def update_view(request, pk):
    unique_note = get_object_or_404(Note, pk=pk)
    form = NoteModelForm(request.POST or None, request.FILES or None, instance=unique_note)
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect('/note/list')
    context = {
        'form': form
    }
    return render(request, 'notepad/create.html', context)
