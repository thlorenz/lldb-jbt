#!/usr/bin/python
import lldb

DEBUG            = False
kHeaderSize      = 0

LAZY_COMPILE     = 'LazyCompile:'
LAZY_COMPILE_LEN = len(LAZY_COMPILE)

from threading import Timer

class Address:
    def __init__(self, inst_start, name):
        self.decimalAddress     = inst_start
        self.hexadecimalAddress = "0x%x" % inst_start
        self.name               = name

unresolvedAddress = Address(0, '')

class Addresses:
    def __init__(self):
        self._addresses = []
        self._sorted = True
    
    def __getitem__(self, key):
        return self._addresses[key]

    def getKey(self, addr):
        return addr.decimalAddress

    def push(self, val):
        self._addresses.append(val)
        self._sorted = False

    def sort_addresses(self):
        if self._sorted: return
        self._addresses = sorted(self._addresses, key=self.getKey)
        self._sorted = True

    def len(self):
        return len(self._addresses)

    def resolve(self, addr):
        self.sort_addresses()

        # if address is smaller than the we first one we have a symbol for bail out immediately
        if self.len() == 0 or addr < self._addresses[0].decimalAddress: return unresolvedAddress

        prev = unresolvedAddress
        for a in self._addresses:
            if addr < a.decimalAddress: return prev
            prev = a
        
        # fell off the end of the list so we might be inside the last symbol
        if addr < prev.decimalAddress + 4096: return prev

        return unresolvedAddress

addresses = Addresses()

def jit_break (frame, bp_loc, dic):

    # kHeaderSize is a constant and evaluating expressions is expensive, so we only do it once
    global kHeaderSize
    if kHeaderSize == 0:
        kHeaderSize_var = frame.EvaluateExpression('((Code*)0x0)->instruction_start()')
        kHeaderSize = kHeaderSize_var.GetValueAsUnsigned()
        
        # If not in debug mode instruction_start symbol is not found
        # error:  call to a function 'v8::internal::Code::instruction_start()' ('_ZN2v88internal4Code17instruction_startEv') 
        #         that is not present in the target 
        # In that case just go with `5f == 95`, this hopefully is close enough on any architecture
        if kHeaderSize == 0: 
            kHeaderSize = 95 
            print 'Warning, could not determine kHeaderSize since node is not running in debug mode. Using approximate instead.'
            if DEBUG: print 'Guessed kHeaderSize: %d' % kHeaderSize
            print 'Run node_g if you want to run in debug mode'
        else:
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

    addresses.push(Address(inst_start, name))

    return False

def jit_bt (debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    frames = thread.get_thread_frames()

    if addresses.len() == 0:
        print 'WARN: jbt is unable to resolve any JavaScript symbols since it has not collected any symbol information yet.'
        print '      You may use "bt" instead since jbt couldn\'t add any extra information at this point.'
        print '      Did you debug Node.js >= v0.11.13 with the --perf-basic-prof flag and "run" the target yet? Example: "lldb -- node_g --perf-basic-prof index.js".'
        return 

    print '* thread: #%d: tid = 0x%x, %s' % (thread.GetIndexID(), thread.GetThreadID(), frame)
    for f in frames:
        star = ' '
        if f.GetFrameID() == frame.GetFrameID(): star = '*'
        name = '%s' % f.GetFunctionName()
        if name != 'None': 
            print ' %s %s' % (star, f)
        else:
            addr = f.GetPC()
            resolved = addresses.resolve(addr)
            print ' %s %s %s' % (star, f, resolved.name)

def run_commands(command_interpreter, commands):
    return_obj = lldb.SBCommandReturnObject()
    for command in commands:
        command_interpreter.HandleCommand( command, return_obj )
        if return_obj.Succeeded():
            if DEBUG: print return_obj.GetOutput()
        else:
            if DEBUG: print return_obj
            return False
    return True

def __lldb_init_module(debugger, internal_dict):
    ci = debugger.GetCommandInterpreter()

    def initBreakPoint():
        success = run_commands(ci, [ 
            'breakpoint set -name v8::internal::PerfBasicLogger::LogRecordedBuffer', 
            'breakpoint command add -F jbt.jit_break' 
        ])
        # Keep trying to set the breakpoint until it succeeds which means we finally have a target set by the user.
        # This is especially important for tools like Xcode which set the target automatically.
        # We need to make sure we don't miss too much generated code after the target starts running, but also don't want to slow things down too much
        # 200ms seems like a good compromise
        if not success:
            t = Timer(0.2, initBreakPoint)
            t.start()

    initBreakPoint()

    debugger.HandleCommand('command script add -f jbt.jit_bt jbt')
    print 'The jit symbol resolver command `jbt` has been initialized and is ready for use.'


### Trouble Shooting

## slow method of determining instruction_start() -- uncomment to check against calculated one
# inst_start_var = frame.EvaluateExpression('reinterpret_cast<uint64_t>(code->instruction_start())');
# inst_start_old = int(value(inst_start_var).value, 10)
