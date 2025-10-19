"""
videoLearnRAG - LLM-based Learning Companion and Co-Pilot for lecture videos.

This package provides intelligent video analysis, transcript processing,
and conversational AI capabilities for educational content.
"""

# Import main services
try:
    from .brokerservice.brokerService import BrokerService
    from .chatservice.chatservice import ChatService
    from .videoindexerclient.VideoService import VideoService
    from .transcriptservice.TranscriptService import TranscriptService
    from .databaseservice.databaseService import DatabaseService
    from .userservice.repository import UserRepositoryService
except ImportError:
    # Fallback for development
    pass

# Expose submodules
from . import brokerservice
from . import chatservice
from . import videoindexerclient
from . import transcriptservice
from . import databaseservice
from . import userservice

# Main classes
__all__ = [
    'BrokerService',
    'ChatService', 
    'VideoService',
    'TranscriptService',
    'DatabaseService',
    'UserRepositoryService',
    'brokerservice',
    'chatservice',
    'videoindexerclient',
    'transcriptservice',
    'databaseservice',
    'userservice'
]

# Version
__version__ = "0.1.0"
