# Bunny Storage konfiguratsiyasi
from django.conf import settings
import os
import aiohttp
import asyncio
import uuid
from pathlib import Path

BUNNY_STORAGE_ZONE = getattr(settings, 'BUNNY_STORAGE_ZONE', 'anikimedia')
BUNNY_API_KEY = getattr(settings, 'BUNNY_API_KEY', '')
BUNNY_STORAGE_URL = f'https://storage.bunnycdn.com/{BUNNY_STORAGE_ZONE}/'
BUNNY_PULL_ZONE_URL = getattr(settings, 'BUNNY_PULL_ZONE_URL', 'https://aniki.b-cdn.net/')

async def upload_file_to_bunny(file_path, filename=None, folder=None):
    """
    Bunny Storage ga fayl yuklaydi va CDN link qaytaradi

    Args:
        file_path: Fayl joylashgan joy
        filename: Fayl nomi (agar berilmasa, asl nomi ishlatiladi)
        folder: CDN da joylashadigan papka nomi
    """
    if not BUNNY_API_KEY or BUNNY_API_KEY == 'your-actual-bunny-storage-api-key':
        raise Exception("Bunny Storage API key not configured. Please set BUNNY_API_KEY in settings.py")

    try:
        # Fayl nomini aniqlash
        if not filename:
            filename = Path(file_path).name

        # Agar folder berilgan bo'lsa, yo'l qurish
        if folder:
            folder = folder.strip('/')
            full_filename = f"{folder}/{filename}"
        else:
            full_filename = filename

        upload_url = f"{BUNNY_STORAGE_URL}{full_filename}"

        headers = {
            "AccessKey": BUNNY_API_KEY,
        }

        async with aiohttp.ClientSession() as session:
            print(f"Fayl yuklanmoqda: {full_filename}")

            with open(file_path, 'rb') as f:
                async with session.put(upload_url, data=f, headers=headers, timeout=300) as response:
                    if response.status not in [201, 200]:
                        error_text = await response.text()
                        raise Exception(f"Upload xatolik: {error_text}")

            # CDN link qaytarish
            cdn_url = f"{BUNNY_PULL_ZONE_URL}{full_filename}"
            print(f"✅ Fayl muvaffaqiyatli yuklandi: {cdn_url}")

            return cdn_url

    except Exception as e:
        print(f"Upload xatolik: {str(e)}")
        raise Exception(f"Fayl yuklanmadi: {str(e)}")

# Sync versiya
def upload_to_bunny_storage(file_path, filename=None, folder=None):
    return asyncio.run(upload_file_to_bunny(file_path, filename, folder))
