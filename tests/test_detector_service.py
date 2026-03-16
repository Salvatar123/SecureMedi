"""
Tests for DetectorService - Anomaly detection in health vitals.
Tests threshold logic, boundary conditions, and dynamic threshold updates.
"""


from services.detector_service import DetectorService


class TestDetectorServiceThresholds:
    """Test threshold configuration and defaults."""

    def test_default_thresholds(self):
        """Test detector initializes with default thresholds."""
        detector = DetectorService()

        thresholds = detector.get_thresholds()
        assert thresholds["heart_rate_max"] == 110
        assert thresholds["temperature_max"] == 38.0
        assert thresholds["spo2_min"] == 92

    def test_custom_thresholds(self):
        """Test detector accepts custom thresholds."""
        detector = DetectorService(heart_rate_max=120, temperature_max=39.0, spo2_min=90)

        thresholds = detector.get_thresholds()
        assert thresholds["heart_rate_max"] == 120
        assert thresholds["temperature_max"] == 39.0
        assert thresholds["spo2_min"] == 90

    def test_update_thresholds(self):
        """Test runtime threshold updates."""
        detector = DetectorService()

        detector.update_thresholds(heart_rate_max=125, temperature_max=39.5, spo2_min=88)

        thresholds = detector.get_thresholds()
        assert thresholds["heart_rate_max"] == 125
        assert thresholds["temperature_max"] == 39.5
        assert thresholds["spo2_min"] == 88

    def test_partial_threshold_update(self):
        """Test updating only some thresholds."""
        detector = DetectorService()
        prev_hr = detector.heart_rate_max

        detector.update_thresholds(temperature_max=39.0)

        # Only temp should change
        assert detector.heart_rate_max == prev_hr
        assert detector.temperature_max == 39.0


