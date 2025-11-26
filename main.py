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

DELAYED_BATCH_FLUSH_INTERVAL_SECONDS = 3

counter = 0
delayed_batch = []
last_delayed_flush_time = time.time()

try:
    while True:
        counter += 1
        current_time = time.time()

        log_message = f"Processing item {counter}"
        if counter % 2 == 0:
            log_message += " [DELAYED EVENT]"

        record = app_logger.makeRecord(
            app_logger.name,
            logging.INFO,
            "(unknown file)",
            0,
            log_message,
            (),
            None
        )
        record.created = current_time
        record.counter = counter
        record.fake_data = "test"
        record.is_delayed = counter % 2 == 0

        if counter % 2 == 0:
            delayed_batch.append(record)
            print(f"Added log #{counter} to delayed batch (batch size: {len(delayed_batch)})")
        else:
            app_logger.handle(record)
            print(f"Sent log #{counter} immediately")

        time_since_last_flush = current_time - last_delayed_flush_time
        if time_since_last_flush >= DELAYED_BATCH_FLUSH_INTERVAL_SECONDS:
            if delayed_batch:
                print(f"\n>>> Flushing {len(delayed_batch)} DELAYED logs (late arrival after {time_since_last_flush:.1f}s) <<<")
                for delayed_record in delayed_batch:
                    app_logger.handle(delayed_record)
                    print(f"  Sent delayed log #{delayed_record.counter}")
                delayed_batch.clear()
                last_delayed_flush_time = current_time

            logger_provider.force_flush()
            print("Provider flush complete\n")

        time.sleep(0.1)
except KeyboardInterrupt:
    logger_provider.force_flush()
    logger_provider.shutdown()
    print("Shutdown complete")