# main/tasks.py

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

async def test_bunny_credentials():
    """
    Bunny Storage credentiallarini test qilish
    """
    if not BUNNY_API_KEY or BUNNY_API_KEY == 'your-actual-bunny-storage-api-key':
        print("❌ Bunny Storage API key not configured. Please set BUNNY_API_KEY in settings.py")
        return False

    try:
        # Test fayl nomi
        test_filename = f"test_{uuid.uuid4()}.txt"
        test_content = b"test file content"

        upload_url = f"{BUNNY_STORAGE_URL}{test_filename}"
        headers = {"AccessKey": BUNNY_API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.put(
                upload_url,
                data=test_content,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 201:
                    print(f"✅ Bunny Storage credentiallari to'g'ri!")
                    # Test faylni o'chirish
                    await delete_bunny_file(test_filename)
                    return True
                else:
                    response_text = await response.text()
                    print(f"❌ Credential test xatolik: HTTP {response.status} - {response_text}")
                    print(f"Upload URL: {upload_url}")
                    print(f"Storage Zone: {BUNNY_STORAGE_ZONE}")
                    print(f"API Key: {BUNNY_API_KEY[:10]}..." if BUNNY_API_KEY else "No API Key")
                    return False

    except Exception as e:
        print(f"❌ Credential test xatolik: {str(e)}")
        return False

async def delete_bunny_file(filename):
    """
    Bunny Storage dan faylni o'chirish
    """
    try:
        delete_url = f"{BUNNY_STORAGE_URL}{filename}"
        headers = {"AccessKey": BUNNY_API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.delete(delete_url, headers=headers) as response:
                if response.status in [200, 204]:
                    print(f"✅ Fayl o'chirildi: {filename}")
                else:
                    print(f"⚠️ Faylni o'chirishda xatolik: {response.status}")

    except Exception as e:
        print(f"⚠️ Faylni o'chirishda xatolik: {str(e)}")

async def upload_file_to_bunny(tmp_path, filename=None, folder=None):
    """
    Bunny Storage ga fayl yuklaydi va CDN link qaytaradi

    Args:
        tmp_path: Vaqtincha fayl joylashgan joy
        filename: Fayl nomi (agar berilmasa, asl nomi ishlatiladi)
        folder: CDN da joylashadigan papka nomi (masalan: "videos" yoki "React+ts videos")
    """
    if not BUNNY_API_KEY or BUNNY_API_KEY == 'your-actual-bunny-storage-api-key':
        raise Exception("Bunny Storage API key not configured. Please set BUNNY_API_KEY in settings.py")

    try:
        # Fayl nomini aniqlash
        if not filename:
            filename = Path(tmp_path).name  # Asl fayl nomini olish

        # Agar folder berilgan bo'lsa, yo'l qurish
        if folder:
            # Folder nomi to'g'rilash (bo'shliqlar va maxsus belgilarni kodlash)
            folder = folder.strip('/')
            full_filename = f"{folder}/{filename}"
        else:
            full_filename = filename

        upload_url = f"{BUNNY_STORAGE_URL}{full_filename}"

        # Bunny Storage uchun to'g'ri header
        headers = {
            "AccessKey": BUNNY_API_KEY,
        }

        async with aiohttp.ClientSession() as session:
            print(f"Fayl yuklanmoqda: {full_filename}")
            print(f"Upload URL: {upload_url}")

            file_size = os.path.getsize(tmp_path)
            print(f"Fayl hajmi: {file_size} bytes")

            with open(tmp_path, 'rb') as f:
                async with session.put(
                    upload_url,
                    data=f,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    response_text = await response.text()
                    print(f"Response status: {response.status}")
                    print(f"Response headers: {dict(response.headers)}")
                    print(f"Response body: {response_text}")

                    if response.status == 201:
                        # CDN link qaytarish
                        cdn_url = f"{BUNNY_PULL_ZONE_URL}{full_filename}"
                        print(f"✅ Fayl muvaffaqiyatli yuklandi: {cdn_url}")
                        return cdn_url
                    else:
                        error_msg = f"HTTP {response.status}: {response_text}"
                        raise Exception(f"Upload xatolik: {error_msg}")

    except Exception as e:
        print(f"Upload xatolik: {str(e)}")
        raise Exception(f"Fayl yuklanmadi: {str(e)}")

    finally:
        # Vaqtincha faylni o'chirish
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                print(f"Vaqtincha fayl o'chirildi: {tmp_path}")
        except Exception as cleanup_error:
            print(f"Vaqtincha faylni o'chirishda xatolik: {cleanup_error}")

# Sync versiya
def upload_to_bunny_storage(tmp_path, filename=None, folder=None):
    return asyncio.run(upload_file_to_bunny(tmp_path, filename, folder))

# Credential test funksiyasi
def test_credentials():
    return asyncio.run(test_bunny_credentials())
