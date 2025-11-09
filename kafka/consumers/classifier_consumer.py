"""Kafka consumer for data classification."""
import json
from kafka import KafkaConsumer
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassifierConsumer:
    """Consume data events and trigger classification."""
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        """Initialize Kafka consumer."""
        self.consumer = KafkaConsumer(
            'data-ingestion',
            bootstrap_servers=[bootstrap_servers],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='classifier-group',
            auto_offset_reset='latest'
        )
        
        logger.info("ClassifierConsumer initialized and listening...")
    
    def process_event(self, event: dict):
        """Process a single event."""
        try:
            file_id = event['file_id']
            size_gb = event['size_gb']
            source = event['source']
            
            # Simulate classification logic
            # In production, this would call the classifier service
            
            # Simple rule-based classification for demo
            if source == 'iot_sensor' or source == 'app_log':
                tier = 'hot'
            elif size_gb < 1.0:
                tier = 'warm'
            else:
                tier = 'cold'
            
            logger.info(
                f"Classified {file_id}: tier={tier}, size={size_gb}GB, source={source}"
            )
            
            # In production, emit classification result to another topic
            return {
                'file_id': file_id,
                'tier': tier,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return None
    
    def start_consuming(self):
        """Start consuming events."""
        logger.info("Starting to consume events...")
        
        try:
            for message in self.consumer:
                event = message.value
                self.process_event(event)
        
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        finally:
            self.consumer.close()
            logger.info("Consumer closed")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CloudFlux AI Classifier Consumer')
    parser.add_argument('--kafka', default='localhost:9092', help='Kafka bootstrap servers')
    
    args = parser.parse_args()
    
    consumer = ClassifierConsumer(bootstrap_servers=args.kafka)
    consumer.start_consuming()
