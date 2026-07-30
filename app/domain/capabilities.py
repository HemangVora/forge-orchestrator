from enum import Enum


class Capability(str, Enum):
    CODING = "coding"
    UI = "ui"
    IMAGE = "image"
    REVIEW = "review"
    TESTING = "testing"
