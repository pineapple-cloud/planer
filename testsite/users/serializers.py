from rest_framework import serializers
from .models import Tasks
from .forms import UserCreationForm


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'day_to_do', 'time_update', 'done', 'tag', 'urgent', 'important']
        read_only_fields = ['username']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['username'] = user.email
        return super().create(validated_data)
class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'day_to_do', 'content', 'time_update', 'done', 'tag', 'urgent', 'important']