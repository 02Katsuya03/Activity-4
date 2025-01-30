from django.contrib import admin
from .models import School, LostItem, Profile, FoundItem, ClaimProcedure, F2FClaim, OnlineClaim, OnlineClaimProcedure
from django import forms

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'phone_number', 'role', 'school')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(School)

class LostItemAdmin(admin.ModelAdmin):
    list_display = ('item_id','item_name', 'category', 'date_lost', 
                  'location_lost', 'lost_by','contact_information', 'school')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'date_lost':
            kwargs['widget'] = forms.DateInput(format='%d/%m/%Y')
        return super().formfield_for_dbfield(db_field, **kwargs)
    
admin.site.register(LostItem, LostItemAdmin)

class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('item_id','item_name', 'category', 'date_found', 
                  'location_found', 'found_by','contact_information', 'school')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'date_lost':
            kwargs['widget'] = forms.DateInput(format='%d/%m/%Y')
        return super().formfield_for_dbfield(db_field, **kwargs)

admin.site.register(FoundItem, FoundItemAdmin)

@admin.register(ClaimProcedure)
class ClaimProcedureAdmin(admin.ModelAdmin):
    list_display = ('get_found_item_name', 'claimed_by', 'school', 'status', 'claimed_at')
    search_fields = ('claimed_by', 'found_item__item_name', 'status')
    list_filter = ('status', 'school')
    readonly_fields = ('claimed_at',)
    ordering = ('-claimed_at',)

    def get_found_item_name(self, obj):
        return obj.found_item.item_name  
    get_found_item_name.short_description = 'Found Item'

@admin.register(OnlineClaimProcedure)
class OnlineClaimProcedureAdmin(admin.ModelAdmin):
    list_display = ('get_found_item_name', 'claimed_by', 'school', 'status', 'claimed_at')
    search_fields = ('claimed_by', 'found_item__item_name', 'status')
    list_filter = ('status', 'school')
    readonly_fields = ('claimed_at',)
    ordering = ('-claimed_at',)

    def get_found_item_name(self, obj):
        return obj.found_item.item_name 
    get_found_item_name.short_description = 'Found Item'

@admin.register(F2FClaim)
class F2FClaimAdmin(admin.ModelAdmin):
    list_display = ('get_found_item_name', 'claimed_by', 'claimed_at', 'status', 'get_school')  

    search_fields = ('claimed_by', 'found_item__item_name', 'status')

    list_filter = ('status',)

    readonly_fields = ('claimed_at',)

    ordering = ('-claimed_at',)

    def get_found_item_name(self, obj):
        return obj.found_item.item_name 
    get_found_item_name.short_description = 'Found Item'

    def get_school(self, obj):
        return obj.school 
    get_school.short_description = 'School'

@admin.register(OnlineClaim)
class OnlineClaimAdmin(admin.ModelAdmin):
    list_display = ('get_found_item_name', 'claimed_by', 'claimed_at', 'status', 'get_school')  # Added school

    search_fields = ('claimed_by', 'found_item__item_name', 'status')

    list_filter = ('status',)

    readonly_fields = ('claimed_at',)

    ordering = ('-claimed_at',)

    def get_found_item_name(self, obj):
        return obj.found_item.item_name 
    get_found_item_name.short_description = 'Found Item'

    def get_school(self, obj):
        return obj.school  
    get_school.short_description = 'School'

