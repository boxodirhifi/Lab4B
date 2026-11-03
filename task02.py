# Lab 4B - Task 2: The notifier that silently did nothing
#
# Answers:
# 2.1 The base class send() is an empty pass, so calling it does nothing and
#     raises no error. The typo sned() just creates a *new* method; nobody
#     calls it, and nothing complains.
# 2.2 Notifier is now an ABC with an abstract send(). TelegramNotifier with
#     the typo cannot be instantiated - Python raises TypeError at creation
#     time because the abstract method is not implemented.
# 2.3 Abstract: send(). Concrete (shared by all children): notify().
#     max_length is a class attribute, each child overrides it.
# 2.4 SmsNotifier uses max_length = 160. test_notify_cuts_text_per_channel
#     proves notify() cuts at each channel's own limit.
from abc import ABC, abstractmethod
import inspect
import pytest


class Notifier(ABC):
    max_length = 1000

    @abstractmethod
    def send(self, recipient: str, text: str) -> None: ...
    def notify(self, recipient: str, text: str) -> None:
        self.send(recipient, text[: self.max_length])


class TelegramNotifier(Notifier):
    max_length = 4096

    def send(self, recipient: str, text: str) -> None:
        print(f"telegram -> {recipient}: {text}")


class SmsNotifier(Notifier):
    max_length = 160

    def send(self, recipient: str, text: str) -> None:
        print(f"sms -> {recipient}: {text}")


def test_notifier_cannot_be_created():
    with pytest.raises(TypeError):
        Notifier()


def test_missing_send_raises_typeerror():
    class BrokenNotifier(Notifier):
        def sned(self, recipient, text):
            pass

    with pytest.raises(TypeError):
        BrokenNotifier()


def test_notify_written_once():
    source = inspect.getsource(Notifier)
    assert source.count("def notify") == 1


def test_notify_cuts_text_per_channel(capsys):
    long_text = "a" * 5000
    TelegramNotifier().notify("@ali", long_text)
    SmsNotifier().notify("+998900000000", long_text)
    out = capsys.readouterr().out.splitlines()
    telegram_line = out[0]
    sms_line = out[1]
    assert len(telegram_line.split(": ", 1)[1]) == 4096
    assert len(sms_line.split(": ", 1)[1]) == 160
