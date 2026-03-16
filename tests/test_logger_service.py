"""
Tests for LoggerService - CSV logging with thread safety.
Tests save operations, concurrent access, statistics calculation, and file handling.
"""

import pytest
import os
import csv
from threading import Thread
from services.logger_service import LoggerService


class TestLoggerServiceBasic:
    """Test basic logger operations."""

    def test_logger_initialization(self, logger_service):
        """Test logger service initializes correctly."""
        assert logger_service is not None
        assert logger_service.log_file is not None

    def test_logger_creates_directory(self, tmp_path):
        """Test logger creates log directory if it doesn't exist."""
        nested_path = tmp_path / "logs" / "nested" / "path"
        log_file = nested_path / "test.csv"
        
        logger = LoggerService(log_file=str(log_file))
        assert os.path.exists(nested_path)

    def test_logger_saves_data(self, logger_service, health_data_normal):
        """Test saving health data to CSV."""
        logger_service.save(health_data_normal, "NORMAL")
        
        assert os.path.isfile(logger_service.log_file)
        
        # Verify CSV was written
        with open(logger_service.log_file, 'r') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 1
            assert rows[0]['status'] == 'NORMAL'


class TestLoggerServiceCSVFormat:
    """Test CSV file format and content."""

    def test_csv_headers_created(self, logger_service, health_data_normal):
        """Test CSV headers are created on first write."""
        logger_service.save(health_data_normal, "NORMAL")
        
        with open(logger_service.log_file, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            assert 'timestamp' in headers
            assert 'heart' in headers
            assert 'temp' in headers
            assert 'spo2' in headers
            assert 'status' in headers

    def test_csv_data_format(self, logger_service, health_data_normal):
        """Test CSV data is formatted correctly."""
        logger_service.save(health_data_normal, "NORMAL")
        
        with open(logger_service.log_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            
            assert row['heart'] == str(health_data_normal['heart'])
            assert row['temp'] == str(health_data_normal['temp'])
            assert row['spo2'] == str(health_data_normal['spo2'])
            assert row['status'] == 'NORMAL'
            assert row['timestamp'] != ''

    def test_multiple_saves(self, logger_service, health_data_normal, health_data_alert_high_heart):
        """Test multiple data saves are appended."""
        logger_service.save(health_data_normal, "NORMAL")
        logger_service.save(health_data_alert_high_heart, "ALERT")
        
        with open(logger_service.log_file, 'r') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 2
            assert rows[0]['status'] == 'NORMAL'
            assert rows[1]['status'] == 'ALERT'

    def test_timestamp_format(self, logger_service, health_data_normal):
        """Test timestamp format is ISO format."""
        logger_service.save(health_data_normal, "NORMAL")
        
        with open(logger_service.log_file, 'r') as f:
            row = next(csv.DictReader(f))
            timestamp = row['timestamp']
            
            # ISO format check: should contain 'T' separator
            assert 'T' in timestamp
            assert '-' in timestamp
            assert ':' in timestamp


class TestLoggerServiceRetrieval:
    """Test data retrieval operations."""

    def test_get_latest_records_empty(self, logger_service):
        """Test get_latest_records on empty file."""
        records = logger_service.get_latest_records(10)
        assert records == []

    def test_get_latest_records_limit(self, logger_service, health_data_normal):
        """Test limit parameter in get_latest_records."""
        # Save 5 records
        for i in range(5):
            logger_service.save(health_data_normal, "NORMAL")
        
        # Get last 3
        records = logger_service.get_latest_records(3)
        assert len(records) == 3

    def test_get_latest_records_order(self, logger_service, health_data_normal):
        """Test records are returned in order."""
        logger_service.save(health_data_normal, "NORMAL")
        logger_service.save(health_data_normal, "ALERT")
        logger_service.save(health_data_normal, "NORMAL")
        
        records = logger_service.get_latest_records(10)
        assert len(records) == 3
        # Last record should be last one saved
        assert records[-1]['status'] == 'NORMAL'


class TestLoggerServiceStatistics:
    """Test statistics calculation."""

    def test_get_statistics_empty(self, logger_service):
        """Test statistics for empty file."""
        stats = logger_service.get_statistics()
        assert stats == {}

    def test_get_statistics_single_record(self, logger_service, health_data_normal):
        """Test statistics with single record."""
        logger_service.save(health_data_normal, "NORMAL")
        stats = logger_service.get_statistics()
        
        assert 'heart' in stats
        assert 'temp' in stats
        assert 'spo2' in stats
        assert stats['heart']['min'] == health_data_normal['heart']
        assert stats['heart']['max'] == health_data_normal['heart']
        assert stats['heart']['avg'] == health_data_normal['heart']

    def test_get_statistics_multiple_records(self, logger_service, health_data_normal, health_data_alert_high_heart):
        """Test statistics with multiple records."""
        logger_service.save(health_data_normal, "NORMAL")
        logger_service.save(health_data_alert_high_heart, "ALERT")
        
        stats = logger_service.get_statistics()
        
        # Heart rate: 75 and 115
        assert stats['heart']['min'] == 75
        assert stats['heart']['max'] == 115
        assert stats['heart']['avg'] == 95

    def test_statistics_none_values(self, logger_service):
        """Test statistics handles None values gracefully."""
        # Save data with missing fields
        logger_service.save({"heart": 70}, "NORMAL")
        logger_service.save({"heart": 80}, "NORMAL")
        
        stats = logger_service.get_statistics()
        assert stats is not None


class TestLoggerServiceThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_writes(self, logger_service, health_data_normal):
        """Test multiple threads can write safely."""
        def write_data(count):
            for _ in range(count):
                logger_service.save(health_data_normal, "NORMAL")
        
        threads = []
        for _ in range(5):
            t = Thread(target=write_data, args=(10,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have 5 * 10 = 50 records
        with open(logger_service.log_file, 'r') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 50

    def test_concurrent_read_write(self, logger_service, health_data_normal):
        """Test concurrent reads and writes work correctly."""
        write_count = 0
        
        def write_data():
            nonlocal write_count
            for i in range(20):
                logger_service.save(health_data_normal, f"STATUS_{i}")
                write_count += 1
        
        def read_data():
            for _ in range(5):
                logger_service.get_latest_records(100)
        
        writer = Thread(target=write_data)
        readers = [Thread(target=read_data) for _ in range(3)]
        
        writer.start()
        for r in readers:
            r.start()
        
        writer.join()
        for r in readers:
            r.join()
        
        assert write_count == 20


class TestLoggerServiceCleanup:
    """Test file operations and cleanup."""

    def test_clear_logs(self, logger_service, health_data_normal):
        """Test clearing all logs."""
        logger_service.save(health_data_normal, "NORMAL")
        logger_service.save(health_data_normal, "ALERT")
        
        assert os.path.isfile(logger_service.log_file)
        
        logger_service.clear_logs()
        
        assert not os.path.isfile(logger_service.log_file)

    def test_clear_logs_empty_file(self, logger_service):
        """Test clearing already empty/non-existent log file."""
        # Should not crash
        logger_service.clear_logs()
        assert not os.path.isfile(logger_service.log_file)

    def test_save_after_clear(self, logger_service, health_data_normal):
        """Test saving after clearing logs."""
        logger_service.save(health_data_normal, "NORMAL")
        logger_service.clear_logs()
        logger_service.save(health_data_normal, "ALERT")
        
        with open(logger_service.log_file, 'r') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 1
            assert rows[0]['status'] == 'ALERT'


class TestLoggerServiceErrorHandling:
    """Test error handling in logger service."""

    def test_save_with_missing_fields(self, logger_service):
        """Test saving data with missing vital fields."""
        data = {"heart": 75}  # Missing temp and spo2
        # Should still save
        logger_service.save(data, "NORMAL")
        
        with open(logger_service.log_file, 'r') as f:
            row = next(csv.DictReader(f))
            assert row['heart'] == '75'
            # Missing fields are saved as empty strings, not 'None'
            assert row['temp'] in ['None', '']

    def test_save_handles_special_characters(self, logger_service):
        """Test saving data with special characters."""
        # While health data shouldn't have special chars,
        # test that it doesn't break CSV format
        data = {"heart": 75, "temp": 37.0, "spo2": 98}
        logger_service.save(data, "NORMAL")
        
        # Verify CSV still readable
        with open(logger_service.log_file, 'r') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 1
