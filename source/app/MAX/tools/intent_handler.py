"""
Intent Recognition and Fallback Handling for M.A.X. AI Agent
Handles unclear queries, ambiguous inputs, and provides helpful clarifications
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import re
from dataclasses import dataclass
from source.app.MAX.tools.betting_calculator import extract_stake_from_message, extract_odds_from_message


class UserIntent(Enum):
    """User intent categories"""
    GREETING = "greeting"
    PREDICTION_REQUEST = "prediction_request"
    CALCULATION_REQUEST = "calculation_request"
    HISTORICAL_INQUIRY = "historical_inquiry"
    HELP_REQUEST = "help_request"
    COMPLAINT = "complaint"
    THANK_YOU = "thank_you"
    UNCLEAR = "unclear"
    NONSENSICAL = "nonsensical"
    BETTING_STRATEGY = "betting_strategy"
    RESULTS_INQUIRY = "results_inquiry"
    ACCOUNT_RELATED = "account_related"


class ConfidenceLevel(Enum):
    """Confidence levels for intent recognition"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # 0.3 - 0.5
    VERY_LOW = "very_low"  # < 0.3


@dataclass
class IntentAnalysis:
    """Results of intent analysis"""
    intent: UserIntent
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    key_entities: List[str]
    suggested_response_type: str
    clarification_needed: bool
    suggested_questions: List[str]
    fallback_options: List[str]


