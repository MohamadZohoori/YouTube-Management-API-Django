from django.db import models


class UserData(models.Model):
    channel_id = models.CharField(max_length=255)

    def __str__(self):
        return self.channel_id

class SubscribersList(models.Model):
    subscribedChannel = models.CharField(max_length=255)
    UserChannel = models.ForeignKey(UserData, on_delete=models.CASCADE)

    def __str__(self):
        return self.subscribedChannel

