import aiohttp
import asyncio
import aiofiles
import os

BUNNY_API_KEY = "3cabea06-3957-4759-80bae3dd0901-79aa-4913"
BUNNY_LIBRARY_ID = "506729"
BUNNY_BASE_URL = "https://video.bunnycdn.com/library"

async def create_video(session, title):
    url = f"{BUNNY_BASE_URL}/{BUNNY_LIBRARY_ID}/videos"
    headers = {
        "Content-Type": "application/json",
        "AccessKey": BUNNY_API_KEY,
    }
    data = {"title": title}
    async with session.post(url, json=data, headers=headers) as res:
        res_data = await res.json()
        if res.status != 200 or "guid" not in res_data:
            raise Exception(f"Video yaratishda xatolik: {res_data}")
        return res_data["guid"]

async def upload_video(session, file_path, video_id, chunk_size=10*1024*1024):
    upload_url = f"{BUNNY_BASE_URL}/{BUNNY_LIBRARY_ID}/videos/{video_id}"
    headers = {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/octet-stream",
    }

    file_size = os.path.getsize(file_path)
    uploaded = 0

    async with aiofiles.open(file_path, 'rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            async with session.put(upload_url, data=chunk, headers=headers) as res:
                if res.status not in [200, 201]:
                    raise Exception(f"Video yuklashda xatolik: {await res.text()}")
            uploaded += len(chunk)
            print(f"Progress: {uploaded/file_size:.2%}")

async def main():
    async with aiohttp.ClientSession() as session:
        video_id = await create_video(session, "Test Video")
        await upload_video(session, "my_video.mp4", video_id)

        # iframe link
        iframe_link = f"https://iframe.mediadelivery.net/play/{BUNNY_LIBRARY_ID}/{video_id}"
        print(f"Video iframe link: {iframe_link}")

if __name__ == "__main__":
    asyncio.run(main())
