class GamificationService:
    LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000]

    @classmethod
    def calculate_level(cls, points: int) -> int:
        level = 1
        for threshold in cls.LEVEL_THRESHOLDS:
            if points >= threshold:
                level += 1
            else:
                break
        return level - 1