class IntentHandler:
    """
    Comprehensive intent recognition and fallback handling system
    
    Features:
    - Multi-pattern intent detection
    - Confidence scoring
    - Entity extraction
    - Contextual clarification
    - Fallback response generation
    - Progressive questioning
    """
    
    def __init__(self):
        self.intent_patterns = self._initialize_patterns()
        self.entity_extractors = self._initialize_extractors()
        
    def analyze_intent(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> IntentAnalysis:
        """
        Analyze user message intent with confidence scoring
        
        Args:
            message: User's message
            context: Optional conversation context
            
        Returns:
            IntentAnalysis with detected intent and confidence
        """
        message = message.strip().lower()
        
        if not message or len(message) < 2:
            return self._handle_empty_or_minimal_input()
        
        # Check for special unclear patterns first
        unclear_analysis = self._check_unclear_patterns(message)
        if unclear_analysis:
            return unclear_analysis
        
        # Run through all intent patterns
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = self._calculate_intent_score(message, patterns)
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return self._handle_unrecognized_intent(message)
        
        # Get best matching intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent, confidence = best_intent
        
        # Extract entities
        entities = self._extract_entities(message)
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence)
        
        # Generate response recommendations
        response_type, clarification_needed, questions, fallbacks = self._generate_response_guidance(
            intent, confidence, entities, message, context
        )
        
        return IntentAnalysis(
            intent=intent,
            confidence=confidence,
            confidence_level=confidence_level,
            key_entities=entities,
            suggested_response_type=response_type,
            clarification_needed=clarification_needed,
            suggested_questions=questions,
            fallback_options=fallbacks
        )
    
    def generate_fallback_response(self, analysis: IntentAnalysis, user_name: str = "there") -> str:
        """
        Generate appropriate fallback response based on intent analysis
        
        Args:
            analysis: Intent analysis results
            user_name: User's name for personalization
            
        Returns:
            Formatted fallback response
        """
        if analysis.intent == UserIntent.UNCLEAR:
            return self._generate_unclear_response(analysis, user_name)
        elif analysis.intent == UserIntent.NONSENSICAL:
            return self._generate_nonsensical_response(user_name)
        elif analysis.confidence < 0.5:
            return self._generate_low_confidence_response(analysis, user_name)
        else:
            return self._generate_clarification_response(analysis, user_name)
    
    def _initialize_patterns(self) -> Dict[UserIntent, List[Dict[str, Any]]]:
        """Initialize intent detection patterns"""
        return {
            UserIntent.GREETING: [
                {"keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"], "weight": 1.0},
                {"keywords": ["greetings", "howdy", "what's up", "how are you"], "weight": 0.9},
            ],
            
            UserIntent.PREDICTION_REQUEST: [
                {"keywords": ["predict", "prediction", "tip", "tips", "picks"], "weight": 1.0},
                {"keywords": ["today's games", "matches today", "tomorrow", "fixtures"], "weight": 0.9},
                {"keywords": ["odds", "bet", "betting", "wager"], "weight": 0.8},
                {"keywords": ["cricket", "football", "match", "game"], "weight": 0.7},
                {"keywords": ["who will win", "winner", "outcome"], "weight": 0.8},
            ],
            
            UserIntent.CALCULATION_REQUEST: [
                {"keywords": ["calculate", "profit", "return", "how much"], "weight": 1.0},
                {"keywords": ["odds", "stake", "win", "payout"], "weight": 0.9},
                {"keywords": ["ev", "expected value", "positive ev"], "weight": 1.0},
                {"keywords": ["£", "$", "€", "money"], "weight": 0.7},
            ],
            
            UserIntent.HISTORICAL_INQUIRY: [
                {"keywords": ["yesterday", "last week", "previous", "history"], "weight": 1.0},
                {"keywords": ["my bets", "my picks", "my results"], "weight": 0.9},
                {"keywords": ["how did", "result", "outcome", "won", "lost"], "weight": 0.8},
            ],
            
            UserIntent.HELP_REQUEST: [
                {"keywords": ["help", "how to", "what is", "explain"], "weight": 1.0},
                {"keywords": ["don't understand", "confused", "not sure"], "weight": 0.9},
                {"keywords": ["guide", "tutorial", "how does"], "weight": 0.8},
            ],
            
            UserIntent.COMPLAINT: [
                {"keywords": ["wrong", "bad", "terrible", "awful", "hate"], "weight": 1.0},
                {"keywords": ["disappointed", "frustrated", "angry"], "weight": 0.9},
                {"keywords": ["not working", "broken", "useless"], "weight": 0.8},
            ],
            
            UserIntent.THANK_YOU: [
                {"keywords": ["thank", "thanks", "appreciate", "grateful"], "weight": 1.0},
                {"keywords": ["good job", "well done", "excellent"], "weight": 0.8},
            ],
            
            UserIntent.BETTING_STRATEGY: [
                {"keywords": ["strategy", "approach", "method", "system"], "weight": 1.0},
                {"keywords": ["bankroll", "risk management", "staking"], "weight": 0.9},
                {"keywords": ["safe bets", "sure bets", "conservative"], "weight": 0.8},
            ],
            
            UserIntent.RESULTS_INQUIRY: [
                {"keywords": ["results", "scores", "final score", "outcome"], "weight": 1.0},
                {"keywords": ["won", "lost", "draw", "tied"], "weight": 0.8},
            ],
            
            UserIntent.ACCOUNT_RELATED: [
                {"keywords": ["account", "profile", "settings", "subscription"], "weight": 1.0},
                {"keywords": ["login", "password", "register", "sign up"], "weight": 0.9},
            ],
        }
    
    def _initialize_extractors(self) -> Dict[str, List[str]]:
        """Initialize entity extraction patterns"""
        return {
            "sports": ["cricket", "football", "soccer", "tennis", "basketball", "baseball"],
            "teams": ["manchester", "liverpool", "arsenal", "chelsea", "india", "australia", "england"],
            "time_references": ["today", "tomorrow", "yesterday", "tonight", "weekend", "next week"],
            "betting_markets": ["winner", "over", "under", "btts", "draw", "handicap"],
            "currencies": ["£", "$", "€", "pounds", "dollars", "euros"],
        }
    
    def _check_unclear_patterns(self, message: str) -> Optional[IntentAnalysis]:
        """Check for clearly unclear patterns"""
        unclear_patterns = [
            r"^\?+$",  # Just question marks
            r"^\.+$",  # Just dots
            r"^[a-z]$",  # Single letter
            r"^(what|huh|eh)\?*$",  # Simple confusion
            r"^(i don't know|idk|no idea)$",  # Don't know responses
            r"^\w{1,2}$",  # Very short responses
            r"^(hmm|uhh|err|um)$",  # Thinking sounds
        ]
        
        for pattern in unclear_patterns:
            if re.match(pattern, message):
                return IntentAnalysis(
                    intent=UserIntent.UNCLEAR,
                    confidence=0.9,
                    confidence_level=ConfidenceLevel.HIGH,
                    key_entities=[],
                    suggested_response_type="clarification",
                    clarification_needed=True,
                    suggested_questions=self._get_clarification_questions(),
                    fallback_options=["Show main options", "Ask for specific help"]
                )
        
        return None
    
    def _calculate_intent_score(self, message: str, patterns: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for an intent"""
        max_score = 0.0
        
        for pattern in patterns:
            keywords = pattern["keywords"]
            weight = pattern["weight"]
            
            # Check for exact keyword matches
            matches = sum(1 for keyword in keywords if keyword in message)
            if matches > 0:
                # Score based on matches and weight
                score = (matches / len(keywords)) * weight
                max_score = max(max_score, score)
        
        return min(1.0, max_score)
    
    def _extract_entities(self, message: str) -> List[str]:
        """Extract entities from the message"""
        entities = []
        
        for category, terms in self.entity_extractors.items():
            for term in terms:
                if term in message:
                    entities.append(f"{category}:{term}")
        
        # Extract numbers (potential stakes/odds)
        numbers = re.findall(r'\d+(?:\.\d+)?', message)
        for number in numbers:
            entities.append(f"number:{number}")
        
        return entities
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to level"""
        if confidence > 0.8:
            return ConfidenceLevel.HIGH
        elif confidence > 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence > 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_response_guidance(
        self,
        intent: UserIntent,
        confidence: float,
        entities: List[str],
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> Tuple[str, bool, List[str], List[str]]:
        """Generate response guidance based on intent and confidence"""
        
        if confidence < 0.5:
            return (
                "clarification",
                True,
                self._get_clarification_questions(),
                ["Show main options", "Ask for specific sport", "Provide examples"]
            )
        
        response_guidance = {
            UserIntent.PREDICTION_REQUEST: (
                "prediction",
                self._needs_sport_clarification(entities),
                ["Which sport interests you?", "Looking for today's games or tomorrow's?"],
                ["Show today's cricket matches", "Show football fixtures", "Show all sports"]
            ),
            
            UserIntent.CALCULATION_REQUEST: (
                "calculation",
                self._needs_calculation_details(message),
                ["What's your stake amount?", "What odds are you looking at?"],
                ["Help with profit calculation", "Explain betting odds", "Show example calculation"]
            ),
            
            UserIntent.HISTORICAL_INQUIRY: (
                "historical",
                False,
                [],
                ["Show recent bets", "Show last week's results", "Show betting history"]
            ),
            
            UserIntent.HELP_REQUEST: (
                "help",
                False,
                [],
                ["Show M.A.X. capabilities", "Explain betting basics", "Show example predictions"]
            ),
            
            UserIntent.GREETING: (
                "greeting",
                False,
                [],
                ["Show today's opportunities", "Get started with predictions"]
            ),
            
            UserIntent.THANK_YOU: (
                "acknowledgment",
                False,
                [],
                ["Show more opportunities", "Any other questions?"]
            ),
        }
        
        return response_guidance.get(intent, (
            "general",
            True,
            ["How can I help you with betting predictions?"],
            ["Show main menu", "Get predictions", "Calculate profits"]
        ))
    
    def _needs_sport_clarification(self, entities: List[str]) -> bool:
        """Check if sport clarification is needed"""
        sports_mentioned = [e for e in entities if e.startswith("sports:")]
        return len(sports_mentioned) == 0
    
    def _needs_calculation_details(self, message: str) -> bool:
        """Check if calculation details are missing"""
        has_stake = extract_stake_from_message(message) is not None
        has_odds = extract_odds_from_message(message) is not None
        return not (has_stake and has_odds)
    
    def _get_clarification_questions(self) -> List[str]:
        """Get generic clarification questions"""
        return [
            "What would you like to know about?",
            "Are you looking for predictions, calculations, or results?",
            "Which sport interests you - cricket or football?",
            "How can I help you with betting today?"
        ]
    
    def _handle_empty_or_minimal_input(self) -> IntentAnalysis:
        """Handle empty or very short inputs"""
        return IntentAnalysis(
            intent=UserIntent.UNCLEAR,
            confidence=1.0,
            confidence_level=ConfidenceLevel.HIGH,
            key_entities=[],
            suggested_response_type="prompt",
            clarification_needed=True,
            suggested_questions=["How can I help you today?"],
            fallback_options=["Show main options", "Get started guide"]
        )
    
    def _handle_unrecognized_intent(self, message: str) -> IntentAnalysis:
        """Handle completely unrecognized messages"""
        return IntentAnalysis(
            intent=UserIntent.NONSENSICAL,
            confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            key_entities=self._extract_entities(message),
            suggested_response_type="redirect",
            clarification_needed=True,
            suggested_questions=self._get_clarification_questions(),
            fallback_options=["Show what M.A.X. can do", "Get example predictions"]
        )
    
    def _generate_unclear_response(self, analysis: IntentAnalysis, user_name: str) -> str:
        """Generate response for unclear inputs"""
        responses = [
            f"I'm not quite sure what you're looking for, {user_name}! 🤔",
            f"Could you clarify what you need help with, {user_name}? 💭",
            f"I want to help, {user_name}, but I need a bit more detail! 🎯"
        ]
        
        base_response = responses[0]  # Could be randomized
        
        options = [
            "📊 Get today's cricket predictions",
            "⚽ Check football matches", 
            "💰 Calculate betting profits",
            "📈 See your recent bets"
        ]
        
        return f"{base_response}\n\nHere's what I can help you with:\n" + "\n".join(options)
    
    def _generate_nonsensical_response(self, user_name: str) -> str:
        """Generate response for nonsensical inputs"""
        return (
            f"I didn't quite catch that, {user_name}! 😅\n\n"
            f"I'm M.A.X., your sports prediction specialist! Here's what I can do:\n"
            f"🏏 Cricket predictions and analysis\n"
            f"⚽ Football match insights\n"
            f"💰 Profit calculations and betting advice\n"
            f"📊 Your betting history and results\n\n"
            f"What interests you most? 🚀"
        )
    
    def _generate_low_confidence_response(self, analysis: IntentAnalysis, user_name: str) -> str:
        """Generate response for low confidence intent detection"""
        intent_responses = {
            UserIntent.PREDICTION_REQUEST: f"Looking for predictions, {user_name}? Which sport - cricket 🏏 or football ⚽?",
            UserIntent.CALCULATION_REQUEST: f"Want to calculate something, {user_name}? What's your stake and odds?",
            UserIntent.HISTORICAL_INQUIRY: f"Checking past results, {user_name}? Which timeframe interests you?",
            UserIntent.HELP_REQUEST: f"Need help, {user_name}? What specific area can I assist with?",
        }
        
        base_response = intent_responses.get(
            analysis.intent, 
            f"I think I understand, {user_name}, but could you be more specific? 🤔"
        )
        
        if analysis.suggested_questions:
            return f"{base_response}\n\n{analysis.suggested_questions[0]}"
        
        return base_response
    
    def _generate_clarification_response(self, analysis: IntentAnalysis, user_name: str) -> str:
        """Generate clarification response for medium confidence intents"""
        if analysis.suggested_questions:
            question = analysis.suggested_questions[0]
            return f"I can help with that, {user_name}! {question}"
        
        return f"Got it, {user_name}! Let me get that information for you. 🚀"
    
    def is_calculation_query(self, message: str) -> bool:
        """Quick check if message is a calculation query"""
        analysis = self.analyze_intent(message)
        return analysis.intent == UserIntent.CALCULATION_REQUEST and analysis.confidence > 0.6
    
    def is_prediction_query(self, message: str) -> bool:
        """Quick check if message is a prediction query"""
        analysis = self.analyze_intent(message)
        return analysis.intent == UserIntent.PREDICTION_REQUEST and analysis.confidence > 0.6
    
    def requires_clarification(self, message: str) -> bool:
        """Check if message requires clarification"""
        analysis = self.analyze_intent(message)
        return analysis.clarification_needed or analysis.confidence < 0.5
    
    def get_contextual_help(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Get contextual help based on message and context"""
        analysis = self.analyze_intent(message, context)
        
        if analysis.intent == UserIntent.UNCLEAR:
            return "I can help you with predictions, calculations, or checking results. What interests you? 🎯"
        elif analysis.intent == UserIntent.PREDICTION_REQUEST and analysis.clarification_needed:
            return "I'd love to get you some predictions! Which sport are you interested in? 🏏⚽"
        elif analysis.intent == UserIntent.CALCULATION_REQUEST and analysis.clarification_needed:
            return "I can calculate your potential profits! Just tell me your stake amount and the odds 💰"
        else:
            return "I'm here to help with sports betting insights! Ask me about predictions, calculations, or results 🚀"


# Quick utility functions for integration
def handle_unclear_message(message: str, user_name: str = "there") -> str:
    """Quick function to handle unclear messages"""
    handler = IntentHandler()
    analysis = handler.analyze_intent(message)
    return handler.generate_fallback_response(analysis, user_name)


def detect_intent_type(message: str) -> str:
    """Quick function to detect intent type"""
    handler = IntentHandler()
    analysis = handler.analyze_intent(message)
    return analysis.intent.value


def needs_clarification(message: str) -> bool:
    """Quick function to check if clarification is needed"""
    handler = IntentHandler()
    return handler.requires_clarification(message)


# Export main components
__all__ = [
    "IntentHandler",
    "UserIntent", 
    "IntentAnalysis",
    "ConfidenceLevel",
    "handle_unclear_message",
    "detect_intent_type", 
    "needs_clarification"
]