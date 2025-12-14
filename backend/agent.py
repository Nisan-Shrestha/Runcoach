import re
import logging
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import get_shared_client, LLM_MODEL_ID
from tools import get_all_tools
from rag import rag

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RunningAssistant:
    def __init__(self):
        self.llm = None
        self.tools = None
        self.conversation_history = []
        self._initialized = False
    
    def setup(self):
        """Initialize the assistant"""
        if self._initialized:
            return
        
        logger.info("🤖 [Agent] Initializing...")
        
        # Initialize LLM
        self.llm = ChatBedrock(
            client=get_shared_client(),
            model_id=LLM_MODEL_ID,
            model_kwargs={"temperature": 0.7},
            beta_use_converse_api=True,
        )
        
        # Get tools (excluding search_knowledge_base since we do it automatically)
        all_tools = get_all_tools()
        self.tools = [t for t in all_tools if t.name != "search_knowledge_base"]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Setup RAG
        rag.setup()
        
        self._initialized = True
        logger.info("✅ [Agent] Ready!")
    
    def _get_system_prompt(self, user_profile: dict = None, rag_context: str = None) -> str:
        """Generate system prompt with user profile and RAG context"""
        profile_section = ""
        if user_profile:
            # Filter out empty/None values for cleaner display
            name = user_profile.get('name') or 'Runner'
            age = user_profile.get('age')
            weight = user_profile.get('weight')
            height = user_profile.get('height')
            experience = user_profile.get('experience_level', 'beginner')
            goal = user_profile.get('goal', 'general fitness')
            training_days = user_profile.get('training_days', 3)
            weekly_mileage = user_profile.get('weekly_mileage')
            diet = user_profile.get('dietary_preference', 'none')
            location = user_profile.get('location')
            
            profile_section = f"""
══════════════════════════════════════════════════════════
🎯 USER'S CURRENT GOAL: {goal.upper()}
══════════════════════════════════════════════════════════
IMPORTANT: The user wants to train for {goal}. 
ALL training plans MUST be for {goal} - not marathon, not half-marathon, not any other distance unless {goal} IS that distance.
USER PROFILE:
- Name: {name}
- Age: {age if age else 'Not provided'}
- Weight: {weight} kg
- Height: {height} cm
- Experience Level: {experience}
- Training Days/Week: {training_days}
- Current Weekly Mileage: {weekly_mileage if weekly_mileage else 'Not specified'} km
- Dietary Preference: {diet}
- Location: {location if location else 'Not specified'}
══════════════════════════════════════════════════════════

CRITICAL REMINDERS:
1. Create plans for {goal.upper()} - THIS IS THE USER'S GOAL not anything else is the history
2. Consider user profile and proficieny in running and current Mileage when creating any sorts of plans.
3. You already have weight/height/age - don't ask for them again and use them
4. Use {location} for weather checks if available
"""
        else:
            profile_section = """
NOTE: No user profile available. You may need to ask user to update the profile from the settings tab on the left side of the UI.
"""
        
        context_section = ""
        if rag_context:
            context_section = f"""
KNOWLEDGE BASE CONTEXT:
{rag_context}
---
"""
        
        return f"""You are RunCoach AI, an expert running coach and sports nutritionist.

{profile_section}

{context_section}

AVAILABLE TOOLS:
1. get_weather - Check weather and forecast for run planning  
2. calculate_nutrition - Calculate BMR, TDEE, macros for runners
3. calculate_pace - Analyze pace and predict race times

WHEN TO USE TOOLS:

Use get_weather when:
- User asks "should I run today/tomorrow?"
- User asks "what kind of run should I do?"
- User asks "what should I wear for a run?"
- User asks about outdoor running plans
- User mentions weather, rain, temperature, or conditions
- User wants to plan runs for the week
- User asks about best time to run
- ANY question about tomorrow's run or future runs
- ALWAYS check weather before recommending specific workouts for a day

Use calculate_nutrition when:
- User asks about calories, macros, nutrition plan, or diet
- You have the user's weight, height, and age from their profile
- IMPORTANT: If profile has weight/height/age, use the tool immediately - don't ask for data you already have!

Use calculate_pace when:
- User shares a recent run time/distance
- User wants race time predictions
- User asks about pacing strategy

CRITICAL INSTRUCTIONS:
- ALWAYS call get_weather before recommending what type of run to do on a specific day
- ALWAYS call get_weather before suggesting what to wear for a run
- If the user's profile contains weight, height, and age - USE IT! Don't ask again!
- Base your responses on the KNOWLEDGE BASE CONTEXT provided above
- Provide specific, actionable advice personalized to this user
- Prioritize safety and injury prevention
- Be encouraging but professional

TRAINING PLAN GUIDELINES:
When creating training plans:
1. ALWAYS create the plan for THE USER'S STATED GOAL (shown in profile above)
2. Do NOT default to marathon - use their actual goal distance
3. Include a MIX of these workout types:
   - Easy runs (60-70% of training) - conversational pace
   - Long runs (1 per week) - building endurance
   - Tempo runs (1 per week) - comfortably hard pace
   - Interval/Speed work (1 per week) - 400m/800m repeats, fartlek
   - Recovery runs - very easy, shorter distance
   - Rest days - essential for adaptation

Example week structure:
- Mon: Rest
- Tue: Easy run + strides
- Wed: Intervals (6x800m at 5K pace)
- Thu: Easy run
- Fri: Rest or cross-training
- Sat: Tempo run
- Sun: Long run"""
    
    def chat(self, message: str, user_profile: dict = None) -> dict:
        """Process a chat message"""
        if not self._initialized:
            self.setup()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"💬 [User] {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # Log profile data if available
        if user_profile:
            name = user_profile.get('name', 'Unknown')
            weight = user_profile.get('weight')
            height = user_profile.get('height')
            age = user_profile.get('age')
            location = user_profile.get('location')
            goal = user_profile.get('goal', 'Not set')
            logger.info(f"👤 [Profile] {name} | Age: {age} | Weight: {weight}kg | Height: {height}cm")
            logger.info(f"🎯 [Goal] {goal.upper()} | Location: {location}")
        else:
            logger.info("👤 [Profile] No profile data")
        
        try:
            # STEP 1: Always search knowledge base first
            logger.info("📚 [RAG] Searching knowledge base...")
            rag_context, sources = rag.search(message, k=4)
            
            if sources:
                logger.info(f"📖 [RAG] Found context from: {', '.join(sources)}")
            else:
                logger.info("📭 [RAG] No relevant documents found")
            
            # STEP 2: Build messages with RAG context in system prompt
            system_prompt = self._get_system_prompt(user_profile, rag_context)
            
            messages = [SystemMessage(content=system_prompt)]
            messages.extend(self.conversation_history[-10:])  # Last 10 messages
            messages.append(HumanMessage(content=message))
            
            # STEP 3: Let LLM respond (may use other tools like weather, calculator)
            response = self.llm_with_tools.invoke(messages)
            
            # Check if other tools were called
            if response.tool_calls:
                tool_results = []
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    logger.info(f"🔧 [Tool] Using: {tool_name}")
                    if tool_args:
                        logger.info(f"   [Args] {tool_args}")
                    
                    result = self._execute_tool(tool_name, tool_args)
                    tool_results.append(f"[{tool_name}]:\n{result}")
                
                # Get final response with tool results
                tool_context = "\n\n".join(tool_results)
                follow_up = HumanMessage(
                    content=f"Based on the tool results below, provide a helpful response to: '{message}'\n\nTool Results:\n{tool_context}"
                )
                
                final_response = self.llm.invoke(messages + [response, follow_up])
                response_text = final_response.content
            else:
                response_text = response.content
            
            # Update conversation history (store WITHOUT thinking tags)
            clean_response = self._strip_thinking(response_text)
            self.conversation_history.append(HumanMessage(content=message))
            self.conversation_history.append(AIMessage(content=clean_response))
            
            logger.info(f"✅ [Response] Generated ({len(response_text)} chars)")
            logger.info(f"{'='*50}\n")
            
            # Return FULL response - frontend will parse and display thinking separately
            return {"response": response_text, "success": True}
        
        except Exception as e:
            logger.error(f"❌ [Error] {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "success": False
            }
    
    def _strip_thinking(self, text: str) -> str:
        """Strip thinking tags (used for conversation history only)"""
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        return cleaned.strip()
    
    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """Execute a tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    return tool.invoke(tool_args)
                except Exception as e:
                    logger.error(f"❌ [Tool] Error in {tool_name}: {e}")
                    return f"Tool error: {str(e)}"
        return f"Unknown tool: {tool_name}"
    
    def reset_memory(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🔄 [Agent] Conversation history cleared")


# Global instance
agent = RunningAssistant()