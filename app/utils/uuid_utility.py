""" UUID Utility Module """

from uuid import UUID, uuid4


class UUIDUtility:
    """This class contains utility functions for UUID."""

    @staticmethod
    def remove_hyphens_from_uuid(uuid: str) -> str:
        """This removes hyphens from the UUID."""
        return uuid.replace("-", "")

    @staticmethod
    def format_uuid(uuid: str) -> str:
        """This adds hyphens to the UUID."""
        return str(UUID(uuid))

    @staticmethod
    def binary_to_uuid(binary_uuid: bytes) -> str:
        """This converts binary UUID to string UUID."""
        return str(UUID(bytes=binary_uuid))

    @staticmethod
    def uuid_to_binary(uuid: str) -> bytes:
        """This converts string UUID to binary UUID."""
        return UUID(uuid).bytes

    @staticmethod
    def generate_uuid_bin() -> bytes:
        """This generates a UUID."""
        return uuid4().bytes
