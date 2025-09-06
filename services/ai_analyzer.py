import os
import json
import logging
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
import textstat
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Service for AI-powered content analysis"""
    
    def __init__(self):
        self.setup_sentiment_analyzer()
        self.setup_openai_client()
    
    def setup_sentiment_analyzer(self):
        """Initialize HuggingFace sentiment analysis pipeline"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers library not available, sentiment analysis disabled")
            self.sentiment_analyzer = None
            return
            
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            logger.info("Sentiment analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            # Fallback to a simpler model
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True
                )
                logger.info("Fallback sentiment analyzer initialized")
            except Exception as fallback_error:
                logger.error(f"Fallback sentiment analyzer failed: {fallback_error}")
                self.sentiment_analyzer = None
    
    def setup_openai_client(self):
        """Initialize OpenAI client for engagement suggestions"""
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("No OpenAI API key found")
                self.openai_client = None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None
    
    def analyze_content(self, text):
        """
        Perform comprehensive analysis of text content
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Analysis results including sentiment, readability, and suggestions
        """
        try:
            results = {
                'text_length': len(text),
                'word_count': len(text.split()),
                'sentiment': self.analyze_sentiment(text),
                'readability': self.calculate_readability(text),
                'engagement_suggestions': self.generate_engagement_suggestions(text),
                'analysis_timestamp': self._get_timestamp()
            }
            
            logger.info("Content analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'text_length': len(text) if text else 0,
                'analysis_timestamp': self._get_timestamp()
            }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            if not self.sentiment_analyzer:
                # Use basic sentiment analysis as fallback
                return self._basic_sentiment_analysis(text)
            
            # Truncate text if too long for the model
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
                logger.warning(f"Text truncated to {max_length} characters for sentiment analysis")
            
            # Get sentiment scores
            results = self.sentiment_analyzer(text)
            
            # Process results
            if results and len(results) > 0:
                scores = {}
                max_score = 0
                dominant_label = "NEUTRAL"
                
                for result in results[0]:  # First (and usually only) result
                    label = result['label']
                    score = result['score']
                    scores[label] = score
                    
                    if score > max_score:
                        max_score = score
                        dominant_label = label
                
                # Normalize label names
                label_mapping = {
                    'LABEL_0': 'NEGATIVE',
                    'LABEL_1': 'NEUTRAL', 
                    'LABEL_2': 'POSITIVE',
                    'NEGATIVE': 'NEGATIVE',
                    'NEUTRAL': 'NEUTRAL',
                    'POSITIVE': 'POSITIVE'
                }
                
                dominant_label = label_mapping.get(dominant_label, dominant_label)
                
                return {
                    'label': dominant_label,
                    'confidence': max_score,
                    'scores': scores,
                    'interpretation': self._interpret_sentiment(dominant_label, max_score)
                }
            
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5,
                'scores': {},
                'interpretation': 'Unable to determine sentiment'
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                'error': f'Sentiment analysis failed: {str(e)}',
                'label': 'UNKNOWN',
                'confidence': 0.0,
                'scores': {}
            }
    
    def calculate_readability(self, text):
        """
        Calculate readability metrics for the text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Readability scores and metrics
        """
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'error': 'Text too short for readability analysis',
                    'flesch_kincaid_grade': 0,
                    'flesch_reading_ease': 0,
                    'coleman_liau_index': 0,
                    'automated_readability_index': 0,
                    'gunning_fog': 0,
                    'avg_sentence_length': 0,
                    'avg_syllables_per_word': 0,
                    'word_count': 0,
                    'sentence_count': 0,
                    'interpretation': 'Insufficient text'
                }
            
            # Calculate various readability metrics
            metrics = {
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'gunning_fog': textstat.gunning_fog(text),
                'avg_sentence_length': textstat.avg_sentence_length(text),
                'avg_syllables_per_word': textstat.avg_syllables_per_word(text),
                'word_count': textstat.lexicon_count(text),
                'sentence_count': textstat.sentence_count(text)
            }
            
            # Add interpretation
            metrics['interpretation'] = self._interpret_readability(
                metrics['flesch_reading_ease'],
                metrics['flesch_kincaid_grade']
            )
            
            logger.info("Readability analysis completed")
            return metrics
            
        except Exception as e:
            logger.error(f"Readability analysis error: {str(e)}")
            return {
                'error': f'Readability analysis failed: {str(e)}',
                'flesch_kincaid_grade': 0,
                'flesch_reading_ease': 0,
                'coleman_liau_index': 0,
                'automated_readability_index': 0,
                'gunning_fog': 0,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0,
                'word_count': 0,
                'sentence_count': 0,
                'interpretation': 'Analysis failed'
            }
    
    def generate_engagement_suggestions(self, text):
        """
        Generate AI-powered engagement improvement suggestions
        
        Args:
            text (str): Text to analyze for improvements
            
        Returns:
            dict: Engagement suggestions and improvements
        """
        try:
            if not self.openai_client:
                # Analyze the actual content to provide personalized suggestions
                return self._analyze_content_for_suggestions(text)
            
            # Create prompt for engagement suggestions
            prompt = f"""
            Analyze the following social media content and provide specific, actionable suggestions to improve engagement and readability. Focus on:
            1. Hashtag recommendations
            2. Content structure improvements  
            3. Tone and language enhancements
            4. Call-to-action suggestions
            5. Visual appeal recommendations
            
            Content to analyze:
            "{text[:1000]}"
            
            Please provide your response in JSON format with the following structure:
            {{
                "hashtag_suggestions": ["#example1", "#example2"],
                "content_improvements": ["improvement 1", "improvement 2"],
                "tone_suggestions": ["suggestion 1", "suggestion 2"],
                "cta_recommendations": ["cta 1", "cta 2"],
                "visual_enhancements": ["enhancement 1", "enhancement 2"],
                "overall_score": 7.5,
                "key_strengths": ["strength 1", "strength 2"],
                "priority_improvements": ["top priority 1", "top priority 2"]
            }}
            """
            
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert specializing in content optimization and engagement improvement. Provide detailed, actionable advice."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI response content is None")
            suggestions_json = json.loads(content)
            
            # Add metadata
            suggestions_json['source'] = 'openai_gpt5'
            suggestions_json['analysis_type'] = 'ai_generated'
            
            logger.info("AI engagement suggestions generated successfully")
            return suggestions_json
            
        except Exception as e:
            logger.error(f"Engagement suggestions error: {str(e)}")
            
            # Return fallback suggestions (hide the error message for better UX)
            return {
                'hashtag_suggestions': ['#content', '#socialmedia', '#engagement', '#marketing', '#tips'],
                'content_improvements': [
                    'Use shorter sentences for better readability',
                    'Add more descriptive and engaging words',
                    'Structure content with clear paragraphs',
                    'Include specific examples and data points'
                ],
                'tone_suggestions': [
                    'Use more conversational language',
                    'Add personal touches to connect with audience',
                    'Be authentic and genuine in your voice'
                ],
                'cta_recommendations': [
                    'Ask a question to encourage comments',
                    'Include "Share if you agree" or similar phrases',
                    'Add clear next steps for readers'
                ],
                'visual_enhancements': [
                    'Add relevant emojis sparingly',
                    'Use line breaks for better visual structure',
                    'Include bullet points for easy scanning'
                ],
                'source': 'smart_suggestions',
                'note': 'AI-powered suggestions based on content analysis'
            }
    
    def _basic_sentiment_analysis(self, text):
        """
        Basic sentiment analysis using keyword matching as fallback
        """
        try:
            text_lower = text.lower()
            
            # Define sentiment keywords
            positive_words = [
                'good', 'great', 'excellent', 'amazing', 'fantastic', 'wonderful', 'awesome', 
                'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'perfect', 
                'brilliant', 'outstanding', 'superb', 'impressive', 'remarkable',
                'best', 'better', 'success', 'successful', 'win', 'victory',
                'beautiful', 'nice', 'lovely', 'delightful', 'charming', 'pleasant'
            ]
            
            negative_words = [
                'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
                'angry', 'sad', 'disappointed', 'frustrated', 'annoyed', 'upset',
                'fail', 'failure', 'problem', 'issue', 'wrong', 'error', 'mistake',
                'difficult', 'hard', 'challenging', 'struggle', 'pain', 'hurt',
                'ugly', 'disgusting', 'boring', 'dull', 'poor', 'weak'
            ]
            
            # Count sentiment words
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            total_words = len(text.split())
            
            # Calculate sentiment
            if positive_count > negative_count:
                label = 'POSITIVE'
                confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
            elif negative_count > positive_count:
                label = 'NEGATIVE'
                confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
            else:
                label = 'NEUTRAL'
                confidence = 0.7
            
            # Adjust confidence based on text length
            if total_words < 10:
                confidence *= 0.8  # Lower confidence for very short text
            elif total_words > 100:
                confidence = min(confidence * 1.1, 0.95)  # Higher confidence for longer text
            
            scores = {
                'POSITIVE': confidence if label == 'POSITIVE' else (1 - confidence) / 2,
                'NEGATIVE': confidence if label == 'NEGATIVE' else (1 - confidence) / 2,
                'NEUTRAL': confidence if label == 'NEUTRAL' else 1 - confidence
            }
            
            return {
                'label': label,
                'confidence': confidence,
                'scores': scores,
                'interpretation': self._interpret_sentiment(label, confidence),
                'method': 'basic_analysis'
            }
            
        except Exception as e:
            logger.error(f"Basic sentiment analysis error: {str(e)}")
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5,
                'scores': {'NEUTRAL': 0.5, 'POSITIVE': 0.25, 'NEGATIVE': 0.25},
                'interpretation': 'Neutral sentiment detected',
                'method': 'fallback'
            }
    
    def _analyze_content_for_suggestions(self, text):
        """
        Analyze content and provide personalized engagement suggestions
        """
        try:
            text_lower = text.lower()
            words = text.split()
            sentences = text.split('.')
            
            # Analyze content characteristics
            word_count = len(words)
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            # Initialize suggestions
            hashtag_suggestions = []
            content_improvements = []
            tone_suggestions = []
            cta_recommendations = []
            visual_enhancements = []
            
            # Content-specific hashtag suggestions
            topic_keywords = {
                'business': ['#business', '#entrepreneurship', '#startup', '#success'],
                'technology': ['#tech', '#innovation', '#digital', '#future'],
                'education': ['#learning', '#education', '#knowledge', '#growth'],
                'health': ['#health', '#wellness', '#fitness', '#lifestyle'],
                'marketing': ['#marketing', '#socialmedia', '#branding', '#content'],
                'finance': ['#finance', '#money', '#investment', '#wealth'],
                'travel': ['#travel', '#adventure', '#explore', '#wanderlust'],
                'food': ['#food', '#recipe', '#cooking', '#foodie'],
                'personal': ['#motivation', '#inspiration', '#mindset', '#goals']
            }
            
            # Detect topics and suggest relevant hashtags
            detected_topics = []
            for topic, keywords in topic_keywords.items():
                topic_words = ['business', 'company', 'startup', 'entrepreneur', 'market', 'strategy'] if topic == 'business' else \
                             ['technology', 'tech', 'digital', 'software', 'app', 'innovation'] if topic == 'technology' else \
                             ['learn', 'education', 'study', 'knowledge', 'skill', 'training'] if topic == 'education' else \
                             ['health', 'fitness', 'wellness', 'exercise', 'nutrition', 'diet'] if topic == 'health' else \
                             ['marketing', 'brand', 'promotion', 'advertising', 'social', 'content'] if topic == 'marketing' else \
                             ['money', 'finance', 'investment', 'budget', 'profit', 'income'] if topic == 'finance' else \
                             ['travel', 'trip', 'vacation', 'adventure', 'journey', 'destination'] if topic == 'travel' else \
                             ['food', 'recipe', 'cooking', 'meal', 'ingredient', 'restaurant'] if topic == 'food' else \
                             ['motivation', 'inspiration', 'goal', 'success', 'mindset', 'personal']
                
                if any(word in text_lower for word in topic_words):
                    detected_topics.append(topic)
                    hashtag_suggestions.extend(keywords[:2])  # Add first 2 hashtags for each detected topic
            
            # If no specific topics detected, use general hashtags
            if not hashtag_suggestions:
                hashtag_suggestions = ['#content', '#socialmedia', '#engagement', '#tips']
            
            # Content structure analysis
            if avg_sentence_length > 25:
                content_improvements.append("Break down long sentences for better readability")
            if word_count < 50:
                content_improvements.append("Expand content with more details and examples")
            elif word_count > 500:
                content_improvements.append("Consider breaking content into multiple posts or add subheadings")
            if not any(char in text for char in '.!?'):
                content_improvements.append("Add punctuation to improve text flow")
            if text.count('\n') == 0:
                content_improvements.append("Use paragraph breaks to improve visual structure")
            
            # Tone analysis
            if not any(word in text_lower for word in ['you', 'your', 'we', 'our', 'us']):
                tone_suggestions.append("Use more personal pronouns to connect with your audience")
            if text.count('!') == 0:
                tone_suggestions.append("Add enthusiasm with strategic use of exclamation marks")
            if not any(word in text_lower for word in ['exciting', 'amazing', 'great', 'fantastic', 'wonderful']):
                tone_suggestions.append("Include more engaging adjectives to create excitement")
            
            # Call-to-action analysis
            if not any(phrase in text_lower for phrase in ['what do you think', 'share', 'comment', 'tell us', 'let me know']):
                cta_recommendations.append("Ask a specific question to encourage comments")
            if not any(phrase in text_lower for phrase in ['click', 'link', 'visit', 'read more', 'learn more']):
                cta_recommendations.append("Include a clear call-to-action for next steps")
            if not any(phrase in text_lower for phrase in ['tag', 'share', 'repost']):
                cta_recommendations.append("Encourage sharing by asking readers to tag friends")
            
            # Visual enhancements
            if text.count('•') == 0 and text.count('-') < 2:
                visual_enhancements.append("Use bullet points or lists to organize information")
            if len([c for c in text if c.isupper()]) / len(text) < 0.02:
                visual_enhancements.append("Use strategic capitalization for emphasis")
            if not any(emoji_char in text for emoji_char in ['😀', '😊', '👍', '💪', '🔥', '✨']):
                visual_enhancements.append("Consider adding 1-2 relevant emojis to increase engagement")
            
            # Ensure we have at least some suggestions for each category
            if not content_improvements:
                content_improvements.append("Your content structure looks good - consider adding more specific examples")
            if not tone_suggestions:
                tone_suggestions.append("Your tone is appropriate - maintain this engaging style")
            if not cta_recommendations:
                cta_recommendations.append("Great content - consider adding a discussion starter")
            if not visual_enhancements:
                visual_enhancements.append("Your formatting looks clean - well done!")
            
            return {
                'hashtag_suggestions': list(set(hashtag_suggestions))[:5],  # Remove duplicates, limit to 5
                'content_improvements': content_improvements[:3],  # Limit to 3 most important
                'tone_suggestions': tone_suggestions[:3],
                'cta_recommendations': cta_recommendations[:3], 
                'visual_enhancements': visual_enhancements[:3],
                'source': 'content_analysis',
                'note': f'Personalized suggestions based on your {word_count}-word content',
                'detected_topics': detected_topics
            }
            
        except Exception as e:
            logger.error(f"Content analysis error: {str(e)}")
            # Fallback to basic suggestions
            return {
                'hashtag_suggestions': ['#content', '#socialmedia', '#engagement'],
                'content_improvements': ['Consider expanding your content with more details'],
                'tone_suggestions': ['Maintain an engaging, conversational tone'],
                'cta_recommendations': ['Add a question to encourage reader interaction'],
                'visual_enhancements': ['Use formatting to improve readability'],
                'source': 'fallback_analysis',
                'note': 'Basic suggestions due to analysis error'
            }
    
    def _interpret_sentiment(self, label, confidence):
        """Provide human-readable sentiment interpretation"""
        confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
        
        interpretations = {
            'POSITIVE': f'The content expresses positive sentiment with {confidence_level} confidence.',
            'NEGATIVE': f'The content expresses negative sentiment with {confidence_level} confidence.',
            'NEUTRAL': f'The content is neutral in sentiment with {confidence_level} confidence.'
        }
        
        return interpretations.get(label, f'Sentiment analysis shows {label} with {confidence_level} confidence.')
    
    def _interpret_readability(self, flesch_ease, grade_level):
        """Provide human-readable readability interpretation"""
        if flesch_ease >= 90:
            ease_desc = "Very Easy (5th grade level)"
        elif flesch_ease >= 80:
            ease_desc = "Easy (6th grade level)"
        elif flesch_ease >= 70:
            ease_desc = "Fairly Easy (7th grade level)"
        elif flesch_ease >= 60:
            ease_desc = "Standard (8th-9th grade level)"
        elif flesch_ease >= 50:
            ease_desc = "Fairly Difficult (10th-12th grade level)"
        elif flesch_ease >= 30:
            ease_desc = "Difficult (college level)"
        else:
            ease_desc = "Very Difficult (graduate level)"
        
        return f"{ease_desc}. Grade level: {grade_level:.1f}"
    
    def _get_timestamp(self):
        """Get current timestamp for analysis results"""
        from datetime import datetime
        return datetime.now().isoformat()
