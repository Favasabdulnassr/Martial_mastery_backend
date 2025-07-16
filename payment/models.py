

import stripe
from django.db import models
from django.conf import settings
from user_auth.models import CustomUser
from Courses.models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY  # Add your Stripe secret key to settings.py

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)  # Made nullable
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, default='pending')  # pending, successful, failed
    payment_date = models.DateTimeField(auto_now_add=True)
    last_error = models.TextField(null=True, blank=True)



    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_status']),
            models.Index(fields=['stripe_session_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]

        

    def update_status(self, status, error=None):
        """Update payment status and handle associated actions"""
        self.payment_status = status
        if error:
            self.last_error = error
        self.save()

       
    
    def create_stripe_session(self):
        """Create Stripe checkout session"""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': self.course.title,
                            'description': self.course.description[:255],
                            'metadata': {
                                'course_id': str(self.course.id)
                            }
                        },
                        'unit_amount': int(float(self.amount_paid) * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.SITE_URL}/payment?success=true",
                cancel_url=f"{settings.SITE_URL}/payment?cancelled=false",
                metadata={
                    'payment_id': str(self.id),
                    'course_id': str(self.course.id),
                    'user_id': str(self.user.id)
                },
                customer_email=self.user.email
            )
            
            self.stripe_session_id = checkout_session.id
            self.update_status('processing')
            return checkout_session.url
            
        except stripe.error.StripeError as e:
            self.update_status('failed', str(e))
            raise
        except Exception as e:
            self.update_status('failed', str(e))
            raise




from cloudinary.models import CloudinaryField


class PurchasedCourse(models.Model):
    tutor =models.ForeignKey( CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name='Purchase_course')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_title = models.CharField(max_length=200)  # Store course title
    course_description = models.TextField()  # Store course description
    course_fees = models.DecimalField(max_digits=10, decimal_places=2)  # Store course fees
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Marks whether the course is active

    def __str__(self):
        return f"{self.course_title} by {self.id}"

 


class PurchasedCourseUser(models.Model):
    purchased_course = models.ForeignKey(PurchasedCourse, on_delete=models.CASCADE, related_name='purchased_users')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchased_course_users')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('purchased_course', 'user')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.email} - {self.purchased_course.course_title} by {self.purchased_course.id}"

class PurchasedCourseLesson(models.Model):
    purchased_course = models.ForeignKey(PurchasedCourse, on_delete=models.CASCADE, related_name='purchased_lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    cloudinary_url = CloudinaryField('video', resource_type='video')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    order = models.PositiveIntegerField()  # Keep the order of lessons the same
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)                                                                    

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.purchased_course.course_title} {self.id}"
    







