## Status

Trying to get `code->instruction_start()` address without evaluating expression since that turned out to be very slow.

```
(lldb) start: (56565112528992 :: 337217706060) code: (v8::internal::Code *) code = 0x0000337217706001
Process 26677 stopped
* thread #1: tid = 0x21984, 0x00000001005f48c4 node_g`v8::internal::PerfBasicLogger::LogRecordedBuffer(this=0x0000000101c01fe0, code=0x0000337217706001, (null)=0x0000000000000000, name=0x0000000101c02004, length=15) + 36 at log.cc:285, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
    frame #0: 0x00000001005f48c4 node_g`v8::internal::PerfBasicLogger::LogRecordedBuffer(this=0x0000000101c01fe0, code=0x0000337217706001, (null)=0x0000000000000000, name=0x0000000101c02004, length=15) + 36 at log.cc:285
   282                                         SharedFunctionInfo*,
   283                                         const char* name,
   284                                         int length) {
-> 285    DCHECK(code->instruction_start() == code->address() + Code::kHeaderSize);
   286
   287    fprintf(stderr, "%d", v8::internal::Code::kHeaderSize);
   288    base::OS::FPrint(perf_output_handle_, "%llx %x %.*s\n",
(lldb) script
Python Interactive Interpreter. To exit, type 'quit()', 'exit()' or Ctrl-D.
>>> code_var = lldb.frame.FindVariable('code')
>>> code_var
<lldb.SBValue; proxy of <Swig Object of type 'lldb::SBValue *' at 0x1098c33f0> >
```
