from django.db import models
from server.models.ParameterSpec import ParameterSpec
import json

# A parameter value, which might be string or float
class ParameterVal(models.Model):
    class Meta:
        ordering = ['order']

    wf_module = models.ForeignKey('WfModule', related_name='parameter_vals',
                               on_delete=models.CASCADE, null=True)  # delete value if Module deleted
    parameter_spec = models.ForeignKey(ParameterSpec, related_name='parameter_vals',
                               on_delete=models.CASCADE, null=True)  # delete value if Spec deleted

    order = models.IntegerField('order', default=0)

    value = models.TextField(blank=True, default='')

    menu_items = models.TextField(null=True, blank=True)

    visible = models.BooleanField(default=True)

    def init_from_spec(self):
        self.set_value(self.parameter_spec.def_value)
        self.order = self.parameter_spec.order
        self.menu_items = self.parameter_spec.def_menu_items
        self.visible = self.parameter_spec.def_visible

    def duplicate(self, to_wf_module):
        if self.parameter_spec.type == ParameterSpec.SECRET:
            value = ''
        else:
            value = self.value

        newval = ParameterVal.objects.create(
            wf_module=to_wf_module,
            parameter_spec=self.parameter_spec,
            order=self.order,
            value=value,
            menu_items=self.menu_items,
            visible=self.visible
        )
        return newval


    # User can access param if they can access wf_module
    def request_authorized_read(self, request):
        return self.wf_module.request_authorized_read(request)

    def request_authorized_write(self, request):
        return self.wf_module.request_authorized_write(request)

    # Return selected menu item index. Insensitive to menu item text, either in config json or at runtime.
    def selected_menu_item_idx(self):
        if self.parameter_spec.type != ParameterSpec.MENU:
            raise ValueError('Request for current item of non-menu parameter ' + self.parameter_spec.name)
        return int(self.value)

    # Return text of currently selected menu item. Warning: will vary between locales etc.
    def selected_menu_item_string(self):
        if self.parameter_spec.type != ParameterSpec.MENU:
            raise ValueError('Request for current item of non-menu parameter ' + self.parameter_spec.name)

        items = self.menu_items
        if (items is not None):
            items = items.split('|')
            idx = int(self.value)
            if items != [''] and idx >=0 and idx < len(items):
                return items[idx]
            else:
                return ''  # return empty if bad idx, to allow for possible errors when menu items changed

    # This is where type checking / coercion happens.
    def set_value(self, new_value):
        ptype = self.parameter_spec.type

        if ptype == ParameterSpec.STRING:
            self.value = new_value

        elif ptype == ParameterSpec.INTEGER:
            try:
                self.value = int(float(new_value))
            except ValueError:
                self.value = '0'

        elif ptype == ParameterSpec.FLOAT:
            try:
                self.value = str(float(new_value))
            except ValueError:
                self.value = '0.0'

        elif ptype == ParameterSpec.CHECKBOX:
            try:
                # Be permissive, allow both actual booleans and "true"/"false" strings
                if type(new_value) is bool:
                    self.value = str(new_value)
                elif type(new_value) is str:
                    self.value = str(new_value.lower().strip() == 'true')
                else:
                    self.value = str(bool(new_value))  # we catch number types here
            except ValueError:
                self.value = 'False'

        elif ptype == ParameterSpec.MENU:
            try:
                self.value = str(int(new_value))
            except ValueError:
                self.value = '0'

        elif ptype == ParameterSpec.COLUMN or \
             ptype == ParameterSpec.MULTICOLUMN or \
             ptype == ParameterSpec.CUSTOM or \
             ptype == ParameterSpec.BUTTON or \
             ptype == ParameterSpec.STATICTEXT:
            self.value = new_value

        elif ptype == ParameterSpec.SECRET:
            if not new_value:
                self.value = ''
            else:
                if (type(new_value) is not dict
                        or type(new_value.get('name')) is not str
                        or not new_value.get('name')
                        or not new_value.get('secret')
                        ):
                    raise ValueError(f'SECRET parameter {self.parameter_spec.id_name} must be a dict with str "name": "..." and non-empty "secret"')
                self.value = json.dumps(new_value)

        else:
            raise ValueError('Unknown parameter type ' + ptype + ' for parameter ' + self.parameter_spec.name + ' in ParameterVal.set_value')

        self.save()

    # Coerce back to appropriate ptype
    def get_value(self):
        ptype = self.parameter_spec.type
        if ptype == ParameterSpec.STRING:
            return self.value
        elif ptype == ParameterSpec.INTEGER:
            return int(self.value) if self.value != '' else 0
        elif ptype == ParameterSpec.FLOAT:
            return float(self.value)
        elif ptype == ParameterSpec.CHECKBOX:
            return self.value == 'True'
        elif ptype == ParameterSpec.MENU:
            return int(self.value) if self.value != '' else 0
        elif ptype == ParameterSpec.COLUMN or \
             ptype == ParameterSpec.MULTICOLUMN or \
             ptype == ParameterSpec.CUSTOM or \
             ptype == ParameterSpec.BUTTON or \
             ptype == ParameterSpec.STATICTEXT:
            return self.value
        elif ptype == ParameterSpec.SECRET:
            if self.value:
                parsed = json.loads(self.value)
                return { 'name': parsed['name'] }
            else:
                return None
        else:
            raise ValueError('Unknown parameter ptype ' + ptype + ' for parameter ' + self.parameter_spec.name + ' in ParameterVal.get_value')


    def get_secret(self):
        ptype = self.parameter_spec.type
        if ptype == ParameterSpec.SECRET:
            if self.value:
                return json.loads(self.value)['secret']
            else:
                return None


    def __str__(self):
        return self.wf_module.__str__() + ' - ' + self.parameter_spec.name + ' - ' + str(self.get_value())
