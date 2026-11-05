# -*- coding: utf-8 -*-
"""Praca w tle bez dotykania tkintera z obcego wątku.

Tkinter nie jest bezpieczny wątkowo - `after()` wywołane z wątku roboczego
potrafi wysypać się na „main thread is not in main loop”. Dlatego wątek tylko
odkłada komunikaty do kolejki, a odbiera je główny wątek, odpytując ją cyklicznie.
"""

import queue
import threading

PROGRESS = "progress"
DONE = "done"
FAILED = "failed"


class BackgroundTask(object):
    """Jedno zadanie w tle powiązane z widgetem.

    `work` dostaje funkcję `emit`, którą może zgłaszać postęp. Wszystkie wywołania
    zwrotne wykonują się już w głównym wątku.
    """

    def __init__(self, widget, work, on_done=None, on_error=None, on_progress=None,
                 poll_ms=60):
        self.widget = widget
        self.work = work
        self.on_done = on_done
        self.on_error = on_error
        self.on_progress = on_progress
        self.poll_ms = poll_ms
        self.queue = queue.Queue()
        self.thread = None
        self._cancel = threading.Event()

    def start(self):
        def runner():
            def emit(*args):
                self.queue.put((PROGRESS, args))
            try:
                result = self.work(emit, self._cancel.is_set)
            except Exception as error:
                self.queue.put((FAILED, error))
                return
            self.queue.put((DONE, result))

        self.thread = threading.Thread(target=runner, daemon=True)
        self.thread.start()
        self.widget.after(self.poll_ms, self._poll)
        return self

    def cancel(self):
        self._cancel.set()

    @property
    def cancelled(self):
        return self._cancel.is_set()

    def _poll(self):
        finished = False
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == PROGRESS:
                    if self.on_progress is not None:
                        self.on_progress(*payload)
                elif kind == DONE:
                    finished = True
                    if self.on_done is not None:
                        self.on_done(payload)
                elif kind == FAILED:
                    finished = True
                    if self.on_error is not None:
                        self.on_error(payload)
        except queue.Empty:
            pass
        if not finished:
            try:
                self.widget.after(self.poll_ms, self._poll)
            except Exception:
                # Okno zamknięto w trakcie pracy - nie ma czego odpytywać.
                pass
