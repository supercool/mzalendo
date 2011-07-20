from django.contrib import admin
from mzalendo.core import models
from django.contrib.gis import db
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.generic import GenericTabularInline
from django import forms

def create_admin_link_for(obj, link_text):
    url = reverse(
        'admin:%s_%s_change' % ( obj._meta.app_label, obj._meta.module_name),
        args=[obj.id]
    )
    return u'<a href="%s">%s</a>' % ( url, link_text )


class ContactKindAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [ 'name' ]


class InformationSourceAdmin(admin.ModelAdmin):
    list_display  = [ 'source', 'show_foreign', 'entered', ]
    list_filter   = [ 'entered', ]
    search_fields = [ 'source', ]

    def show_foreign(self, obj):
        return create_admin_link_for( obj.content_object, str(obj.content_object) )
    show_foreign.allow_tags = True


class InformationSourceInlineAdmin(GenericTabularInline):
    model      = models.InformationSource
    extra      = 0
    can_delete = False
    fields     = [ 'source', 'note', 'entered', ]
    formfield_overrides = {
        db.models.TextField: {'widget': forms.Textarea(attrs={'rows':2, 'cols':40})},
    }


class ContactAdmin(admin.ModelAdmin):
    list_display  = [ 'kind', 'value', 'show_foreign' ]
    search_fields = ['value', ]
    inlines       = [ InformationSourceInlineAdmin, ]
    
    def show_foreign(self, obj):
        return create_admin_link_for( obj.content_object, str(obj.content_object) )
    show_foreign.allow_tags = True
    

class ContactInlineAdmin(GenericTabularInline):
    model      = models.Contact
    extra      = 0
    can_delete = False
    fields     = [ 'kind', 'value', 'source', 'note', ]
    formfield_overrides = {
        db.models.TextField: {'widget': forms.Textarea(attrs={'rows':2, 'cols':20})},
    }


class PositionAdmin(admin.ModelAdmin):
    list_display  = [ 'id', 'show_person', 'show_organisation', 'show_place', 'title', 'start_date', 'end_date' ]
    search_fields = ['person__first_name', 'person__last_name', 'organisation__name' ]
    list_filter   = [ 'title__name' ]    
    inlines       = [ InformationSourceInlineAdmin, ]
    
    def show_person(self, obj):
        return create_admin_link_for( obj.person, obj.person.name() )
    show_person.allow_tags = True
    
    def show_organisation(self, obj):
        return create_admin_link_for(obj.organisation, obj.organisation.name)
    show_organisation.allow_tags = True

    def show_place(self, obj):
        return create_admin_link_for(obj.place, obj.place.name)
    show_place.allow_tags = True


class PositionInlineAdmin(admin.TabularInline):
    model      = models.Position
    extra      = 0
    can_delete = False
    fields     = [ 'person', 'organisation', 'place', 'title', 'start_date', 'end_date' ]


class PersonAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("first_name","last_name")}
    inlines       = [ PositionInlineAdmin, ContactInlineAdmin, InformationSourceInlineAdmin, ]
    list_display  = [ 'slug', 'name', 'date_of_birth' ]
    search_fields = ['first_name', 'last_name']

class PlaceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display  = [ 'slug', 'name', 'kind', 'show_organisation' ]
    list_filter   = [ 'kind' ]
    search_fields = [ 'name', 'organisation__name' ]
    inlines       = [ InformationSourceInlineAdmin, ]

    def show_organisation(self, obj):
        if obj.organisation:
            return create_admin_link_for(obj.organisation, obj.organisation.name)
        else:
            return '-'
    show_organisation.allow_tags = True


class PlaceInlineAdmin(admin.TabularInline):
    model      = models.Place
    extra      = 0
    can_delete = False
    fields     = [ 'name', 'slug', 'kind' ]


class OrganisationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines       = [ PlaceInlineAdmin, PositionInlineAdmin, ContactInlineAdmin, InformationSourceInlineAdmin, ]
    list_display  = [ 'slug', 'name', 'kind', ]
    list_filter   = [ 'kind', ]
    search_fields = [ 'name' ]

class OrganisationKindAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [ 'name' ]

class PlaceKindAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [ 'name' ]

class PositionTitleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [ 'name' ]


# Add these to the admin
admin.site.register( models.Contact,              ContactAdmin               )
admin.site.register( models.ContactKind,          ContactKindAdmin           )
admin.site.register( models.InformationSource,    InformationSourceAdmin     )
admin.site.register( models.Organisation,         OrganisationAdmin          )
admin.site.register( models.OrganisationKind,     OrganisationKindAdmin      )
admin.site.register( models.Person,               PersonAdmin                )
admin.site.register( models.Place,                PlaceAdmin                 )
admin.site.register( models.PlaceKind,            PlaceKindAdmin             )
admin.site.register( models.Position,             PositionAdmin              )
admin.site.register( models.PositionTitle,        PositionTitleAdmin         )
