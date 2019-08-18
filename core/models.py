import random

from aiomotorengine import Document, StringField, IntField, ListField, \
    BooleanField, DateTimeField, BinaryField, EmbeddedDocumentField
from bson import ObjectId


class ProgressEmbedded(Document):
    passed = ListField(StringField(), default=[])
    current = StringField(required=False)
    score = IntField(required=True, default=0)


class Player(Document):
    name = StringField(required=True, max_length=50)
    username = StringField(required=False, max_length=50)
    score = IntField(required=True, default=0)
    active = BooleanField(default=False)
    created = DateTimeField(auto_now_on_insert=True)
    upd = DateTimeField(auto_now_on_update=True)
    progress = EmbeddedDocumentField(ProgressEmbedded, required=False)
    chat = StringField(required=True)

    @classmethod
    async def get_player_by_chat(cls, chat_id):
        return await cls.objects.get(chat=str(chat_id))

    @classmethod
    async def create_player(cls, chat):
        player = cls(
            chat=str(chat['id']),
            name=chat['first_name'],
            username=chat['username']
        )
        player = await player.save()
        return player

    @classmethod
    async def show_leader_board(cls):
        best_players = await cls.objects.order_by(
            'score',
            direction=-1
        ).limit(5).find_all()
        results = [
            f"{num} место: {x.name} - {x.score} очков"
            for num, x in enumerate(best_players, start=1)
        ]
        return '\n'.join(results)

    def inc_score(self):
        self.progress.score += 1

    def get_passed_tracks_ids(self):
        if hasattr(self.progress, 'passed'):
            return [ObjectId(x) for x in self.progress.passed]

    async def deactivate(self):
        if self.score < self.progress.score:
            self.score = self.progress.score
        self.progress = None
        self.active = False
        await self.save()


class Music(Document):
    right = StringField(required=True)
    answers = ListField(StringField(), required=True)
    file = StringField(required=False)

    @classmethod
    async def get_random_track(cls, exclude=None):
        music = (
            await Music.objects.filter({'_id': {'$nin': exclude}}).find_all()
            if exclude
            else await Music.objects.find_all()
        )
        return random.choice(music) if music else None


class Storage(Document):
    right = StringField()
    binary = BinaryField()
    answers = ListField(StringField())
