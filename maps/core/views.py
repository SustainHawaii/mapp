from rest_framework.response import Response
from mappweb.templatetags.mapp_tags import check_permission

class LinkBuilder(object):

    def __init__(self, user, base_url, perm_type,del_func="set_id"):
        self.user = user
        self.base_url = base_url
        self.perm_type = perm_type
        self.del_func = del_func


    def edit_link(self, obj):
        if self.user.can_edit(obj, self.perm_type):
            return "<a href='%s%s'>Edit</a> |" % (self.base_url, obj.id)

        return ""

    def view_link(self, obj):
        if self.user.can_edit(obj, self.perm_type):
            return "<a href='%s%s'>%s</a>" % (self.base_url, obj.id,obj.name)

        return ""

    def del_link(self, obj):
        if self.user.can_delete(obj, self.perm_type):
            return "<a data-toggle='modal' href='#delete-single' class='delete' onclick=\"%s('%s');\">Delete</a>" % (self.del_func,obj.id)

        return ""


    
    
    


