import base64
import collections
import heapq
import io
import json
import logging
import os

from dotenv import load_dotenv

from videoindexerclient.model import Video
from videoindexerclient.repository import VideoIndexerRepositoryService
from .Consts import Consts
from .VideoIndexerClient import VideoIndexerClient
from .utils import convert_timestamp_to_ms

load_dotenv()

class VideoService:
    def __init__(
        self,
        account_name=os.environ.get('ACCOUNT_NAME'),
        resource_group=os.environ.get('RESOURCE_GROUP'),
        subscription_id=os.environ.get('SUBSCRIPTION_ID'),
        api_version=os.environ.get('API_VERSION'),
        api_endpoint=os.environ.get('API_ENDPOINT'),
        azure_resource_manager=os.environ.get('AZURE_RESOURCE_MANAGER')
    ):
        consts = Consts(api_version, api_endpoint, azure_resource_manager, account_name, resource_group, subscription_id)
        self.client = VideoIndexerClient()
        self.client.authenticate_async(consts)
        self.client.start_authentication_scheduler()
        self.database = VideoIndexerRepositoryService()

            
    #nicole here!! without indexin
    def index_video_without_indexing (self, video_id: str, excluded_ai: list=None) -> (str, dict):
        """
        Retrieve insights of a video already uploaded and indexed in video indexer

        Args:
            video_id (str): Video ID of the video needed to be fetched. Required.
            excluded_ai (list): AI Features to excluded from Azure Video Indexer. Optional.
        """
        
        insights = self.client.get_video_async(video_id)
        with open(f"nicole_{video_id}.json", "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=4, ensure_ascii=False)

        if insights and video_id:
            document = {
                "video_indexer_id": video_id,
                "insights": insights
            }
            self.database.insert_video_index_raw(document)
            return video_id, insights
        else:
            raise Exception("Indexing Video process failed.")
    
    #this one is the old one with frontend
    def index_video(self, video_base64_encoded: Video, excluded_ai: list=None) -> (str, dict):
        """
        Index Video using Azure AI Video Indexer.

        Args:
            video_base64_encoded (Video): Video to be indexed. Required.
            excluded_ai (list): AI Features to excluded from Azure Video Indexer. Optional.
        """
        if excluded_ai is None:
            excluded_ai = ['Faces', 'Labels', 'Emotions', 'ObservedPeople', 'RollingCredits', 'Celebrities', 'Clapperboard', 'FeaturedClothing', 'ShotType', 'PeopleDetectedClothing']
        
    
        if video_base64_encoded.base64_encoded_video.startswith("data"):
            data = video_base64_encoded.base64_encoded_video.split(",")[1]
        else:
            data = video_base64_encoded.base64_encoded_video

        video_data = base64.b64decode(data)
        video_file = io.BytesIO(video_data)
        video_file.name = video_base64_encoded.video_name
        video_id = self.client.file_upload_async(video_file, video_name=video_file.name, excluded_ai=excluded_ai)


        self.client.wait_for_index_async(video_id) #keep checking every 10seconds until the index is processed 
        
        
        insights = self.client.get_video_async(video_id)
        with open(f"VI_insights_{video_id}.json", "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=4, ensure_ascii=False)
        # print(insights)
    
        if insights and video_id:
            document = {
                "video_indexer_id": video_id,
                "insights": insights
            }
            self.database.insert_video_index_raw(document)
            return video_id, insights
        else:
            raise Exception("Indexing Video process failed.")

    def map_insights_to_document(self, insights):
        """
        Processes OCR insights from Azure Video Indexer and organizes them into structured documents.
        
        This function takes raw OCR (Optical Character Recognition) data from video analysis
        and groups text elements by their spatial and temporal coordinates to create
        meaningful document segments. It handles text that appears at similar times and
        positions to create coherent text blocks.
        
        The function performs the following operations:
        1. Groups OCR text by timestamp (converted to milliseconds)
        2. Sorts text elements by their vertical position (top coordinate)
        3. Groups text that appears at similar vertical positions (within 1 pixel tolerance)
        4. Creates document segments with start time and associated text
        5. Filters out segments with too many text elements (>5) to avoid clutter
        6. Saves the structured data to a JSON file
        
        Args:
            insights (dict): Raw insights data from Azure Video Indexer containing OCR information.
                           Expected structure: insights["videos"][0]["insights"]["ocr"]
        
        Returns:
            None: The function saves the processed data to "frames.json" file
        
        Note:
            This function is used for creating structured text documents from video content
            that can be used for search, indexing, or further text analysis.
        """
        hash_map = collections.defaultdict(list)

        for insight in insights["videos"][0]["insights"]["ocr"]:
            for instance in insight["instances"]:
                heapq.heappush(hash_map[convert_timestamp_to_ms(instance["adjustedStart"])], (insight["top"], insight["left"], insight["id"], insight["text"]))

        documents = []

        # Iterate through the items in the hashMap
        for k, v in hash_map.items():
            last_top = v[0][0]
            same_top = []
            same_time = []
            while v:
                if last_top-1 <= v[0][0] <= last_top+1:
                    same_top.append(heapq.heappop(v)[3])
                else:
                    same_time.append(" ".join(same_top))
                    last_top = v[0][0]
                    same_top = []

            if len(same_top) > 0:
                same_time.append(" ".join(same_top))

            if len(same_time) < 5:
                documents.append({
                    "start": k,
                    "texts": same_time
                })

        document = {"frames": documents}

        self.save_to_file(document, "frames.json")


    def get_player_widget_url_async(self, video_id: str) -> str:
        result = self.client.get_player_widget_url_async(video_id)
        return result

    def get_insights_widgets_url_async(self, video_id: str) -> str:
        result = self.client.get_insights_widgets_url_async(video_id, [], True)
        return result

    def save_to_file(self, data, filename):
        """Save the provided data to a JSON file."""
        try:
            with open(filename, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving to file {filename}: {e}")

    def get_video_thumbnail(self, video_id: str, thumbnail_id: str) -> str:
        encoded_image = self.client.get_video_thumbnail(video_id, thumbnail_id)
        return encoded_image

    def get_prompt_content(self, video_id: str):
        result = self.client.get_prompt_content(video_id, check_alreay_exists=False)
        self.database.insert_prompt_content_raw(result, video_id)
        self.database.insert_prompt_context_index(result, video_id)
        return result

if __name__ == '__main__':
    video_service = VideoService()
    video_service.get_insights_widgets_url_async("o5a4ifcp49")



