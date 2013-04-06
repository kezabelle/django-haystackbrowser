from haystack.forms import ModelSearchForm, FacetedModelSearchForm


class PreSelectedModelSearchForm(FacetedModelSearchForm):
    """ Minor modification to the standard ModelSearchForm. Only changes ``no_query_found``."""
    def no_query_found(self):
        """When nothing is entered, show everything, because it's a better
        useful default for our usage.
        """
        return self.searchqueryset.all()
