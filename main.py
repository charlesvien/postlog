from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
import logging
import time
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

otlp_exporter = OTLPLogExporter(
    endpoint="http://localhost:4318/v1/logs",
    headers={"Authorization": f"Bearer {os.getenv('POSTHOG_API_KEY')}"}
)

logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        otlp_exporter,
        max_export_batch_size=1,
        schedule_delay_millis=500
    )
)

handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
app_logger = logging.getLogger("postlog")
app_logger.addHandler(handler)
app_logger.setLevel(logging.INFO)
app_logger.propagate = False

counter = 0
try:
    while True:
        counter += 1
        app_logger.info(f"Processing item {counter}", extra={"counter": counter, "fake_data": "test", "timestamp": time.time()})
        print(f"Sent log #{counter}")

        if counter % 5 == 0:
            logger_provider.force_flush()
            print("Flush complete\n")

        time.sleep(1)
except KeyboardInterrupt:
    logger_provider.force_flush()
    logger_provider.shutdown()
    print("Shutdown complete")