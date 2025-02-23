from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import requests
import base64
import time


users = {}


CLIENT_ID = "394a8fc67d3543ec9169a0612afac4e8"  
CLIENT_SECRET = "e89fe1ea474d459c9e60c9846f29923c"  

# Variables globales para token y tiempo de expiración
SPOTIFY_TOKEN = None
TOKEN_EXPIRATION = 0

# Obtener Token de Spotify
def get_spotify_token():
    global SPOTIFY_TOKEN, TOKEN_EXPIRATION

    if SPOTIFY_TOKEN and time.time() < TOKEN_EXPIRATION:
        return SPOTIFY_TOKEN

    creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    creds_b64 = base64.b64encode(creds.encode()).decode()
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {creds_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        SPOTIFY_TOKEN = token_data["access_token"]
        TOKEN_EXPIRATION = time.time() + token_data["expires_in"]
        return SPOTIFY_TOKEN
    else:
        return None  # Manejo de error

# Obtener información de un artista desde Spotify
def get_artist_info(request, artist_name):
    token = get_spotify_token()
    if not token:
        return JsonResponse({"error": "No se pudo obtener el token de Spotify"}, status=500)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.spotify.com/v1/search?q={artist_name}&type=artist", headers=headers)

    if response.status_code != 200:
        return JsonResponse({"error": "Error al obtener datos del artista"}, status=response.status_code)

    data = response.json()

    # Verificar si la lista de artistas está vacía
    if not data.get("artists", {}).get("items"):
        return JsonResponse({"error": "Artista no encontrado"}, status=404)

    return JsonResponse(data)

# Obtener información de una canción desde Spotify
def get_song_info(request, song_name):
    token = get_spotify_token()
    if not token:
        return JsonResponse({"error": "No se pudo obtener el token de Spotify"}, status=500)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.spotify.com/v1/search?q={song_name}&type=track", headers=headers)

    if response.status_code != 200:
        return JsonResponse({"error": "Error al obtener datos de la canción"}, status=response.status_code)

    return JsonResponse(response.json())

# Vista basada en clase para manejar usuarios
class UserView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('id')
            name = data.get('name')

            if user_id and name:
                users[user_id] = {"id": user_id, "name": name}
                return JsonResponse({"message": "User created successfully!"}, status=201)
            else:
                return JsonResponse({"error": "Invalid data. 'id' and 'name' are required."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    def get(self, request):
        try:
            return JsonResponse({"users": list(users.values())}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

# Vista basada en clase para manejar un usuario específico
class UserDetailView(View):
    @csrf_exempt
    def put(self, request, user_id):
        try:
            data = json.loads(request.body)
            if user_id in users:
                users[user_id]['name'] = data.get('name', users[user_id]['name'])
                return JsonResponse({"message": "User updated successfully!"}, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    @csrf_exempt
    def delete(self, request, user_id):
        try:
            if user_id in users:
                del users[user_id]
                return JsonResponse({"message": "User deleted successfully!"}, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

# Vista basada en clase para manejar preferencias de usuario
class UserPreferencesView(View):
    @csrf_exempt
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            if user_id in users:
                users[user_id]['preferences'] = data.get('genre')
                return JsonResponse({"message": "Preferences added successfully!"}, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    def get(self, request, user_id):
        try:
            if user_id in users:
                preferences = users[user_id].get('preferences')
                if preferences:
                    return JsonResponse({"preferences": preferences}, status=200)
                else:
                    return JsonResponse({"error": "Preferences not found"}, status=404)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
