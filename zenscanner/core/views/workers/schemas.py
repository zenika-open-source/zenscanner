from ninja import Schema


class ScanInformation(Schema):
    branch: str | None
    last_commit: str | None
