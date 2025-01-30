from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
import random

class School(models.Model):
    # Choices for school levels
    SCHOOL_LEVELS = [
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('Senior High', 'Senior High'),
        ('College', 'College'),
    ]

    # Choices for school type
    SCHOOL_TYPES = [
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]

    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Type of school with choices
    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPES, default='Public')
    
    # School level (Elementary, High School, etc.)
    school_level = models.CharField(max_length=20, choices=SCHOOL_LEVELS, default='High School')

    # Images
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)  # School logo
    school_picture = models.ImageField(upload_to='school_pictures/', blank=True, null=True)  # School image

    def save(self, *args, **kwargs):
        self.name = self.name.upper()  # Ensure name is always in uppercase
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.school_level} - {self.school_type})"

class Profile(models.Model):
    SEX = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),   
    ]

    ROLES = [
        ('User', 'User'),
        ('ADMIN', 'Admin')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30, blank=True)  
    sex = models.CharField(max_length=10, choices=SEX)         
    phone_number = models.CharField(max_length=15)              
    role = models.CharField(max_length=10, choices=ROLES, default='User')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user)


class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('documents', 'Documents'),
        ('keys', 'Keys'),
        ('books_stationary', 'Books & Stationary'),
        ('bags_luggage', 'Bags & Luggage'),
        ('sporting_goods', 'Sporting Goods'),
        ('toys_games', 'Toys & Games'),
        ('money', 'Money')
    ]

    item_id = models.CharField(max_length=10, unique=True, blank=True, default='') 
    item_name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, default='Lost')
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date_lost = models.DateField()
    date_added = models.DateTimeField(default=now)
    location_lost = models.CharField(max_length=100)
    contact_information = models.CharField(max_length=100)
    lost_by = models.CharField(max_length=100, blank=True, null=True)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.item_name} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.item_id:
            self.item_id = self._generate_unique_item_id()
        super().save(*args, **kwargs)

    def _generate_unique_item_id(self):
        while True:
            random_id = f"LT-{random.randint(10000000, 99999999)}"
            if not LostItem.objects.filter(item_id=random_id).exists():
                return random_id
            
class FoundItem(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('documents', 'Documents'),
        ('keys', 'Keys'),
        ('books_stationary', 'Books & Stationary'),
        ('bags_luggage', 'Bags & Luggage'),
        ('sporting_goods', 'Sporting Goods'),
        ('toys_games', 'Toys & Games'),
        ('money', 'Money')
    ]

    item_id = models.CharField(max_length=10, unique=True, blank=True, default='')  
    item_name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, default='Found')
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date_found = models.DateField()
    date_added = models.DateTimeField(default=now)
    location_found = models.CharField(max_length=100)
    contact_information = models.CharField(max_length=100)
    found_by = models.CharField(max_length=100, blank=True, null=True)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='found_items/', blank=True, null=True)
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.item_name} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.item_id:
            self.item_id = self._generate_unique_item_id()
        super().save(*args, **kwargs)

    def _generate_unique_item_id(self):
        while True:
            random_id = f"FT-{random.randint(10000000, 99999999)}"
            if not FoundItem.objects.filter(item_id=random_id).exists():
                return random_id

