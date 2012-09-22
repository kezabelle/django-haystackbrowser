from django import forms
from haystack.forms import ModelSearchForm

class PreSelectedModelSearchForm(ModelSearchForm):
    #def __init__(self, *args, **kwargs):
    #    super(PreSelectedModelSearchForm, self).__init__(*args, **kwargs)
    #    self.fields['models'].initial = (choice[0] for choice in self.fields['models'].choices)

    def no_query_found(self):
        return self.searchqueryset.all()

    #def search(self):
    #    return super(PreSelectedModelSearchForm, self).search()
