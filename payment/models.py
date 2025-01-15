

import stripe
from django.db import models
from django.conf import settings
from user_auth.models import CustomUser
from Courses.models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY  # Add your Stripe secret key to settings.py

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)  # Made nullable
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, default='pending')  # pending, successful, failed
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} paid for {self.course.title}"

    def mark_payment_successful(self):
        self.payment_status = 'successful'
        self.save()

    def mark_payment_failed(self):
        self.payment_status = 'failed'
        self.save()

    def get_payment_url(self):
        """Get a Stripe payment link."""
        try:
            # Add proper error handling and logging
            if not self.course:
                raise ValueError("No course associated with this payment")
            
            if not self.amount_paid:
                raise ValueError("No amount specified for payment")
            
            # Create Stripe checkout session with better error handling
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{self.course.title} by {self.course.tutor.first_name} {self.course.tutor.last_name}",
                            'description': self.course.description[:255],  # Stripe has a limit on description length
                        },
                        'unit_amount': int(float(self.amount_paid) * 100),  # Ensure proper conversion to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.SITE_URL}/courses?success=true",
                cancel_url=f"{settings.SITE_URL}/courses?cancelled=false",
                metadata={
                    'payment_id': str(self.id),
                    'course_id': str(self.course.id),
                    'user_id': str(self.user.id)
                },
                customer_email=self.user.email  # Pre-fill customer email
            )
            
            # Store the session ID
            self.stripe_session_id = checkout_session.id
            self.save()
            
            return checkout_session.url
            
        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            print(f"Stripe error: {str(e)}")
            return f"Stripe error: {str(e)}"
        except Exception as e:
            # Handle other errors
            print(f"Error creating payment URL: {str(e)}")
            return f"Error: {str(e)}"




from cloudinary.models import CloudinaryField


class PurchasedCourse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tutor =models.ForeignKey( CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name='Purchase_course')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_title = models.CharField(max_length=200)  # Store course title
    course_description = models.TextField()  # Store course description
    course_fees = models.DecimalField(max_digits=10, decimal_places=2)  # Store course fees
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Marks whether the course is active

    def __str__(self):
        return f"{self.user.email} purchased {self.course_title}"

    def create_purchased_lessons(self):
        """Creates lessons for the purchased course."""
        for lesson in self.course.tutorials.all():
            PurchasedCourseLesson.objects.create(
                purchased_course=self,
                title=lesson.title,
                description=lesson.description,
                cloudinary_url=lesson.cloudinary_url,
                thumbnail=lesson.thumbnail,
                order=lesson.order
            )



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
        return f"{self.title} - {self.purchased_course.course_title}"
