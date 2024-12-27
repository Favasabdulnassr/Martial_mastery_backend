from rest_framework import serializers
from .models import Course
from user_auth.models import CustomUser

class CourseSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),many=True,required=False)

    class Meta:
        model = Course
        fields = ['id','name','description','tutor','created_at']


    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
     
        
        for field_name, field in self.fields.items():

            if field_name != 'tutor':
                field.required = True
        