from typing import Optional
import asyncio
from deepgram import Deepgram
import os
import json
from datetime import datetime

class TranscriptionService:
    def __init__(self):
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.dg_client = Deepgram(self.deepgram_api_key)
        
    async def transcribe_audio(self, audio_data: bytes, language: str = "en-US") -> str:
        """
        Transcribe audio data using Deepgram
        """
        try:
            source = {"buffer": audio_data, "mimetype": "audio/wav"}
            response = await self.dg_client.transcription.prerecorded(
                source,
                {
                    "smart_format": True,
                    "model": "nova",
                    "language": language,
                    "punctuate": True,
                    "utterances": True
                }
            )
            
            # Extract the transcript from the response
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            return transcript
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def transcribe_stream(self, audio_stream, language: str = "en-US") -> str:
        """
        Transcribe streaming audio data using Deepgram
        """
        try:
            # Configure real-time transcription
            config = {
                "smart_format": True,
                "model": "nova",
                "language": language,
                "punctuate": True,
                "interim_results": False
            }
            
            # Create WebSocket connection
            connection = await self.dg_client.transcription.live(config)
            
            # Handle incoming transcription results
            transcript = ""
            
            @connection.on("transcriptReceived")
            async def handle_transcript(transcript_data):
                nonlocal transcript
                result = json.loads(transcript_data)
                transcript += result["channel"]["alternatives"][0]["transcript"] + " "
            
            # Send audio data
            while True:
                data = await audio_stream.read()
                if not data:
                    break
                connection.send(data)
            
            # Close connection and return final transcript
            await connection.finish()
            return transcript.strip()
            
        except Exception as e:
            raise Exception(f"Streaming transcription failed: {str(e)}")
    
    def save_transcript(self, transcript: str, filename: Optional[str] = None) -> str:
        """
        Save transcript to a file with timestamp
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transcript_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(transcript)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Failed to save transcript: {str(e)}")
    
    async def process_teams_transcript(self, transcript_text: str) -> str:
        """
        Process and clean up a Teams meeting transcript
        """
        try:
            # Remove speaker labels and timestamps
            lines = transcript_text.split("\n")
            cleaned_lines = []
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Skip lines that are just timestamps or speaker labels
                if ":" in line and len(line.split(":")) == 2:
                    continue
                    
                cleaned_lines.append(line.strip())
            
            return " ".join(cleaned_lines)
            
        except Exception as e:
            raise Exception(f"Failed to process Teams transcript: {str(e)}") 