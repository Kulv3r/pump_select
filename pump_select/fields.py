#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import partial

from werkzeug.datastructures import OrderedMultiDict
from wtforms import widgets, ValidationError, SelectMultipleField
from wtforms.compat import text_type
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField

BLANK_SELECTBOX_TEXT = '---'
BLANK_SELECTBOX_OPTION = [(None, '---')]

QueryRadioField = partial(
    QuerySelectField,
    widget=widgets.ListWidget(prefix_label=False),
    option_widget=widgets.RadioInput(),
)


class SelectMultipleCheckBoxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class GroupedSelectMultipleWidget(widgets.Select):
    """
        Renders a select field with groups. Expects a list of tuples when
        calling `field.iter_choices()`.

        There are two possible variations of tuples. The first type is a
        select, where both elements in the tuple are strings, the second one,
        consists of a string and a list of tuples of the first kind. It will
        render an optgroup with the string as label and a set of selects
        using the tuples in the list.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % widgets.html_params(name=field.name, **kwargs)]
        for value, label, selected in field.iter_choices():
            if hasattr(label, '__iter__'):
                html.append('<optgroup %s>' % widgets.html_params(label=value))
                for realvalue, reallabel, realselected in label:
                    html.append(self.render_option(realvalue, reallabel,
                                                   realselected))
                html.append('</optgroup>')
            else:
                html.append(self.render_option(value, label, selected))
        html.append('</select>')
        return widgets.HTMLString(''.join(html))


class GroupedQuerySelectMultipleField(QuerySelectMultipleField):
    """
        A QuerySelectMultipleField is a QuerySelectMultipleField with
        support for Grouping. This is probably the longest class name
        ever.

        This fields expects exactly the same arguments as
        QuerySelectMultipleField does, plus the keyworded `get_group`
        parameter. `get_group` has to return the group of an object, if
        there is one and `None` if the object should not be in a group.

        The function will perform the same validation as
        `QuerySelectField`, making sure that there are no inexistent
        selected values.

        It requires the `GroupedSelectMultipleWidget` for proper
        rendering.
    """

    widget = GroupedSelectMultipleWidget(multiple=True)

    def __init__(self, *args, **kwargs):
        # make sure that get_group is specified.
        self.get_group = kwargs.pop('get_group', None)
        if not self.get_group or not hasattr(self.get_group, '__call__'):
            raise ValueError('This field requires a function as value for the'
                             + 'get_group parameter.')
        # then run the usual initialization
        super(GroupedQuerySelectMultipleField, self).__init__(*args, **kwargs)

    def _get_object_list(self, ungrouped=False):
        """
            Returns a list of the objects. Retuns the ungrouped list, if
            `ungrouped=True` is passed.
        """
        # if this is run for the first time, let's get the data
        if self._object_list is None:
            # use the query or run one from the factory
            query = self.query or self.query_factory()
            # same helpers
            get_pk = self.get_pk
            get_group = self.get_group
            # now it get's complicated. We will use `ungrouped_object_list`
            # to be able to run a quick validation later on, whether the
            # selected objects exist.
            ungrouped_object_list = []
            # we will use the object_list for rendering the actual choices in
            # groups
            object_list = []
            # and we will use an intermediate dictionary to build the groups
            # I had to use an OrderedMultiDict, because a normal dict does
            # not preserve the order of the entries meaning that the order
            # the user passes on would not be preserved.
            # using an OrderedMultiDict enables the user to order stuff to his
            # liking and we will pass that on to the groups.
            groups = OrderedMultiDict()
            # now we run over all elements in the query
            for object in query:
                # and in any case every object is stored in the ungrouped list.
                ungrouped_object_list.append((text_type(get_pk(object)),
                                             object))
                # then we try to get the group of the object
                group = get_group(object)
                # if the object has no group it will just be appended to the
                # object_list
                if not group:
                    object_list.append((text_type(get_pk(object)), object))
                else:
                    # if it has a group we will attach it to the list of
                    # objects in the groups or create the group
                    if groups.get(group):
                        groups[group].append((text_type(get_pk(object)),
                                             object))
                    else:
                        groups[group] = [(text_type(get_pk(object)), object)]
            # now that we have all groups with all their elements, we add
            # the groups to the object_list
            for group, values in groups.items():
                object_list.append((group, values))
            # we store both lists for use later on.
            self._object_list = object_list
            self._ungrouped_object_list = ungrouped_object_list
        # and return the one that was asked for.
        if ungrouped:
            return self._ungrouped_object_list
        return self._object_list

    def _get_data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            # we go over our list of all objects
            for key, object in self._get_object_list(ungrouped=True):
                # if there is no formdata left, we are finished
                if not formdata:
                    break
                # if the object is selected, it's primary key is in `formdata`
                # and we will remove it from there and append the object to
                # data
                elif key in formdata:
                    formdata.remove(key)
                    data.append(object)
            # if any formdata is left now, there were objects selected that
            # did not exist
            if formdata:
                self._invalid_formdata = True
            # we save the data on the object
            self._set_data(data)
        # and return it
        return self._data

    # these two work are exactly the same way as on the parent, but
    # it does not work unless the property is updated to include the new
    # `_get_data`
    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self, choices=None):
        # for the choices we use the grouped object list, or if this a
        # recursive call, the passed on data.
        choices = choices if choices is not None else self._get_object_list()
        get_label = self.get_label
        # we loop over the current data
        for value, content in choices:
            # if the content of the tuple is a list, we recurse
            if isinstance(content, (list, tuple)):
                yield (value, self.iter_choices(content), None)
            # if not, we yield the actual data and the label
            else:
                yield(value, get_label(content), content in self.data)

    def pre_validate(self, form):
        # if there was data left when it was read, _invalid_formdata should
        # be `True` and we raise a ValidationError
        if self._invalid_formdata:
            raise ValidationError(self.gettext('Not a valid choice'))
        elif self.data:
            # if we have data, we loop over the objects in the ungrouped object
            # list to make sure that everything is correct, if we can't
            # find it, there is a problem and we raise a ValidationError
            obj_list = [x[1] for x in self._get_object_list(ungrouped=True)]
            for value in self.data:
                if value not in obj_list:
                    raise ValidationError(self.gettext('Not a valid choice.'))


def coerce_to_int_or_None(x):
    if x in (None, u'None'):
        return None
    return int(x)


def coerce_to_None(x):
    if x in (None, u'None'):
        return None
    return x


def coerce_bool_to_js(var):
    return str(var is True).lower()
