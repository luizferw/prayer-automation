import os
import logging


log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "prayer_automation.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PrayerAutomation")
