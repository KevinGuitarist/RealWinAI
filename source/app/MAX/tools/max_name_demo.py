"""
M.A.X. Name-based Greeting Demo
Demonstrates how M.A.X. now greets users by their actual names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from max_big_brother_personality import BigBrotherPersonality
from max_user_personalization import UserPersonalizationSystem, UserProfile
from datetime import datetime


def demo_name_greetings():
    """Demonstrate M.A.X. greeting users by their actual names"""
    
    print("🎯 M.A.X. PERSONALIZED GREETING DEMO")
    print("=" * 50)
    
    # Initialize systems
    big_brother = BigBrotherPersonality()
    user_system = UserPersonalizationSystem()
    
    # Demo different users
    users = [
        {"name": "Vaibhav", "is_first_time": True},
        {"name": "Rahul", "is_first_time": True}, 
        {"name": "Priya", "is_first_time": False},
        {"name": "Amit", "is_first_time": False}
    ]
    
    for user in users:
        name = user["name"]
        is_first_time = user["is_first_time"]
        
        print(f"\n--- Greeting for {name} ({'First Time' if is_first_time else 'Returning'}) ---")
        
        # Create user profile
        user_id = f"user_{name.lower()}"
        profile = user_system.create_user_profile(user_id, name)
        
        # Get personalized greeting
        greeting = big_brother.greet_user_by_name(name, is_first_time)
        print(f"M.A.X.: {greeting}")
        
        # Show how M.A.X. uses their name in responses
        sample_response = big_brother.get_personality_response(
            "advice", 
            {"query": "Should I bet on this match?"}, 
            "India has a 65% chance of winning based on recent form.", 
            user_id
        )
        print(f"\nSample Response:\nM.A.X.: {sample_response[:150]}...")
    
    print("\n" + "=" * 50)
    print("✅ M.A.X. now greets everyone by their actual name!")
    print("✅ Names are used throughout conversations for personal touch")


if __name__ == "__main__":
    demo_name_greetings()