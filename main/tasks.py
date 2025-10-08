# main/tasks.py
import os
import aiohttp
import aiofiles
import asyncio
from django.conf import settings

BUNNY_API_KEY = getattr(settings, 'BUNNY_STREAM_API_KEY', "3cabea06-3957-4759-80bae3dd0901-79aa-4913")
BUNNY_LIBRARY_ID = getattr(settings, 'BUNNY_STREAM_LIBRARY_ID', "506729")
BUNNY_BASE_URL = "https://video.bunnycdn.com/library"

async def create_video(session, title):
    url = f"{BUNNY_BASE_URL}/{BUNNY_LIBRARY_ID}/videos"
    headers = {
        "Content-Type": "application/json",
        "AccessKey": BUNNY_API_KEY,
    }
    data = {"title": title}
    async with session.post(url, json=data, headers=headers, timeout=30) as res:
        res_data = await res.json()
        if res.status != 200 or "guid" not in res_data:
            raise Exception(f"Video yaratishda xatolik: {res_data}")
        return res_data["guid"]

async def upload_file(session, tmp_path, video_id, chunk_size=10*1024*1024):
    upload_url = f"{BUNNY_BASE_URL}/{BUNNY_LIBRARY_ID}/videos/{video_id}"
    headers = {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/octet-stream",
    }

    file_size = os.path.getsize(tmp_path)
    uploaded = 0

    async with aiofiles.open(tmp_path, 'rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            async with session.put(upload_url, data=chunk, headers=headers, timeout=300) as res:
                if res.status not in [200, 201]:
                    raise Exception(f"Upload xatolik: {await res.text()}")
            uploaded += len(chunk)
            print(f"Progress: {uploaded/file_size:.2%}")

async def upload_video_task(tmp_path, title):
    """
    BunnyCDN ga video upload qiladi va iframe link qaytaradi
    """
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Video yaratilyapti: {title}")
            video_id = await create_video(session, title)
            print(f"Video ID: {video_id}")

            await upload_file(session, tmp_path, video_id)
            print("✅ Video muvaffaqiyatli yuklandi!")

            iframe_link = f"https://iframe.mediadelivery.net/play/{BUNNY_LIBRARY_ID}/{video_id}"
            print(f"Video iframe link: {iframe_link}")

            return iframe_link

    except Exception as e:
        print(f"Upload xatolik: {str(e)}")
        raise Exception(f"Video yuklanmadi: {str(e)}")

    finally:
        # Vaqtincha faylni o'chirish
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                print(f"Vaqtincha fayl o'chirildi: {tmp_path}")
        except Exception as cleanup_error:
            print(f"Vaqtincha faylni o'chirishda xatolik: {cleanup_error}")

# Agar sync tarzda chaqirmoqchi bo'lsangiz
def upload_video(tmp_path, title):
    return asyncio.run(upload_video_task(tmp_path, title))
