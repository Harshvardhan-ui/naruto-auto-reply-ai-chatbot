"""
Auto-Reply AI Chatbot - WhatsApp Roast Bot
Author: AI Assistant
Description: Monitors WhatsApp Web, generates humorous roast-style responses using OpenAI GPT
"""

import pyautogui
import time
import pyperclip
import openai
import re
import logging
import sys
from typing import Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration settings for the chatbot"""
    target_user: str = "Rohan Das"
    check_interval: int = 10  # seconds
    openai_api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 150
    temperature: float = 0.8
    enable_bot: bool = True
    safety_delay: float = 2.0  # seconds between operations
    max_retries: int = 3
    chat_app_name: str = "WhatsApp Web"
    
    # Screen coordinates (will be calibrated)
    chat_area_top: Optional[int] = None
    chat_area_bottom: Optional[int] = None
    input_field_x: Optional[int] = None
    input_field_y: Optional[int] = None

class WhatsAppAutoReplyBot:
    """Main class for the auto-reply chatbot system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.last_message_hash = None
        self.sent_messages = []
        self.retry_count = 0
        
        # Initialize OpenAI API
        if config.openai_api_key:
            openai.api_key = config.openai_api_key
        else:
            logger.error("OpenAI API key not provided")
            raise ValueError("OpenAI API key is required")
    
    def calibrate_screen_positions(self):
        """Calibrate screen coordinates for chat application"""
        logger.info("Starting screen calibration...")
        print("Move your mouse to the TOP of the chat area in 5 seconds...")
        time.sleep(5)
        self.config.chat_area_top = pyautogui.position().y
        print(f"Top position saved: {self.config.chat_area_top}")
        
        print("Move your mouse to the BOTTOM of the chat area in 5 seconds...")
        time.sleep(5)
        self.config.chat_area_bottom = pyautogui.position().y
        print(f"Bottom position saved: {self.config.chat_area_bottom}")
        
        print("Move your mouse to the INPUT FIELD in 5 seconds...")
        time.sleep(5)
        self.config.input_field_x, self.config.input_field_y = pyautogui.position()
        print(f"Input field position saved: ({self.config.input_field_x}, {self.config.input_field_y})")
        
        logger.info("Screen calibration completed")
    
    def select_and_copy_chat_history(self) -> bool:
        """Select and copy chat history from the chat window"""
        try:
            # Move to top of chat area
            pyautogui.moveTo(
                x=pyautogui.size().width // 2,  # Center of screen
                y=self.config.chat_area_top,
                duration=0.5
            )
            
            # Click and drag to bottom
            pyautogui.mouseDown()
            time.sleep(0.2)
            pyautogui.moveTo(
                x=pyautogui.size().width // 2,
                y=self.config.chat_area_bottom,
                duration=1.0
            )
            pyautogui.mouseUp()
            
            # Copy selection
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(self.config.safety_delay * 0.5)
            
            logger.info("Chat history copied to clipboard")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy chat history: {e}")
            return False
    
    def get_chat_history(self) -> Optional[str]:
        """Retrieve chat history from clipboard"""
        try:
            # Clear clipboard first to ensure fresh data
            pyperclip.copy('')
            time.sleep(0.1)
            
            if not self.select_and_copy_chat_history():
                return None
            
            time.sleep(0.5)  # Wait for clipboard to update
            chat_text = pyperclip.paste()
            
            if not chat_text or chat_text.isspace():
                logger.warning("No text found in clipboard")
                return None
            
            logger.debug(f"Retrieved chat history: {len(chat_text)} characters")
            return chat_text
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None
    
    def parse_last_message_sender(self, chat_text: str) -> Tuple[bool, str]:
        """
        Parse chat history to determine sender of last message
        
        Returns: (is_target_user, cleaned_chat_text)
        """
        if not chat_text:
            return False, ""
        
        # Split by lines and filter out empty lines
        lines = [line.strip() for line in chat_text.split('\n') if line.strip()]
        
        if not lines:
            return False, ""
        
        # Find the last message sender
        # Assuming format like "Sender Name\nMessage Text"
        last_message_line = -1
        for i in range(len(lines)-1, -1, -1):
            if re.match(r'^[A-Za-z\s]+$', lines[i]) and i < len(lines)-1:
                # This looks like a sender name (only letters and spaces)
                last_message_line = i
                break
        
        if last_message_line == -1:
            logger.warning("Could not identify sender in chat history")
            return False, chat_text
        
        last_sender = lines[last_message_line]
        is_target = self.config.target_user.lower() in last_sender.lower()
        
        logger.info(f"Last message sender: {last_sender}, Is target: {is_target}")
        return is_target, chat_text
    
    def generate_ai_response(self, chat_history: str) -> Optional[str]:
        """Generate humorous roast response using OpenAI API"""
        system_prompt = f"""You are Naruto Uzumaki from the Naruto anime series. 
        You're in a chat with {self.config.target_user} and you need to respond with funny, 
        light-hearted roasts based on the chat history.
        
        Guidelines:
        1. Stay in character as Naruto - use his speech patterns and personality
        2. Make responses humorous and playful, not mean-spirited
        3. Keep responses relatively short (1-2 sentences)
        4. Reference the chat history when relevant
        5. Use Naruto's catchphrases occasionally ("Believe it!", "Dattebayo!")
        6. Be creative and entertaining
        
        Remember: This is all in good fun!"""
        
        user_prompt = f"""Chat History with {self.config.target_user}:
        {chat_history}
        
        Generate a funny, roast-style response as Naruto:"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                n=1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up the response
            ai_response = re.sub(r'^["\'](.*)["\']$', r'\1', ai_response)
            ai_response = re.sub(r'\s+', ' ', ai_response)
            
            logger.info(f"Generated AI response: {ai_response}")
            return ai_response
            
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}")
            return None
    
    def send_response(self, response: str):
        """Send the AI-generated response to the chat"""
        try:
            # Copy response to clipboard
            pyperclip.copy(response)
            time.sleep(self.config.safety_delay * 0.5)
            
            # Click on input field
            pyautogui.click(
                x=self.config.input_field_x,
                y=self.config.input_field_y,
                duration=0.3
            )
            time.sleep(0.5)
            
            # Paste response
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # Send message (Enter key)
            pyautogui.press('enter')
            
            # Log the sent message
            self.sent_messages.append({
                'timestamp': datetime.now().isoformat(),
                'message': response
            })
            
            logger.info(f"Response sent successfully")
            
        except Exception as e:+0
        # Get chat history
        chat_text = self.get_chat_history()
        if not chat_text:
            logger.warning("No chat history retrieved")
            return False
        
        # Check if last message is from target user
        is_target, cleaned_chat = self.parse_last_message_sender(chat_text)
        
        if not is_target:
            logger.info("Last message not from target user, skipping")
            return False
        
        # Generate hash to avoid responding to same message
        current_hash = hash(chat_text[-500:])  # Hash last 500 chars
        if current_hash == self.last_message_hash:
            logger.info("Already responded to this message")
            return False
        
        # Generate AI response
        ai_response = self.generate_ai_response(cleaned_chat)
        if not ai_response:
            logger.error("Failed to generate AI response")
            return False
        
        # Send response
        self.send_response(ai_response)
        
        # Update last message hash
        self.last_message_hash = current_hash
        
        return True
    
    def run(self):
        """Main execution loop"""
        logger.info(f"Starting Auto-Reply AI Chatbot for {self.config.target_user}")
        logger.info(f"Bot enabled: {self.config.enable_bot}")
        
        if not self.config.enable_bot:
            logger.info("Bot is disabled. Exiting.")
            return
        
        # Calibrate if positions not set
        if any(pos is None for pos in [
            self.config.chat_area_top,
            self.config.chat_area_bottom,
            self.config.input_field_x,
            self.config.input_field_y
        ]):
            logger.warning("Screen positions not calibrated")
            self.calibrate_screen_positions()
        
        # Main monitoring loop
        try:
            while True:
                try:
                    if self.retry_count >= self.config.max_retries:
                        logger.error("Max retries exceeded. Stopping bot.")
                        break
                    
                    success = self.check_for_new_message()
                    
                    if success:
                        logger.info(f"Response sent successfully. Waiting {self.config.check_interval} seconds.")
                        self.retry_count = 0  # Reset retry count on success
                    else:
                        logger.info(f"No response needed. Waiting {self.config.check_interval} seconds.")
                    
                    time.sleep(self.config.check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.retry_count += 1
                    time.sleep(self.config.check_interval)
                    
        finally:
            logger.info("Bot shutdown complete")
            self.save_logs()
    
    def save_logs(self):
        """Save sent messages to a log file"""
        try:
            with open('sent_messages.json', 'w') as f:
                import json
                json.dump(self.sent_messages, f, indent=2)
            logger.info(f"Saved {len(self.sent_messages)} sent messages to log file")
        except Exception as e:
            logger.error(f"Failed to save logs: {e}")

def main():
    """Main entry point"""
    
    # Configuration
    config = Config(
        target_user="Rohan Das",
        check_interval=15,  # Check every 15 seconds
        openai_api_key="YOUR_OPENAI_API_KEY_HERE",  # Replace with your API key
        model="gpt-3.5-turbo",
        max_tokens=150,
        temperature=0.8,
        enable_bot=True,
        safety_delay=2.0
    )
    
    # Instructions for setup
    print("=" * 60)
    print("AUTO-REPLY AI CHATBOT SETUP")
    print("=" * 60)
    print("\nBefore starting:")
    print("1. Open Chrome and navigate to WhatsApp Web")
    print("2. Log in and open the chat with the target user")
    print("3. Make sure the chat window is visible")
    print("4. Have your OpenAI API key ready")
    print("\nThe bot will ask you to calibrate screen positions.")
    print("=" * 60)
    
    # Get OpenAI API key if not provided
    if config.openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
        api_key = input("\nEnter your OpenAI API key: ").strip()
        if api_key:
            config.openai_api_key = api_key
        else:
            print("API key is required. Exiting.")
            return
    
    # Create and run bot
    try:
        bot = WhatsAppAutoReplyBot(config)
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()