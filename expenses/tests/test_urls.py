from django.urls import reverse, resolve
class TestUrls:
    def test_expenselist_url(self):
        path = reverse('expenses:expense_list', kwargs={})
        assert resolve(path).view_name == 'expenses:expense_list'
    def test_addexpense_url(self):
        path = reverse('expenses:add_expense', kwargs={})
        assert resolve(path).view_name == 'expenses:add_expense'
    def test_updateexpense_url(self):
        path = reverse('expenses:update_expense', kwargs={'expense_id': 1})
        assert resolve(path).view_name == 'expenses:update_expense'
        
