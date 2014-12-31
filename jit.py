#!/usr/bin/python
import lldb

DEBUG            = True
kHeaderSize      = 0

LAZY_COMPILE     = 'LazyCompile:'
LAZY_COMPILE_LEN = len(LAZY_COMPILE)

def jit_break (frame, bp_loc, dic):

    # kHeaderSize is a constant and evaluating expressions is expensive, so we only do it once
    global kHeaderSize
    if kHeaderSize == 0:
        kHeaderSize_var = frame.EvaluateExpression('((Code*)0x0)->instruction_start()')
        kHeaderSize = kHeaderSize_var.GetValueAsUnsigned()
        if DEBUG: print 'Determined kHeaderSize: %d' % kHeaderSize


    code_var   = frame.FindVariable('code')
    name_var   = frame.FindVariable('name')
    length_var = frame.FindVariable('length')

    length      = length_var.GetValueAsUnsigned()
    name        = "%.*s" % (length, name_var.GetSummary().strip('"'))
    code        = code_var.GetValueAsUnsigned()
    inst_start  = code + kHeaderSize
    
    if name.startswith(LAZY_COMPILE):
        name = name[LAZY_COMPILE_LEN:]

    # this prints exactly what PerfBasicLogger::LogRecordedBuffer prints omitting the instruction_size since we don't need it
    if DEBUG: print '%x %s' % (inst_start, name)

    return False

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('breakpoint set -name v8::internal::PerfBasicLogger::LogRecordedBuffer')
    debugger.HandleCommand('breakpoint command add -F jit.jit_break')
    print 'The jit resolver has been initialized and is ready for use.'


### Trouble Shooting

## slow method of determining instruction_start() -- uncomment to check against calculated one
# inst_start_var = frame.EvaluateExpression('reinterpret_cast<uint64_t>(code->instruction_start())');
# inst_start_old = int(value(inst_start_var).value, 10)
