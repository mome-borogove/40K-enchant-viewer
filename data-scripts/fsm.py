#!/usr/bin/env python3

from enum import EnumMeta
import logging
import types
import re

class FSMError(Exception): pass

class FSM(object):
  '''Simple line-by-line FSM parser.

  State-transition function signature:
    StateEnum = lambda(match:re.Match, data:dict)
  or
    StateEnum = lambda()
  or
    None # to ignore the input
  Returning None from a lambda means "stay in the same state"

  Example:
  _S = Enum('_S', 'A B C')
  fsm = FSM(_S, A, [A,B,C], {
    _S.A: [
      (r'pattern', lambda match,data: _S.B),
    ],
    _S.B: [
      (r'pattern', lambda: _S.A),
      (r'ignore_this', None),
    ]
  }'''

  def __init__(self, states, start, stops, machine):
    assert isinstance(states, EnumMeta)
    logging.basicConfig()
    self._trace_logger = logging.getLogger('FSM')
    self._states = states
    self._start = start
    self._stops = stops
    self._verify_fsm(machine)
    self._machine = self._precompile_fsm(machine)
    self.reset()
    self.tracing(False)

  def _verify_fsm(self, machine):
    assert isinstance(machine,dict)
    assert len(machine)>0
    for k,node in machine.items():
      assert k in self._states
      for transitions in node:
        assert len(transitions)==2
        r,f = transitions
        assert isinstance(r,str)
        assert isinstance(f,types.FunctionType) or f is None
        assert ((f is None) or
                (f.__code__.co_argcount==2) or
                (f.__code__.co_argcount==0))
    return True

  def _precompile_fsm(self, fsm):
    return { state :
             [ (re.compile(regex_str), func)
               for regex_str,func in transitions ]
             for state,transitions in fsm.items() }

  def _init_state(self):
    self._data = {}

  def reset(self):
    self._current_state = self._start
    self._init_state()

  def tracing(self, v):
    if v:
      self._trace_logger.setLevel(logging.DEBUG)
      return True
    else:
      self._trace_logger.setLevel(logging.ERROR)
      return False

  def _trace(self, *args, **kwargs):
    return self._trace_logger.debug(*args, **kwargs)

  @property
  def S(self):
    return self._states

  @property
  def state(self):
    return self._current_state

  def __call__(self, input):
    self._trace('In state '+str(self._current_state)+' considering input: '+str(input))
    for regex,func in self._machine[self._current_state]:
      m = re.match(regex,input)
      if m is not None:
        self._trace('Matched '+str(regex))
        # Allow people to define thunks when there's no logic needed
        if func is None:
          next_state = None
        elif func.__code__.co_argcount==0:
          next_state = func()
        else:
          next_state = func(m.groups(), self._data)
        if next_state is not None:
          if next_state not in self._states:
            raise FSMError('Invalid state transition: '+str(next_state))
          self._current_state = next_state
        self._trace('Transitioning to '+str(self._current_state))
        return self._current_state in self._stops
    raise FSMError('No rule in state '+str(self._current_state)+' which matches input: "'+input+'"')

  @property
  def data(self):
    return self._data

  @data.setter
  def data(self, value):
    assert isinstance(value,dict)
    self._data = value

  def terminate(self):
    if self._current_state in self._stops:
      return True
    raise FSMError('Premature termination in state '+str(self._current_state))

