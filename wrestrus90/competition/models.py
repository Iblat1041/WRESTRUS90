from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models.query import QuerySet
from core.enums import Limits
from django.db.models import(
   Model,
   IntegerChoices,
   CharField,
   SlugField,
   TextField,
   ImageField,
   DateTimeField,
   BooleanField,
   Manager,
   ForeignKey,
   PROTECT,
   SET_NULL
)

from django.urls import reverse


class PublishedManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_published=Competition.Status.PUBLISHED)


class Competition(Model):
    class Status(IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = CharField(
        max_length=Limits.MAX_LEN_COMPETITION_CHARFIELD.value,
        verbose_name='Заголовок'
        )
    slug = SlugField(
        max_length=Limits.MAX_LEN_COMPETITION_SLAGFIELD.value,
        unique=True,
        db_index=True,
        verbose_name='Slug'
        )
    photo = ImageField(
        upload_to="photos/%Y/%m/%d/", 
        default=None,
        blank=True, 
        null=True,
        verbose_name="Фото"
        )
    content = TextField(
        blank=True,
        verbose_name="Текст статьи"
        )
    time_create = DateTimeField(
        auto_now_add=True,
        verbose_name="Время создания"
        )
    time_update = DateTimeField(
        auto_now=True,
        verbose_name="Время изменения"
        )
    is_published = BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.DRAFT,
        verbose_name="Статус"
        )
    cat = ForeignKey(
        'CategoryCompetition', 
        on_delete=PROTECT,
        null=True
        )
    author = ForeignKey(get_user_model, on_delete=SET_NULL)

    objects = Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_competition', kwargs={'post_slug': self.slug})


class CategoryCompetition(Model):
    name = CharField(
        max_length=Limits.MAX_LEN_CAT_COMPETITION_SLAGFIELD.value,
        db_index=True
    )
    slug = SlugField(
        max_length=Limits.MAX_LEN_CAT_COMPETITION_SLAGFIELD.value,
        unique=True,
        db_index=True
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("category_competition", kwargs={"cat_slug": self.slug})
