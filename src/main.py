import signal
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from config.settings import TELEGRAM_BOT_TOKEN
from communication.telegram_bot import TelegramBot
from communication.command_dispatcher import CommandDispatcher
from communication.telemetry import Telemetry
from navigation.navigator import Navigator
from navigation.path_planner import PathPlanner
from hardware.motors import MotorController
from utils.logger import setup_logger

logger=setup_logger('main')

class RoverSystem:
    def __init__(self):
        self.running=False
        self.motors=None
        self.navigator=None
        self.telemetry=None
        self.planner=None
        self.dispatcher=None
        self.bot=None
    
    def initialize(self):
        logger.info("Initializing Rover System...")
        
        self.motors=MotorController()
        self.planner=PathPlanner()
        self.navigator=Navigator(self.motors)
        self.telemetry=Telemetry()
        self.dispatcher=CommandDispatcher(self.navigator, self.planner, self.telemetry)
        self.bot=TelegramBot(TELEGRAM_BOT_TOKEN, self.dispatcher)
        
        logger.info("Rover System initialized successfully")
    
    def start(self):
        self.running=True
        logger.info("Starting Rover System...")
        
        self.telemetry.start()
        self.navigator.start()
        
        logger.info("Starting Telegram Bot...")
        self.bot.start_polling()
    
    def shutdown(self):
        logger.info("Shutting down Rover System...")
        self.running=False
        
        if self.navigator:
            self.navigator.stop()
        if self.telemetry:
            self.telemetry.stop()
        if self.motors:
            self.motors.stop()
        
        logger.info("Rover System shutdown complete")

def signal_handler(sig, frame):
    logger.info("Interrupt received, shutting down...")
    rover.shutdown()
    sys.exit(0)

if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    rover=RoverSystem()
    rover.initialize()
    rover.start()