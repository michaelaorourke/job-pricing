"""
Mock OpenAI service for testing when API quota is exceeded
"""

import json
import random
from typing import Dict, List, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class MockOpenAIService:
    """Mock OpenAI service for testing"""

    async def analyze_job_description(self, text: str) -> Dict:
        """Mock job analysis - returns realistic test data"""

        logger.info("Using MOCK OpenAI service for job analysis")

        # Simulate different job levels based on keywords
        level = 3  # Default mid-level
        if any(word in text.lower() for word in ['senior', 'lead', 'principal']):
            level = random.choice([5, 6, 7])
        elif any(word in text.lower() for word in ['junior', 'entry', 'associate']):
            level = random.choice([1, 2])
        elif any(word in text.lower() for word in ['staff', 'director', 'vp']):
            level = random.choice([7, 8, 9])

        # Detect location
        location = "San Francisco, CA"  # Default
        if "new york" in text.lower() or "nyc" in text.lower():
            location = "New York, NY"
        elif "austin" in text.lower():
            location = "Austin, TX"
        elif "remote" in text.lower():
            location = "Remote"

        # Generate mock analysis
        return {
            "title": self._extract_title(text),
            "level": level,
            "band": 1 if "engineer" in text.lower() or "developer" in text.lower() else 2,
            "zone": 1 if location in ["San Francisco, CA", "New York, NY"] else 2,
            "years_exp_min": max(0, (level - 1) * 2),
            "years_exp_max": level * 3,
            "skills": [
                "Python", "JavaScript", "SQL", "AWS", "Docker"
            ][:random.randint(3, 5)],
            "department": "Engineering" if "engineer" in text.lower() else "Operations",
            "location": location,
            "remote_type": "hybrid",
            "key_responsibilities": [
                "Design and implement scalable systems",
                "Collaborate with cross-functional teams",
                "Mentor junior team members",
                "Drive technical initiatives",
                "Ensure code quality and best practices"
            ][:random.randint(3, 5)],
            "requirements": [
                "Bachelor's degree in Computer Science or related field",
                f"{level * 2}+ years of relevant experience",
                "Strong problem-solving skills",
                "Excellent communication abilities"
            ],
            "confidence": 0.75
        }

    def _extract_title(self, text: str) -> str:
        """Extract or generate job title"""
        titles = {
            "engineer": "Software Engineer",
            "developer": "Full Stack Developer",
            "manager": "Engineering Manager",
            "analyst": "Data Analyst",
            "designer": "Product Designer",
            "product": "Product Manager"
        }

        text_lower = text.lower()
        for keyword, title in titles.items():
            if keyword in text_lower:
                # Add seniority prefix if found
                if "senior" in text_lower:
                    return f"Senior {title}"
                elif "lead" in text_lower:
                    return f"Lead {title}"
                elif "principal" in text_lower:
                    return f"Principal {title}"
                elif "junior" in text_lower:
                    return f"Junior {title}"
                return title

        return "Software Engineer"  # Default

    async def chat_completion(self, messages: List[Dict], context: Dict = None) -> str:
        """Mock chat completion"""

        user_message = messages[-1]["content"] if messages else ""

        # Generate contextual responses
        if "salary" in user_message.lower():
            return "Based on the market data, the salary range for this position is competitive with similar roles in the area. The recommended range takes into account the required experience level and current market conditions."
        elif "remote" in user_message.lower():
            return "This position offers hybrid work arrangements, with flexibility for remote work 2-3 days per week. The salary range accounts for the location flexibility."
        elif "benefits" in user_message.lower():
            return "The total compensation package includes base salary plus equity, health benefits, 401k matching, and professional development budget."
        else:
            return f"I understand you're asking about: {user_message[:100]}. Based on the job analysis, this is a level {context.get('level', 'N/A')} position with competitive market positioning."

    async def chat_completion_stream(
        self,
        messages: List[Dict],
        context: Dict = None
    ) -> AsyncGenerator[str, None]:
        """Mock streaming chat"""

        response = await self.chat_completion(messages, context)

        # Simulate streaming by yielding words one at a time
        words = response.split()
        for word in words:
            yield word + " "

    def generate_embeddings(self, text: str) -> List[float]:
        """Generate mock embeddings"""
        # Return a mock 1536-dimensional vector
        return [random.random() for _ in range(1536)]

    def _track_usage(self, usage):
        """Mock usage tracking"""
        logger.info("Mock API usage tracked")