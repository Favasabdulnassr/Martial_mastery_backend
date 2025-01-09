from rest_framework import serializers
from .models import Course
from user_auth.models import CustomUser
from Tutorials.serializers import TutorialSerializer



class CourseSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),many=True,required=False)
    tutorials = TutorialSerializer(many=True,read_only=True)

    class Meta:
        model = Course
        fields = ['id','name','description','tutor','created_at','tutorials']


    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
     
        
        for field_name, field in self.fields.items():

            if field_name != 'tutor':
                field.required = True
        