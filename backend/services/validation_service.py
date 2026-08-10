from backend.domain.sensor import SensorEvent


class ValidationService:

    @staticmethod
    def validate(data):

        sensor = SensorEvent(**data)

        return sensor.model_dump(mode='json')