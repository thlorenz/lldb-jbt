#!/usr/bin/python
import lldb
from sbvalue import value
from sbvalue import variable

def jit_break (frame, bp_loc, dic):
    try: 
        # Getting parse errors at times
        # todo: better to check for NULL or something?

        # todo:
        #       get to code->instruction_start() without evaluating expression (which is slow)
        inst_start_var = frame.EvaluateExpression('reinterpret_cast<uint64_t>(code->instruction_start())');
        inst_start = int(value(inst_start_var).value, 10)

        code_var   = frame.FindVariable('code')
        name_var   = frame.FindVariable('name')
        length_var = frame.FindVariable('length')

        length      = int(value(length_var).value, 10)
        name        = value(name_var).summary.strip('"')
        code        = value(code_var)
        
        print 'start: (%d :: %x) code: %s' % (inst_start, inst_start, code_var)

        #inst_size  = int(value(inst_size_var).value, 10)
    except:
        print "parse error"
        return True

    return True

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('breakpoint set -name v8::internal::PerfBasicLogger::LogRecordedBuffer')
    debugger.HandleCommand('breakpoint command add -F jit.jit_break')
    print 'The jit resolver has been initialized and is ready for use.'
