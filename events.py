#events.py
#Copyright (C) 2011 PyTeam

"""Contains the Event class."""

import pygame
import proxyref

class Event(object):
    """Represents a game event."""
    #: Used in automatic handler registration etc
    name = "event"
    #: should be filled by Event subclasses
    #actually, it is better to use metaclasses here so as not to retype same thing in each subclass, but I give you a chance to understand it :-)
    _event_handlers = {}

    def __init__(self, sender, **kwargs):
        """Creates an event.
        @param sender: the object which instantiated the event.
        @type sender: object
        variable number of arguments can be passed to associate with this event.
        for example,  key down event may contain key code as an argument.
        """
        self.sender = sender
        #: whether this event should not be propagated to other handlers
        self.stop_propagating = False
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def propagate(self, handlers):
        """Propagates this event to all registered handlers.
        @param handlers: the list of handlers for this event
        @type handlers: list
        """
        for handler in handlers[:]:
            try:
                handler(self)
            except ReferenceError: #object died
                handlers.remove(handler)
            if self.stop_propagating: #handler requested that the event should not be passed to other handlers
                break

    @classmethod
    def register_event_handler(cls, event, handler):
        """Registers handler for an event.
        Handler will be called when specified event occurs in the system, passing appropriate parameters.
        @param event: the event to register handler for
        @type event: str
        @param handler: callable to call when event occurs
        @type handler: callable
        """                
        handlers = cls._event_handlers.get(event, None)
        if handlers is None:
            raise RuntimeError("event '%s' is not supported")
        #store a weak reference in order not to prevent object from garbage colecting if it listens for events
        handlers.append(proxyref.Proxy(handler))

    @classmethod
    def unregister_event_handler(cls, event, handler):
        """Unregisters a specified event handler."""
        cls._event_handlers[event].remove(proxyref.Proxy(handler))

    @classmethod
    def process_event(cls, event):
        if event is None: return
        event.propagate(cls._event_handlers[event.name])


class KeyDownEvent(Event):
    """User presses the key on the keyboard.
    attributes: unicode, key, mod
    """
    name = 'keydown'
    Event._event_handlers[name] = [] #It is obligatory for all Event subclasses!


class KeyUpEvent(Event):
    """User releases the key on the keyboard.
    attributes: key, mod
    """
    name = 'keyup'
    Event._event_handlers[name] = [] #It is obligatory for all Event subclasses!


class QuitEvent(Event):
    """User requests to quit."""
    name = 'quit'
    Event._event_handlers[name] = []


class ActiveEvent(Event):
    """User switches from/to the game window.
    attributes: gain, state
    """
    name = 'active'
    Event._event_handlers[name] = []


class MouseMotionEvent(Event):
    """Mouse moves inside the game window.
    attributes: pos, rel, buttons
    """
    name = 'mousemotion'
    Event._event_handlers[name] = []


class MouseButtonDownEvent(Event):
    """User presses the mouse button.
    attributes: pos, button
    """
    name = 'mousebuttondown'
    Event._event_handlers[name] = []


class MouseButtonUpEvent(Event):
    """User releases the mouse button.
    attributes: pos, button
    """
    name = 'mousebuttonup'
    Event._event_handlers[name] = []

class AutoListeningObject(object):
    """A mixin which registers event handlers based on present methods.
    Usage:
    class MyClass(AutoListeningObject, ...):
        ...
        def event_keydown(self, event):
            if self.event.code==something:
                self.do_something_cool()
    your method event_keydown will be automatically registered as a handler of event type 'keydown'.
    Enjoy!
    """

    def __init__(self):
        for event_name in Event._event_handlers:
            handler = getattr(self, 'event_%s'%event_name, None)
            if handler is not None:
                Event.register_event_handler(event_name, handler)
        super(AutoListeningObject, self).__init__()

    def __del__(self):
        #unregister all handlers
        for event_name in Event._event_handlers:
            handler = getattr(self, 'event_%s'%event_name, None)
            if handler is not None:
                Event.unregister_event_handler(event_name, handler)


def event_from_pygame_event(sender, event):
    """Maps pygame event to an appropriate Event subclass.
    @param event: a pygame event to map
    @type event: pygame.event.Event
    @returns: an instance of Event subclass
    @rtype: Event
    """
    pygame_events_to_event = {
        'QUIT': QuitEvent,
        'ACTIVEEVENT': ActiveEvent,
        'MOUSEMOTION': MouseMotionEvent,
        'MOUSEBUTTONUP    ': MouseButtonUpEvent,
        'MOUSEBUTTONDOWN': MouseButtonDownEvent,
        'KEYDOWN': KeyDownEvent,
        'KEYUP': KeyUpEvent,
    }
    event_name = pygame.event.event_name(event.type).upper()
    klass = pygame_events_to_event.get(event_name, None)
    if klass is None:
        #raise RuntimeError("There is no Event class for event '%s'"%event_name)
        #print("There is no Event class for event '%s'"%event_name)
        return None
    return klass(sender, **event.dict)
