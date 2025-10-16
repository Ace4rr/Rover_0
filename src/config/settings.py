import os
import json
from pathlib import Path

BASE_DIR=Path(__file__).parent.parent

SECRETS_FILE=BASE_DIR / "config" / "secrets.json"

def load_secrets():
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE, 'r') as f:
            return json.load(f)
    return {}

secrets=load_secrets()

TELEGRAM_BOT_TOKEN=secrets.get('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', ''))
YANDEX_API_KEY=secrets.get('YANDEX_API_KEY', os.getenv('YANDEX_API_KEY', ''))
ROVER_ID=secrets.get('ROVER_ID', 'DELIVERY_ROVER_001')

CONTROL_CENTER_URL=secrets.get('CONTROL_CENTER_URL', 'http://localhost:8000')

TELEMETRY_INTERVAL=5

MOTOR_LEFT_PIN=17
MOTOR_RIGHT_PIN=27
PWM_FREQUENCY=1000

GPS_SERIAL_PORT='/dev/ttyUSB0'
GPS_BAUD_RATE=9600

LIDAR_PORT='/dev/ttyUSB1'
LIDAR_BAUD_RATE=115200

LOG_LEVEL='INFO'
LOG_FILE=BASE_DIR / "logs" / "rover.log"

PID_KP=1.0
PID_KI=0.1
PID_KD=0.05

MAX_SPEED=100
MIN_SPEED=30

OBSTACLE_DETECTION_DISTANCE=1.0

WAYPOINT_TOLERANCE=2.0