class TestDetectorNormalDetection:
    """Test normal (ALERT=False) detection."""

    def test_all_vitals_normal(self, detector_service, health_data_normal):
        """Test detection when all vitals are normal."""
        result = detector_service.detect(health_data_normal)
        assert result == "NORMAL"

    def test_heart_rate_exactly_at_threshold(self, detector_service):
        """Test heart rate exactly at threshold (should be NORMAL)."""
        data = {"heart": 110, "temp": 37.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_temp_exactly_at_threshold(self, detector_service):
        """Test temperature exactly at threshold (should be NORMAL)."""
        data = {"heart": 70, "temp": 38.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_spo2_exactly_at_threshold(self, detector_service):
        """Test SpO2 exactly at threshold (should be NORMAL)."""
        data = {"heart": 70, "temp": 37.0, "spo2": 92}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_all_vitals_well_within_range(self, detector_service):
        """Test all vitals well within normal range."""
        data = {"heart": 80, "temp": 37.5, "spo2": 96}
        result = detector_service.detect(data)
        assert result == "NORMAL"


class TestDetectorAlertDetection:
    """Test alert (ALERT=True) detection."""

    def test_high_heart_rate(self, detector_service, health_data_alert_high_heart):
        """Test alert triggered by high heart rate."""
        result = detector_service.detect(health_data_alert_high_heart)
        assert result == "ALERT"

    def test_high_temperature(self, detector_service, health_data_alert_high_temp):
        """Test alert triggered by high temperature."""
        result = detector_service.detect(health_data_alert_high_temp)
        assert result == "ALERT"

    def test_low_spo2(self, detector_service, health_data_alert_low_spo2):
        """Test alert triggered by low SpO2."""
        result = detector_service.detect(health_data_alert_low_spo2)
        assert result == "ALERT"

    def test_heart_rate_one_above_threshold(self, detector_service):
        """Test alert triggered when HR is exactly 1 above threshold."""
        data = {"heart": 111, "temp": 37.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "ALERT"

    def test_multiple_vitals_abnormal(self, detector_service):
        """Test alert when multiple vitals are abnormal."""
        data = {"heart": 120, "temp": 38.5, "spo2": 90}
        result = detector_service.detect(data)
        assert result == "ALERT"

    def test_extreme_high_heart_rate(self, detector_service):
        """Test alert with extremely high heart rate."""
        data = {"heart": 180, "temp": 37.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "ALERT"

    def test_extreme_high_temperature(self, detector_service):
        """Test alert with extremely high temperature."""
        data = {"heart": 70, "temp": 40.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "ALERT"

    def test_extreme_low_spo2(self, detector_service):
        """Test alert with extremely low SpO2."""
        data = {"heart": 70, "temp": 37.0, "spo2": 80}
        result = detector_service.detect(data)
        assert result == "ALERT"


class TestDetectorBoundaryConditions:
    """Test edge cases and boundary conditions."""

    def test_missing_heart_rate_defaults_to_zero(self, detector_service):
        """Test missing heart rate defaults to 0 (treated as normal)."""
        data = {"temp": 37.0, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_missing_temperature_defaults_to_zero(self, detector_service):
        """Test missing temperature defaults to 0 (treated as normal)."""
        data = {"heart": 70, "spo2": 98}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_missing_spo2_defaults_to_100(self, detector_service):
        """Test missing SpO2 defaults to 100 (treated as normal)."""
        data = {"heart": 70, "temp": 37.0}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_empty_data_dict(self, detector_service):
        """Test detection with empty data dictionary."""
        result = detector_service.detect({})
        assert result == "NORMAL"

    def test_zero_vitals(self, detector_service):
        """Test detection with all zero vitals."""
        data = {"heart": 0, "temp": 0, "spo2": 100}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_float_vitals(self, detector_service):
        """Test detection works with float values."""
        data = {"heart": 75.5, "temp": 37.2, "spo2": 97.8}
        result = detector_service.detect(data)
        assert result == "NORMAL"

    def test_string_vitals_converted(self, detector_service):
        """Test detection attempts conversion of string values."""
        data = {"heart": "75", "temp": "37.0", "spo2": "98"}
        # This may fail or succeed depending on implementation
        # Just ensure it doesn't crash
        try:
            result = detector_service.detect(data)
            assert result in ["ALERT", "NORMAL"]
        except (ValueError, TypeError):
            # Also acceptable if proper type validation raises
            pass


class TestDetectorWithCustomThresholds:
    """Test detection with custom thresholds."""

    def test_strict_thresholds(self):
        """Test detection with strict thresholds."""
        detector = DetectorService(heart_rate_max=60, temperature_max=37.0, spo2_min=95)

        # Normal vitals would be ALERT with strict thresholds
        data = {"heart": 75, "temp": 37.2, "spo2": 94}
        result = detector.detect(data)
        assert result == "ALERT"

    def test_loose_thresholds(self):
        """Test detection with loose thresholds."""
        detector = DetectorService(heart_rate_max=150, temperature_max=40.0, spo2_min=80)

        # High vitals would be NORMAL with loose thresholds
        data = {"heart": 140, "temp": 39.5, "spo2": 85}
        result = detector.detect(data)
        assert result == "NORMAL"

    def test_threshold_priority(self):
        """Test that any threshold violation triggers ALERT."""
        detector = DetectorService()

        # Only heart rate is violated
        data1 = {"heart": 115, "temp": 37.0, "spo2": 98}
        assert detector.detect(data1) == "ALERT"

        # Only temperature is violated
        data2 = {"heart": 70, "temp": 38.5, "spo2": 98}
        assert detector.detect(data2) == "ALERT"

        # Only SpO2 is violated
        data3 = {"heart": 70, "temp": 37.0, "spo2": 90}
        assert detector.detect(data3) == "ALERT"


class TestDetectorRealistic:
    """Test realistic scenarios."""

    def test_resting_patient(self, detector_service):
        """Test detection for resting patient."""
        data = {"heart": 60, "temp": 36.8, "spo2": 99}
        assert detector_service.detect(data) == "NORMAL"

    def test_exercising_patient(self, detector_service):
        """Test detection for patient after exercise."""
        data = {"heart": 105, "temp": 37.5, "spo2": 97}
        assert detector_service.detect(data) == "NORMAL"

    def test_fever_patient(self, detector_service):
        """Test detection for patient with fever."""
        data = {"heart": 95, "temp": 39.0, "spo2": 96}
        assert detector_service.detect(data) == "ALERT"

    def test_hypoxic_patient(self, detector_service):
        """Test detection for hypothetical hypoxic patient."""
        data = {"heart": 110, "temp": 37.0, "spo2": 88}
        assert detector_service.detect(data) == "ALERT"

    def test_critical_patient(self, detector_service):
        """Test detection for critically ill patient."""
        data = {"heart": 140, "temp": 39.5, "spo2": 85}
        assert detector_service.detect(data) == "ALERT"
