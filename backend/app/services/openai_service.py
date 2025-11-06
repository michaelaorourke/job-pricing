"""
OpenAI service for job analysis and chat
"""

from openai import OpenAI
import hashlib
import json
import redis
from typing import Dict, List, Optional, AsyncGenerator
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI integration with caching"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.redis = redis.from_url(settings.REDIS_URL)
        self.cache_ttl = timedelta(hours=24)

    async def analyze_job_description(self, text: str) -> Dict:
        """Extract structured data from job description"""

        # Check cache
        cache_key = self._generate_cache_key("job_analysis", text)
        cached = self.redis.get(cache_key)
        if cached:
            logger.info("Using cached job analysis")
            return json.loads(cached)

        # Define function for structured output
        functions = [{
            "name": "extract_job_info",
            "description": "Extract structured information from job description",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Job title"},
                    "level": {"type": "integer", "description": "Job level (1-10)"},
                    "band": {"type": "integer", "description": "Compensation band (1=tech, 2=non-tech)"},
                    "zone": {"type": "integer", "description": "Geographic zone (1=primary, 2=secondary)"},
                    "years_exp_min": {"type": "integer", "description": "Minimum years of experience"},
                    "years_exp_max": {"type": "integer", "description": "Maximum years of experience"},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "Required skills"},
                    "department": {"type": "string", "description": "Department or job family"},
                    "location": {"type": "string", "description": "Job location"},
                    "remote_type": {
                        "type": "string",
                        "enum": ["onsite", "hybrid", "remote"],
                        "description": "Remote work type"
                    },
                    "key_responsibilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Top 5 key responsibilities"
                    },
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key requirements"
                    },
                    "nice_to_have": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Nice to have qualifications"
                    },
                    "seniority_indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Indicators of seniority level"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score (0-1)"
                    }
                },
                "required": ["title", "level", "skills", "department"]
            }
        }]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert HR analyst specializing in job description analysis
                        and compensation benchmarking. Analyze the job description and extract structured
                        information for salary benchmarking purposes.

                        For job level, use this scale:
                        1-2: Entry level / Junior
                        3-4: Mid-level / Experienced
                        5-6: Senior / Lead
                        7-8: Staff / Principal / Director
                        9-10: VP / C-Level

                        For zone:
                        1 = Primary markets (SF, NYC, Seattle, Boston, LA, DC)
                        2 = Secondary markets (all others)"""
                    },
                    {"role": "user", "content": f"Analyze this job description:\n\n{text}"}
                ],
                functions=functions,
                function_call={"name": "extract_job_info"},
                temperature=0.1
            )

            # Parse function response
            result = json.loads(response.choices[0].message.function_call.arguments)

            # Cache result
            self.redis.setex(
                cache_key,
                int(self.cache_ttl.total_seconds()),
                json.dumps(result)
            )

            # Track usage
            self._track_usage(response.usage)

            return result

        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            # Return basic fallback analysis
            return self._fallback_analysis(text)

    async def chat_completion(self, messages: List[Dict], context: Dict = None) -> str:
        """Generate chat completion"""

        # Add system message with context
        system_message = self._build_system_message(context)
        full_messages = [{"role": "system", "content": system_message}] + messages

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=full_messages,
                temperature=0.7,
                max_tokens=500
            )

            # Track usage
            self._track_usage(response.usage)

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

    async def chat_completion_stream(
        self,
        messages: List[Dict],
        context: Dict = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion for real-time response"""

        system_message = self._build_system_message(context)
        full_messages = [{"role": "system", "content": system_message}] + messages

        try:
            stream = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=full_messages,
                temperature=0.7,
                stream=True,
                max_tokens=500
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI stream error: {e}")
            yield "I'm having trouble connecting. Please try again."

    def generate_embeddings(self, text: str) -> List[float]:
        """Generate text embeddings for semantic search"""

        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

    def _build_system_message(self, context: Dict = None) -> str:
        """Build system message with context"""

        base_message = """You are an expert compensation analyst assistant for the Salary Intelligence Platform.
        You have access to market data from Mercer and Lattice benchmarks.
        Provide accurate, data-driven insights about salary and compensation."""

        if context:
            context_info = f"""
            Current context:
            - Job: {context.get('job_title', 'Not specified')}
            - Location: {context.get('location', 'Not specified')}
            """
            return base_message + context_info

        return base_message

    def _generate_cache_key(self, prefix: str, content: str) -> str:
        """Generate cache key"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"openai:{prefix}:{content_hash}"

    def _track_usage(self, usage):
        """Track token usage for cost monitoring"""
        if usage:
            total_tokens = usage.total_tokens
            # Estimate cost (GPT-4 Turbo: $0.01/1K input, $0.03/1K output)
            input_cost = (usage.prompt_tokens / 1000) * 0.01
            output_cost = (usage.completion_tokens / 1000) * 0.03
            total_cost = input_cost + output_cost

            logger.info(f"OpenAI usage - Tokens: {total_tokens}, Est. cost: ${total_cost:.4f}")

            # Could store in database for tracking

    def _fallback_analysis(self, text: str) -> Dict:
        """Basic pattern-based analysis as fallback"""

        import re

        # Simple pattern matching
        title = "Unknown Position"
        level = 3  # Default to mid-level

        # Try to extract title
        title_patterns = [
            r'(Position|Role|Title):\s*([^\n]+)',
            r'We are (seeking|looking for|hiring) (?:a|an)\s+([^\n]+)',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(2) if len(match.groups()) > 1 else match.group(1)
                break

        # Detect seniority
        if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'principal']):
            level = 5
        elif any(word in text.lower() for word in ['junior', 'jr.', 'entry', 'associate']):
            level = 2
        elif any(word in text.lower() for word in ['staff', 'principal', 'director']):
            level = 7

        # Detect location
        location = "Remote"
        if "san francisco" in text.lower() or "sf" in text.lower():
            location = "San Francisco, CA"
        elif "new york" in text.lower() or "nyc" in text.lower():
            location = "New York, NY"
        elif "austin" in text.lower():
            location = "Austin, TX"

        return {
            "title": title,
            "level": level,
            "band": 1,
            "zone": 1 if location in ["San Francisco, CA", "New York, NY"] else 2,
            "years_exp_min": 2,
            "years_exp_max": 5,
            "skills": [],
            "department": "Engineering",
            "location": location,
            "remote_type": "hybrid",
            "confidence": 0.3
        }