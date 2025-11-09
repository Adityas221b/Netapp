"""Kafka data generator - simulates continuous data flow."""
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataStreamGenerator:
    """Generate continuous data stream events."""
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        """Initialize Kafka producer."""
        self.producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.topic = 'data-ingestion'
        
        # Data source types
        self.sources = ['iot_sensor', 'app_log', 'user_upload', 'database_backup', 'media_file']
        self.content_types = ['video/mp4', 'application/json', 'text/plain', 'image/jpeg', 'application/pdf']
        
        logger.info(f"DataStreamGenerator initialized, publishing to topic: {self.topic}")
    
    def generate_event(self) -> dict:
        """Generate a single data ingestion event."""
        event = {
            'event_id': f"evt_{int(time.time())}_{random.randint(1000, 9999)}",
            'file_id': f"file_{random.randint(100000, 999999)}",
            'file_name': f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}.dat",
            'size_gb': round(random.uniform(0.1, 100), 2),
            'timestamp': datetime.now().isoformat(),
            'source': random.choice(self.sources),
            'content_type': random.choice(self.content_types),
            'metadata': {
                'user_id': f"user_{random.randint(1, 100)}",
                'priority': random.choice(['high', 'medium', 'low']),
                'region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1'])
            }
        }
        
        return event
    
    def stream_events(self, events_per_sec: int = 5, duration_sec: int = None):
        """
        Stream events continuously.
        
        Args:
            events_per_sec: Number of events to generate per second
            duration_sec: Duration to run (None = infinite)
        """
        logger.info(f"Starting data stream: {events_per_sec} events/sec")
        
        start_time = time.time()
        event_count = 0
        
        try:
            while True:
                # Check duration
                if duration_sec and (time.time() - start_time) >= duration_sec:
                    break
                
                # Generate and send event
                event = self.generate_event()
                
                self.producer.send(
                    self.topic,
                    key=event['file_id'],
                    value=event
                )
                
                event_count += 1
                
                if event_count % 10 == 0:
                    logger.info(f"Sent {event_count} events | Last: {event['file_id']} | Size: {event['size_gb']}GB")
                
                # Wait to maintain rate
                time.sleep(1.0 / events_per_sec)
        
        except KeyboardInterrupt:
            logger.info("Stream stopped by user")
        finally:
            self.producer.flush()
            self.producer.close()
            logger.info(f"Stream ended. Total events sent: {event_count}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CloudFlux AI Data Stream Generator')
    parser.add_argument('--rate', type=int, default=5, help='Events per second')
    parser.add_argument('--duration', type=int, default=None, help='Duration in seconds')
    parser.add_argument('--kafka', default='localhost:9092', help='Kafka bootstrap servers')
    
    args = parser.parse_args()
    
    generator = DataStreamGenerator(bootstrap_servers=args.kafka)
    generator.stream_events(events_per_sec=args.rate, duration_sec=args.duration)
