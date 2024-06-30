from rest_framework import serializers
import webcolors
from .models import Cat, Owner, Achievement, AchievementCat, CHOICES
import datetime as dt

class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Owner

        fields = ('first_name', 'last_name', 'cats')

class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name') # переопределение имени

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


# class Hex2NameColor(serializers.Field):
#     def to_representation(self, value):
#         return value
    
#     def to_internal_value(self, data):
        
#         try:
#             data = webcolors.hex_to_name(data)

#         except ValueError:
#             raise serializers.ValidationError("Для этого цвета нет имени")
        
#         return data

class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField() # своё поле
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements', 'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year
    

    def create(self, validated_data):
        if 'achievements' not in validated_data:
            cat = Cat.objects.create(**validated_data)
            return cat

        # Уберём список достижений из словаря validated_data и сохраним его
        achievements = validated_data.pop('achievements')

        # Создадим нового котика пока без достижений, данных нам достаточно
        cat = Cat.objects.create(**validated_data)

        # Для каждого достижения из списка достижений
        for achievement in achievements:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)
        return cat
    
