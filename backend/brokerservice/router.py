from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from brokerservice.brokerService import BrokerService
from brokerservice.model import UpdateRequestBody, CourseDetailsRequest, VideoDetailsRequest, CourseDetails
from loggingConfig import logger
from transcriptservice.TranscriptService import TranscriptService

load_dotenv()

router = APIRouter(tags=["broker-service"])

broker_service = BrokerService()

@router.put("/visibility", status_code=200)
def get_videos(body: UpdateRequestBody):
    """
    Updates the visibility option for either a video or course.
    
    This endpoint allows administrators to change the visibility status of videos or courses,
    controlling whether they are publicly accessible or hidden from users.
    
    Args:
        body (UpdateRequestBody): Contains the ID, type (VIDEO/COURSE), and new visibility option

    """
    try:
        output = ""
        if body.type == "VIDEO":
            output = broker_service.broker_db.update_visibility_option_video(body.id, body.newOption)
        elif body.type == "COURSE":
            output = broker_service.broker_db.update_visibility_option_course(body.id, body.newOption)
        if output:
            return JSONResponse(status_code=200, content={"message": "Successfully Updated Visibility"})
        else:
            return JSONResponse(status_code=404, content={"message": "No Records Visibility Updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while updating visibility: {str(e)}")

@router.put("/course", status_code=200)
def update_course(body: CourseDetailsRequest):
    """
    Updates course details including course name and description.
    
    This endpoint allows administrators to modify existing course information
    such as course name and description while maintaining the course ID.
    
    Args:
        body (CourseDetailsRequest): Contains the course details to be updated
        
    """
    try:
        output = broker_service.broker_db.update_course_details(body.course_detail)
        if output:
            return JSONResponse(status_code=200, content={"message": "Successfully Updated Course"})
        else:
            return JSONResponse(status_code=404, content={"message": "No Records Course Updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while updating course: {str(e)}")


@router.put("/video", status_code=200)
def update_video(body: VideoDetailsRequest):
    """
    Updates video details including video name and description.
    
    This endpoint allows administrators to modify existing video information
    such as video name and description while maintaining the video ID.
    
    Args:
        body (VideoDetailsRequest): Contains the video details to be updated
   
    """
    try:
        output = broker_service.broker_db.update_video_details(body.video_detail)
        if output:
            return JSONResponse(status_code=200, content={"message": "Successfully Updated Video"})
        else:
            return JSONResponse(status_code=404, content={"message": "No Records Video Updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while updating video: {str(e)}")

@router.get("/videos", status_code=200)
def get_videos():
    """
    Retrieves all public videos with their course mappings.
    
    This endpoint returns a list of all videos that are marked as public/visible,
    organized by their associated courses. This is typically used for displaying
    available content to end users.
    
    Returns:
        dict: Success message with course-video mapping if videos are found,
              or error message if no records are found
    """
    course_video = broker_service.get_video()
    if course_video:
        return {"message": "Successfully Retrieve", "course_video_mapping": course_video}
    else:
        return {"message": "No Records Found"}

@router.get("/videos/manage", status_code=200)
def get_videos_manage():
    """
    Retrieves all videos for management purposes including private/hidden videos.
    
    This endpoint returns a comprehensive list of all videos regardless of their
    visibility status, organized by courses. This is typically used by administrators
    for content management and oversight purposes.
    
    Returns:
        dict: Success message with course-video mapping if videos are found,
              or error message if no records are found
    """
    course_video = broker_service.get_video_manage()
    if course_video:
        return {"message": "Successfully Retrieve", "course_video_mapping": course_video}
    else:
        return {"message": "No Records Found"}

@router.post("/course")
def add_course(body: CourseDetails):
    """
    Creates a new course in the system.
    
    This endpoint allows administrators to add new courses to the system with
    course ID, name, and description. The course will be available for video
    uploads and content management.
    
    Args:
        body (CourseDetails): Contains the course ID, name, and description
        
    Returns:
        dict: Success message if course was added successfully,
              or error message if an exception occurs
        
    Raises:
        Exception: Logs error and returns 500 status if course creation fails
    """
    try:
        broker_service.add_course(body.course_id, body.course_name, body.course_description)
        return {"message": "Successfully Added Course"}
    except Exception as e:
        logger.info("Error at /course: " + str(e))
        return JSONResponse(status_code=500, content={"message": "Error adding Course"})
