import os
import aiohttp
from typing import Optional, Dict, Any
from fastapi import UploadFile
from ..models.transcription import TranscriptionResponse
import json
from deepgram import Deepgram

class TranscriptionService:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Deepgram API key")
        self.client = Deepgram(self.api_key)
        
        # Default transcription options
        self.default_options = {
            "smart_format": True,
            "model": "nova",
            "language": "en-US",
            "tier": "enhanced"
        }
    
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio data using Deepgram
        """
        try:
            options = self.default_options.copy()
            if language:
                options["language"] = language
                
            response = await self.client.transcription.prerecorded(
                audio_data,
                options
            )
            
            return {
                "transcript": response["results"]["channels"][0]["alternatives"][0]["transcript"],
                "confidence": response["results"]["channels"][0]["alternatives"][0]["confidence"],
                "language": response["results"]["channels"][0]["detected_language"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    async def transcribe_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio from a file using Deepgram
        """
        try:
            with open(file_path, "rb") as audio:
                audio_data = audio.read()
                return await self.transcribe_audio(audio_data, language)
                
        except Exception as e:
            raise Exception(f"Failed to transcribe file: {str(e)}")
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for transcription
        """
        return [
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "nl", "name": "Dutch"},
            {"code": "hi", "name": "Hindi"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"}
        ]

    async def transcribe(
        self,
        file: UploadFile,
        language: str = "en"
    ) -> TranscriptionResponse:
        """
        Transcribe an audio file using Deepgram
        """
        async with aiohttp.ClientSession() as session:
            # Read the file content
            content = await file.read()
            
            # Prepare the request
            url = f"{self.base_url}/listen?language={language}&model=nova"
            
            # Make the request to Deepgram
            async with session.post(
                url,
                headers=self.headers,
                data=content
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Deepgram API error: {error_text}")
                
                result = await response.json()
                
                # Extract the transcription from the response
                transcript = result["results"]["channels"][0]["alternatives"][0]
                
                return TranscriptionResponse(
                    text=transcript["transcript"],
                    confidence=transcript["confidence"],
                    language=language
                )

    async def transcribe_stream(
        self,
        audio_chunk: bytes,
        language: str = "en"
    ) -> TranscriptionResponse:
        """
        Transcribe streaming audio data using Deepgram
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/listen?language={language}&model=nova&encoding=linear16&sample_rate=16000"
            
            async with session.post(
                url,
                headers=self.headers,
                data=audio_chunk
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Deepgram API error: {error_text}")
                
                result = await response.json()
                
                # Extract the transcription from the response
                transcript = result["results"]["channels"][0]["alternatives"][0]
                
                return TranscriptionResponse(
                    text=transcript["transcript"],
                    confidence=transcript["confidence"],
                    language=language
                ) 