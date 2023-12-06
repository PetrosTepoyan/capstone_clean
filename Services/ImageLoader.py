import aiohttp
import asyncio
import logging
from ConcreteStorages import ImageStorage

class ImageLoader:
    def __init__(self, storage: ImageStorage):
        self.storage = storage
            
    async def download_image(self, session, url, source, apartment_id, index):
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return

                extension = url.split(".")[-1]
                image_path = f"{source}/{apartment_id}/{index}.{extension}"
                bytes = await response.read()
                self.storage.save_image(bytes, image_path)
        except Exception as e:
            self.storage.image_error_log(
                source = source, 
                url = url,
                apartment_id = apartment_id,
                index = index,
                error = e
            )
            logging.error(f"Can't download image {apartment_id} {index}")
            

    async def __download_images(self, links, source, apartment_id):
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_image(session, url, source, apartment_id, ind) for ind, url in enumerate(links)]
            await asyncio.gather(*tasks)

    def download_images(self, links, source, apartment_id):
        try:
            if asyncio.get_running_loop():
                asyncio.create_task(self.__download_images(links, source, apartment_id))
            else:
                asyncio.run(self.__download_images(links, source, apartment_id))
        except:
            # Meaning running in a sync context, need to force running in an event loop
            asyncio.run(self.__download_images(links, source, apartment_id))