from django.urls import path
from .views import get_artist_info, get_song_info, UserView, UserDetailView, UserPreferencesView

urlpatterns = [
    # Rutas para la API de Spotify
    path('spotify/artist/<str:artist_name>/', get_artist_info, name='get_artist_info'),
    path('spotify/song/<str:song_name>/', get_song_info, name='get_song_info'),

    # Rutas para los usuarios
    path('users/', UserView.as_view(), name='user_view'),  # Crear usuario y obtener todos los usuarios
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user_detail_view'),  # Actualizar y eliminar usuario
    path('users/<str:user_id>/preferences/', UserPreferencesView.as_view(), name='user_preferences_view'),  # Agregar y obtener preferencias
]