class ClaimProcedure(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REQUIRED_DOCUMENT_CHOICES = [
        ('id_card', 'ID Card'),
        ('birth_certificate', 'Birth Certificate'),
        ('proof_of_address', 'Proof of Address')
    ]
    
    CLAIM_TYPE_CHOICES = [
        ('Face-to-Face', 'Face-to-Face'),
        ('Online', 'Online')
    ]

    found_item = models.OneToOneField(FoundItem, on_delete=models.CASCADE, null=True)
    claimed_by = models.CharField(max_length=255, help_text="Name of the person claiming")
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    claimed_at = models.DateTimeField(default=now)  
    appointment_date = models.DateField(null=True, blank=True)
    required_documents = models.CharField(max_length=20, choices=REQUIRED_DOCUMENT_CHOICES)
    document_image = models.ImageField(upload_to='document_uploads/', blank=True, null=True)
    other_document = models.CharField(max_length=100, blank=True, null=True, help_text="If 'Other' is selected, specify the document.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_number = models.CharField(max_length=15, blank=True, null=True, help_text="Your contact number")
    reason_for_claim = models.TextField(blank=True, null=True, help_text="Reason for claiming the item")
    remarks = models.TextField(blank=True, null=True, help_text="Additional remarks")
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE_CHOICES, help_text="Claim type (e.g. Face-to-Face)")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
     
        if not self.found_item:
            raise ValueError("FoundItem must be provided for the claim procedure.")
        
       
        if not FoundItem.objects.filter(id=self.found_item.id).exists():
            raise ValueError("The provided FoundItem does not exist in the database.")

       
        if self.school and not School.objects.filter(id=self.school.id).exists():
            raise ValueError("The provided School does not exist in the database.")

        super().save(*args, **kwargs) 

     
        if self.status == 'in_progress':
            f2f_claim, created = F2FClaim.objects.get_or_create(
                found_item=self.found_item,
                claimed_by=self.claimed_by,
                defaults={
                    'claimed_at': self.claimed_at,
                    'status': self.status,
                    'school': self.school,
                    'claim_procedure': self, 
                }
            )
            if not created:
                f2f_claim.status = self.status
                f2f_claim.save()

class OnlineClaimProcedure(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REQUIRED_DOCUMENT_CHOICES = [
        ('id_card', 'ID Card'),
        ('birth_certificate', 'Birth Certificate'),
        ('proof_of_address', 'Proof of Address')
    ]
    
    CLAIM_TYPE_CHOICES = [
        ('Face-to-Face', 'Face-to-Face'),
        ('Online', 'Online')
    ]

    found_item = models.OneToOneField(FoundItem, on_delete=models.CASCADE)
    claimed_by = models.CharField(max_length=255, help_text="Name of the person claiming")
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    claimed_at = models.DateTimeField(default=now) 
    appointment_date = models.DateField(null=True, blank=True)
    required_documents = models.CharField(max_length=20, choices=REQUIRED_DOCUMENT_CHOICES)
    document_image = models.ImageField(upload_to='document_uploads/', blank=True, null=True)
    other_document = models.CharField(max_length=100, blank=True, null=True, help_text="If 'Other' is selected, specify the document.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_number = models.CharField(max_length=15, blank=True, null=True, help_text="Your contact number")
    reason_for_claim = models.TextField(blank=True, null=True, help_text="Reason for claiming the item")
    remarks = models.TextField(blank=True, null=True, help_text="Additional remarks")
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE_CHOICES, help_text="Claim type (e.g. Face-to-Face)")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Claim for {self.found_item} by {self.claimed_by}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 

       
        if self.status == 'in_progress':
            online_claim, created = OnlineClaim.objects.get_or_create(
                found_item=self.found_item,
                claimed_by=self.claimed_by,
                defaults={
                    'claimed_at': self.claimed_at,
                    'status': self.status,
                    'school': self.school,
                    'claim_procedure': self, 
                }
            )
            if not created:
                online_claim.status = self.status
                online_claim.save()


class OnlineClaim(models.Model):
    claim_procedure = models.OneToOneField(OnlineClaimProcedure, on_delete=models.CASCADE, null=True)
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    claimed_by = models.CharField(max_length=255)
    claimed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default='Pending')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    claim_type = models.CharField(max_length=20, choices=OnlineClaimProcedure.CLAIM_TYPE_CHOICES, default='Online')

    def __str__(self):
        return f"Claimed by {self.claimed_by} for {self.found_item.item_name}"

    def save(self, *args, **kwargs):
        self.status = self.status.capitalize() 
        super().save(*args, **kwargs)

class F2FClaim(models.Model):
    claim_procedure = models.OneToOneField(ClaimProcedure, on_delete=models.CASCADE, null=True)
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    claimed_by = models.CharField(max_length=255)
    claimed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 
    status = models.CharField(max_length=255, default='Pending')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    claim_type = models.CharField(max_length=20, choices=ClaimProcedure.CLAIM_TYPE_CHOICES, default='Online')

    def __str__(self):
        return f"Claimed by {self.claimed_by} for {self.found_item.item_name}"

    def save(self, *args, **kwargs):
        self.status = self.status.capitalize() 
        super().save(*args, **kwargs)


